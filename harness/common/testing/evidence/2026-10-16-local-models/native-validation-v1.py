"""Run bounded native Codex checks in disposable, isolated harness installations."""
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
OUT = Path(__file__).absolute().parent
NAME = 'comm-manage-local-models'
CANDIDATE = REPO / 'harness/common/inbox/2026-10-16-local-models/candidate' / NAME


def ordinary(path):
    for component in (path, *path.parents):
        if component.is_symlink():
            raise ValueError(f'Symlink refused: {component}')
    if path.is_dir():
        for directory, folders, files in os.walk(path, followlinks=False):
            for name in folders + files:
                child = Path(directory) / name
                if child.is_symlink():
                    raise ValueError(f'Symlink refused: {child}')


def state(root):
    ordinary(root)
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and '.git' not in p.parts}


def prepare(root, mode, baseline):
    ordinary(REPO / 'harness')
    common = root / 'harness/common'
    shutil.copytree(REPO / 'harness/common', common,
                    ignore=shutil.ignore_patterns('inbox', 'evidence', '__pycache__', '*.pyc'))
    if not baseline:
        ordinary(CANDIDATE)
        shutil.copytree(CANDIDATE, common / 'skills' / NAME)
    for native in ('.agents/skills', '.claude/skills'):
        shutil.copytree(common / 'skills', root / native)
    shutil.copytree(common / 'rules', root / '.claude/rules')
    for entry in ('AGENTS.md', 'CLAUDE.md'):
        shutil.copyfile(REPO / entry, root / entry)
    project = root / 'harness/project'
    original = None
    if mode == 'both':
        project.mkdir()
        for name, body in {
            'START.md': '# Existing neutral project\n',
            'INDEX.md': '# Existing project map\n',
            'sentinel.txt': 'Preserve this existing project byte for byte.\n',
            'README.human.md': '# Existing project\n\nExample: retain sentinel.txt.\n',
        }.items():
            (project / name).write_text(body)
        original = state(project)
    runs = []
    first = None
    for _ in range(2):
        r = subprocess.run(['python3', '-B', 'harness/common/checks/ensure_entrypoint_links.py'],
                           cwd=root, capture_output=True, text=True)
        runs.append({'code': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr})
        if r.returncode:
            raise RuntimeError(runs)
        current = state(root)
        if first is None:
            first = current
        else:
            assert current == first, 'Repeated startup changed files'
    if original is not None:
        assert state(project) == original, 'Existing project changed'
    (root / 'LAUNCH.md').write_text(
        'A neutral Python service uses generation, embedding and OCR models.\n'
        'Dependencies are locked with uv. Downloaded weights currently live in .venv/models/.\n'
        'The service launcher obtains model paths from ignored config/service.local.toml.\n'
        'There is no model manifest or model-preparation command yet.\n'
        'An operator wants project-root rag/local_models/ to survive venv recreation.\n'
        'The model registry, exact revisions and trusted checksums have not been provided.\n'
        'The future embedding replacement may retain the same vector dimension.\n'
        'There is no permission to access production, reindex data or download files.\n')
    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    return runs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('common', 'both'))
    parser.add_argument('case', choices=('implicit', 'explicit', 'unrelated'))
    parser.add_argument('--baseline', action='store_true')
    parser.add_argument('--tag', default='v1')
    args = parser.parse_args()
    phase = 'baseline' if args.baseline else 'candidate'
    output = OUT / f'native-codex-{args.mode}-{phase}-{args.case}-{args.tag}.json'
    if output.exists():
        raise FileExistsError(output)
    scenarios = json.loads((OUT / 'scenarios.json').read_text())
    with tempfile.TemporaryDirectory(prefix='local-models-native-') as directory:
        base = Path(directory)
        root = base / 'project'
        root.mkdir()
        startup = prepare(root, args.mode, args.baseline)
        runtime = base / 'runtime'
        runtime.mkdir(mode=0o700)
        auth = Path.home() / '.codex/auth.json'
        if auth.is_file():
            with auth.open('rb') as source, (runtime / 'auth.json').open('xb') as target:
                os.chmod(target.name, 0o600)
                shutil.copyfileobj(source, target)
        before = state(root)
        prompt = ('Это изолированный синтетический проект. Выполни обязательный старт '
                  'и чтение в установленном порядке. README.human.md не читай. '
                  'Не делай коммитов и не меняй harness. Назови релевантные скиллы '
                  'из нативного каталога, если он предоставлен; не читай тела ради перечисления. '
                  + scenarios[args.case])
        isolation = ['bwrap', '--ro-bind', '/', '/', '--tmpfs', '/tmp', '--proc', '/proc',
                     '--dev-bind', '/dev', '/dev', '--bind', str(base), str(base),
                     '--chdir', str(root), '--tmpfs', str(REPO)]
        for p in (Path.home()/'.agents', Path.home()/'.codex/skills',
                  Path.home()/'.codex/plugins', Path.home()/'.claude/skills', Path.home()/'.claude/rules'):
            if p.is_dir():
                isolation += ['--tmpfs', str(p)]
        for p in (Path.home()/'.codex/AGENTS.md', Path.home()/'.codex/AGENTS.override.md',
                  Path.home()/'.claude/CLAUDE.md'):
            if p.is_file():
                isolation += ['--ro-bind', '/dev/null', str(p)]
        command = ['codex', 'exec', '--ephemeral', '--ignore-user-config',
                   '--skip-git-repo-check', '-s', 'workspace-write', '-C', str(root),
                   '-c', 'features.multi_agent=false', '--json', prompt]
        started = time.monotonic()
        try:
            r = subprocess.run(isolation + ['--'] + command,
                               env=dict(os.environ, CODEX_HOME=str(runtime)),
                               stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=240)
            code, stdout, stderr = r.returncode, r.stdout, r.stderr
        except subprocess.TimeoutExpired as exc:
            code = 'timeout'
            stdout = exc.stdout or b''
            stderr = exc.stderr or b''
            if isinstance(stdout, bytes): stdout = stdout.decode(errors='replace')
            if isinstance(stderr, bytes): stderr = stderr.decode(errors='replace')
        events = []
        for line in stdout.splitlines():
            try:
                events.append(json.loads(line))
            except ValueError:
                pass
        after = state(root)
        changed = sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))
        result = {'mode': args.mode, 'case': args.case, 'phase': phase,
                  'command': command, 'isolation': isolation, 'exit_code': code,
                  'stdout': stdout, 'stderr': stderr,
                  'completed': any(e.get('type') == 'turn.completed' for e in events),
                  'elapsed_seconds': round(time.monotonic()-started, 2),
                  'startup': startup, 'before': before, 'after': after, 'changed_files': changed}
        with output.open('x') as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
        print(json.dumps({k: result[k] for k in
                          ('mode', 'case', 'phase', 'exit_code', 'completed', 'elapsed_seconds', 'changed_files')}),
              flush=True)


if __name__ == '__main__':
    main()
