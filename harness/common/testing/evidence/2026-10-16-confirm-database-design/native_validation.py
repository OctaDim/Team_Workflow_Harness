"""Disposable native probes. Raw JSON is append-only; never edits installed sources."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

EVIDENCE = Path(__file__).absolute().parent
REPO = EVIDENCE.parents[4]
REQUEST = REPO / 'harness/common/inbox/2026-10-16-confirm-database-design'
NAME = 'comm-confirm-database-design'


def ordinary(path):
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError(f'Symlink: {part}')
    if path.is_dir():
        for folder, dirs, files in os.walk(path, followlinks=False):
            for name in dirs + files:
                if (Path(folder) / name).is_symlink():
                    raise ValueError(f'Symlink: {Path(folder) / name}')


def snapshot(root):
    ordinary(root)
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)


def prepare(root, mode, phase):
    common = root / 'harness/common'
    shutil.copytree(REPO / 'harness/common', common,
                    ignore=shutil.ignore_patterns('inbox', 'evidence', '__pycache__', '*.pyc'))
    if phase != 'baseline':
        shutil.copytree(REQUEST / NAME, common / 'skills' / NAME)
        shutil.copyfile(REQUEST / f'{NAME}.md', common / 'rules' / f'{NAME}.md')
    for dest in ('.agents/skills', '.claude/skills'):
        shutil.copytree(common / 'skills', root / dest)
    shutil.copytree(common / 'rules', root / '.claude/rules')
    for entry in ('AGENTS.md', 'CLAUDE.md'):
        shutil.copyfile(REPO / entry, root / entry)
    if mode == 'both':
        project = root / 'harness/project'
        project.mkdir()
        for entry in ('START.md', 'INDEX.md'):
            (project / entry).write_text('# Existing neutral project\n', encoding='utf-8')
        (project / 'README.human.md').write_text('# Existing test project\n\nExample: sentinel must survive startup.\n')
        (project / 'sentinel').write_text('Preserve existing project byte-for-byte\n')
    before_project = snapshot(root / 'harness/project') if mode == 'both' else None
    starts = []
    for _ in range(2):
        result = subprocess.run(['python3', '-B', 'harness/common/checks/ensure_entrypoint_links.py'],
                                cwd=root, text=True, capture_output=True)
        starts.append(dict(code=result.returncode, stdout=result.stdout, stderr=result.stderr))
        if result.returncode:
            raise RuntimeError(starts)
    if before_project is not None:
        assert snapshot(root / 'harness/project') == before_project
    (root / 'context.md').write_text(
        'Тестовый Python-проект, SQLite, существующих данных нет. Модели, миграции и слой доступа ещё не созданы. '
        'Один процесс, синхронные задачи. Архитектурных согласований пока нет. Реальной БД нет.\n', encoding='utf-8')
    return starts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('agent', choices=['codex', 'claude'])
    parser.add_argument('mode', choices=['common', 'both'])
    parser.add_argument('phase', choices=['baseline', 'candidate'])
    parser.add_argument('case')
    parser.add_argument('tag')
    args = parser.parse_args()
    if (EVIDENCE / f'{args.tag}-superseded.json').exists():
        print(json.dumps(dict(agent=args.agent, mode=args.mode, case=args.case,
                              status=f'not run: superseded candidate {args.tag}')))
        return
    ordinary(REPO / 'harness')
    scenarios = json.loads((EVIDENCE / 'scenarios.json').read_text())
    output = EVIDENCE / f'native-{args.agent}-{args.mode}-{args.phase}-{args.case}-{args.tag}.json'
    if output.exists():
        raise FileExistsError(output)
    with tempfile.TemporaryDirectory(prefix='database-design-native-') as directory:
        root = Path(directory)
        startup = prepare(root, args.mode, args.phase)
        before = snapshot(root)
        prompt = ('Это отдельная синтетическая задача в одноразовом проекте. '
                  'Маршрут уже явно выбран пользователем: Без специального маршрута — текущая модель c effort самостоятельно выполняет задачу. '
                  'Сначала выполни обязательный старт и прочитай стартовые инструкции в установленном порядке. '
                  'README.human.md не читай. Затем выполни задачу: ' + scenarios[args.case]['prompt'])
        isolation = ['bwrap', '--ro-bind', '/', '/', '--tmpfs', '/tmp', '--proc', '/proc',
                     '--dev-bind', '/dev', '/dev', '--bind', str(root), str(root),
                     '--chdir', str(root), '--tmpfs', str(REPO)]
        config = Path.home() / ('.codex' if args.agent == 'codex' else '.claude')
        isolation += ['--bind', str(config), str(config)]
        for directory in (Path.home() / '.agents', Path.home() / '.codex/skills',
                          Path.home() / '.codex/plugins', Path.home() / '.claude/skills',
                          Path.home() / '.claude/rules'):
            if directory.is_dir():
                isolation += ['--tmpfs', str(directory)]
        for path in (Path.home() / '.codex/AGENTS.md', Path.home() / '.codex/AGENTS.override.md',
                     Path.home() / '.claude/CLAUDE.md'):
            if path.is_file():
                isolation += ['--ro-bind', '/dev/null', str(path)]
        if args.agent == 'codex':
            command = ['codex', 'exec', '--ephemeral', '--skip-git-repo-check', '-s', 'workspace-write',
                       '-C', str(root), '-c', 'features.multi_agent=false', '--json', prompt]
        else:
            command = ['claude', '-p', '--no-session-persistence', '--output-format', 'stream-json',
                       '--verbose', '--setting-sources', 'project', '--strict-mcp-config',
                       '--mcp-config', '{"mcpServers":{}}', '--permission-mode', 'dontAsk',
                       '--tools', 'Read,Glob,Grep,Bash,Skill,Write,Edit',
                       '--allowedTools', 'Read,Glob,Grep,Bash,Skill,Write,Edit', '--', prompt]
        started = time.monotonic()
        try:
            result = subprocess.run(isolation + ['--'] + command, stdin=subprocess.DEVNULL,
                                    capture_output=True, text=True, timeout=240)
            stdout, stderr, code = result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else exc.stdout or ''
            stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else exc.stderr or ''
            code = 'timeout'
        events = []
        for line in stdout.splitlines():
            try:
                events.append(json.loads(line))
            except ValueError:
                pass
        completed = any(e.get('type') == 'turn.completed' for e in events) if args.agent == 'codex' else any(
            e.get('type') == 'result' and not e.get('is_error', True) for e in events)
        after = snapshot(root)
        changed = [p for p in before.keys() | after.keys() if before.get(p) != after.get(p)]
        record = dict(agent=args.agent, mode=args.mode, phase=args.phase, case=args.case,
                      command=command, isolation=isolation, exit_code=code, completed=completed,
                      elapsed_seconds=round(time.monotonic()-started, 2), stdout=stdout, stderr=stderr,
                      startup=startup, before=before, after=after, changed_files=sorted(changed),
                      changed_text={p:(root/p).read_text(errors='replace') for p in changed
                                    if (root/p).is_file() and (root/p).stat().st_size < 20000
                                    and Path(p).name != 'README.human.md'})
        save(output, record)
        print(json.dumps({k: record[k] for k in ('agent','mode','phase','case','exit_code','completed','elapsed_seconds')}))


if __name__ == '__main__':
    main()
