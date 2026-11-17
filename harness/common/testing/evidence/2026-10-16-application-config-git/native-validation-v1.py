"""Isolated synthetic config checks; never edits the real project's index/configs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

REPO = Path(__file__).absolute().parents[5]
EVIDENCE = Path(__file__).absolute().parent
CANDIDATE = REPO / 'harness/common/inbox/2026-10-16-application-config-git/candidate'
NAME = 'comm-separate-application-config'
RULE = 'comm-application-config-git.md'


def ordinary(path):
    for component in (path, *path.parents):
        if component.is_symlink():
            raise ValueError(f'Symlink: {component}')
    if path.is_dir():
        for folder, dirs, files in os.walk(path, followlinks=False):
            for name in dirs + files:
                if (Path(folder) / name).is_symlink():
                    raise ValueError(f'Symlink: {Path(folder) / name}')


def state(root):
    ordinary(root)
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts}


def git(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True, check=True)


def prepare(root, mode, baseline):
    common = root / 'harness/common'
    shutil.copytree(REPO / 'harness/common', common,
                    ignore=shutil.ignore_patterns('inbox', 'evidence', '__pycache__', '*.pyc', '.pytest_cache'))
    if not baseline:
        shutil.copytree(CANDIDATE / 'skills' / NAME, common / 'skills' / NAME)
        shutil.copyfile(CANDIDATE / 'rules' / RULE, common / 'rules' / RULE)
    for target in ('.agents/skills', '.claude/skills'):
        shutil.copytree(common / 'skills', root / target)
    shutil.copytree(common / 'rules', root / '.claude/rules')
    for entry in ('AGENTS.md', 'CLAUDE.md'):
        shutil.copyfile(REPO / entry, root / entry)
    project = root / 'harness/project'
    previous_project = None
    if mode == 'both':
        project.mkdir()
        (project / 'START.md').write_text('# Synthetic existing project\n')
        (project / 'INDEX.md').write_text('# Synthetic existing project map\n')
        (project / 'README.human.md').write_text('# Human guide\n\nExample: preserve the sentinel.\n')
        (project / 'sentinel.txt').write_text('Must survive startup unchanged.\n')
        previous_project = state(project)
    startup = []
    for index in range(2):
        r = subprocess.run(['python3', '-B', 'harness/common/checks/ensure_entrypoint_links.py'],
                           cwd=root, capture_output=True, text=True)
        startup.append({'exit_code': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr})
        if r.returncode:
            raise RuntimeError(startup)
        if index == 0:
            first_state = state(root)
    assert first_state == state(root), 'Repeated startup changed files'
    if previous_project is not None:
        assert previous_project == state(project), 'Existing project changed'
    git(root, 'init', '-q')
    contents = {
        'backend/config/app.local.toml': '[database]\npassword = "SYNTHETIC_CONFIG_SECRET_7319"\n',
        'backend/config/limits.toml': '[limits]\nfile_bytes = 50000000\n',
        'frontend/config/app.local.toml': '[api]\norigin = "http://example.invalid:8000"\n',
        'frontend/index.html': '<html><body>Synthetic static fixture</body></html>\n',
        'unrelated.txt': 'User-owned staged content; preserve unchanged.\n',
        '.gitignore': '__pycache__/\n',
    }
    for name, content in contents.items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    git(root, 'add', '--', *contents)
    # Seed the trap: the backend local file is already tracked despite its ignore entry.
    (root / '.gitignore').write_text('__pycache__/\n/backend/config/app.local.toml\n')
    git(root, 'add', '--', '.gitignore')
    return startup


PROMPTS = {
    'implicit': (
        'Подготовь конфиги синтетического приложения к хранению в Git. '
        'Используй app.example.toml для шаблонов, app.local.toml для параметров установки '
        'в обоих разделах backend/config и frontend/config. Общие лимиты должны оставаться '
        'версионируемыми. Разрешены изменения только файлов конфигурации этих двух разделов '
        'и корневого .gitignore; разрешено удалить только backend/config/app.local.toml и '
        'frontend/config/app.local.toml из индекса с сохранением рабочих файлов. '
        'Не делай коммитов, не переписывай историю и не меняй unrelated.txt. '
        'Проверь полученный результат и объясни его без раскрытия значений секретов.'),
    'explicit': (
        'Применяй $comm-separate-application-config. Подготовь конфиги синтетического '
        'приложения к Git с app.example.toml и app.local.toml в backend/config и frontend/config. '
        'Сохрани общие лимиты и локальные рабочие файлы. Разрешено изменять только эти '
        'конфиги и .gitignore, а из индекса удалять только оба app.local.toml. '
        'Не делай коммитов, не переписывай историю, не меняй unrelated.txt. '
        'Проверь результат и объясни его без раскрытия значений секретов.'),
    'unrelated': 'Ответь на 37 * 4. Работа с файлами приложения не поручена.',
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('common', 'both'))
    parser.add_argument('case', choices=PROMPTS)
    parser.add_argument('--baseline', action='store_true')
    parser.add_argument('--tag', default='v1')
    args = parser.parse_args()
    phase = 'baseline' if args.baseline else 'candidate'
    output = EVIDENCE / f'native-codex-{args.mode}-{phase}-{args.case}-{args.tag}.json'
    if output.exists():
        raise FileExistsError(output)
    ordinary(REPO / 'harness')
    with tempfile.TemporaryDirectory(prefix='application-config-native-') as directory:
        root = Path(directory)
        startup = prepare(root, args.mode, args.baseline)
        before = state(root)
        index_before = git(root, 'ls-files', '--stage', '--', 'unrelated.txt').stdout
        prompt = (
            'Это отдельный синтетический проект. Маршрут уже выбран: без специального '
            'маршрута, текущая модель выполняет задачу самостоятельно. Субагентов не запускай. '
            'Выполни обязательный старт и прочитай инструкции в установленном порядке. '
            'README.human.md не читай. Перед задачей назови релевантные скиллы из нативного '
            'каталога, если он предоставлен; не читай файлы ради перечисления. '
            + PROMPTS[args.case])
        isolation = ['bwrap', '--ro-bind', '/', '/', '--tmpfs', '/tmp', '--proc', '/proc',
                     '--dev-bind', '/dev', '/dev', '--bind', str(root), str(root),
                     '--chdir', str(root), '--tmpfs', str(REPO)]
        config = Path.home() / '.codex'
        isolation += ['--bind', str(config), str(config)]
        for folder in (Path.home() / '.agents', Path.home() / '.codex/skills',
                       Path.home() / '.codex/plugins', Path.home() / '.claude/skills',
                       Path.home() / '.claude/rules'):
            if folder.is_dir():
                isolation += ['--tmpfs', str(folder)]
        for path in (Path.home() / '.codex/AGENTS.md', Path.home() / '.codex/AGENTS.override.md',
                     Path.home() / '.claude/CLAUDE.md'):
            if path.is_file():
                isolation += ['--ro-bind', '/dev/null', str(path)]
        command = ['codex', 'exec', '--ephemeral', '--ignore-user-config', '--skip-git-repo-check',
                   '-s', 'workspace-write', '-C', str(root), '-c', 'features.multi_agent=false',
                   '--json', prompt]
        started = time.monotonic()
        try:
            r = subprocess.run(isolation + ['--'] + command, stdin=subprocess.DEVNULL,
                               capture_output=True, text=True, timeout=240)
            stdout, stderr, code = r.stdout, r.stderr, r.returncode
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
        after = state(root)
        changed = sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))
        record = {'mode': args.mode, 'case': args.case, 'phase': phase,
                  'command': command, 'isolation': isolation, 'exit_code': code,
                  'completed': any(e.get('type') == 'turn.completed' for e in events),
                  'elapsed_seconds': round(time.monotonic() - started, 2),
                  'stdout': stdout, 'stderr': stderr, 'startup': startup,
                  'before': before, 'after': after, 'changed_files': changed,
                  'unrelated_index_preserved': index_before == git(root, 'ls-files', '--stage', '--', 'unrelated.txt').stdout,
                  'index_paths': git(root, 'ls-files').stdout.splitlines(),
                  'working_local_files_preserved': all(before.get(p) == after.get(p) for p in
                     ('backend/config/app.local.toml', 'frontend/config/app.local.toml')),
                  'changed_text': {p: (root / p).read_text(errors='replace') for p in changed
                                   if (root / p).is_file() and Path(p).name != 'README.human.md'
                                   and (root / p).stat().st_size < 20000}}
        with output.open('x') as stream:
            json.dump(record, stream, ensure_ascii=False, indent=2)
        print(json.dumps({key: record[key] for key in
                         ('mode', 'case', 'phase', 'exit_code', 'completed', 'elapsed_seconds', 'changed_files')}), flush=True)


if __name__ == '__main__':
    main()
