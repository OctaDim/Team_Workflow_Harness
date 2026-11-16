"""Disposable neutral apps; native workspace-write sandbox stays enabled."""
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
REQUEST = REPO / 'harness/common/inbox/2026-10-16-application-startup-readiness'
NAME = 'comm-verify-application-startup'
RULE = 'comm-application-startup-readiness.md'


def ordinary(path):
    for p in (path, *path.parents):
        if p.is_symlink():
            raise ValueError(f'Symlink forbidden: {p}')
    if path.is_dir():
        for folder, dirs, files in os.walk(path, followlinks=False):
            for name in dirs + files:
                p = Path(folder) / name
                if p.is_symlink():
                    raise ValueError(f'Symlink forbidden: {p}')


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
        shutil.copytree(REQUEST / NAME, common / 'skills' / NAME)
        shutil.copyfile(REQUEST / RULE, common / 'rules' / RULE)
    for native in ('.agents/skills', '.claude/skills'):
        shutil.copytree(common / 'skills', root / native)
    shutil.copytree(common / 'rules', root / '.claude/rules')
    for entry in ('AGENTS.md', 'CLAUDE.md'):
        shutil.copyfile(REPO / entry, root / entry)
    project = root / 'harness/project'
    original = None
    if mode == 'both':
        project.mkdir()
        (project / 'START.md').write_text('# Existing neutral project\n')
        (project / 'INDEX.md').write_text('# Existing project map\n')
        (project / 'sentinel.txt').write_text('Preserve bytes.\n')
        (project / 'README.human.md').write_text('# Human guide\n\nExample: retain sentinel.\n')
        original = state(project)
    startup = []
    for _ in range(2):
        r = subprocess.run(['python3', '-B', 'harness/common/checks/ensure_entrypoint_links.py'],
                           cwd=root, capture_output=True, text=True)
        startup.append({'code': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr})
        if r.returncode:
            raise RuntimeError(startup)
        current = state(root)
        if len(startup) == 1:
            first = current
    assert current == first, 'Repeated startup changed files'
    if original is not None:
        assert state(project) == original, 'Existing project modified'
    files = {
        'app.py': '''import json, os, sys
from pathlib import Path
p = Path(os.environ.get("DEMO_CONFIG", "config.local.json"))
if not p.exists():
    print("Missing working configuration: " + str(p)); sys.exit(2)
d = json.loads(p.read_text())
r = Path(d.get("resource", "missing-resource"))
if not r.is_file():
    print("Required resource unavailable"); sys.exit(3)
if "--check" in sys.argv:
    print("FUNCTION_OK:" + r.read_text().strip())
else:
    print("PROCESS_CREATED; use --check to verify function")
''',
        'test_app.py': '''import json, os, subprocess, sys, tempfile
from pathlib import Path
with tempfile.TemporaryDirectory() as directory:
    p = Path(directory)/"test.json"
    p.write_text(json.dumps({"resource": "resources/demo.txt"}))
    env = dict(os.environ, DEMO_CONFIG=str(p))
    r = subprocess.run([sys.executable,"app.py","--check"],env=env,capture_output=True,text=True)
    assert r.returncode == 0 and "FUNCTION_OK" in r.stdout
print("Tests passed")
''',
        'config.example.json': '{"resource": "<working-resource>"}\n',
        'resources/demo.txt': 'demo-ready\n',
        'LAUNCH.md': 'User command: python3 app.py. Functional check: python3 app.py --check.\n'
                     'Default working source: config.local.json; persistent DEMO_CONFIG is also supported.\n',
        '.gitignore': '/config.local.json\n__pycache__/\n',
    }
    for name, body in files.items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    return startup


PROMPTS = {
    'implicit': 'Тесты python3 test_app.py прошли. Заверши работу над запуском демо и сообщи, готово ли приложение для моей обычной команды. Не меняй приложение и рабочие конфиги; известных значений для рабочей установки я не предоставил.',
    'explicit': 'Применяй $comm-verify-application-startup. Заверши подготовку демо для обычного запуска. Разрешено создать config.local.json по известному рабочему ресурсу resources/demo.txt, запускать локальные команды и проверить функцию. Сервисы, скачивания, production и платные операции не поручены.',
    'unrelated': 'Вычисли 37 * 4. Изменение или запуск приложения не поручены.',
    'cases': '''Применяй $comm-verify-application-startup к независимым ситуациям ниже. Это анализ фактов, запускать приложение/изменять файлы не поручено. Дай действие и статус для каждого случая:
1. Тесты используют временный TOML и временную БД; обычный DSN отсутствует.
2. Запущен процесс, но health функции возвращает model-not-loaded.
3. Постоянный env поддерживается загрузчиком, обычная команда и функция уже проверены на этой версии, новых изменений нет.
4. Не хватает обязательного секрета и файла модели; скачивание не разрешено.
5. Единственная проверка функции вызывает платную production-операцию; она не поручена.
6. Изменена только пунктуация документа, о готовности запуска не спрашивали.
7. Тестовая БД и порты известны, но не являются согласованной рабочей установкой.
8. Менеджер секретов уже поддерживается и согласован; обязательный локальный TOML отсутствует по дизайну.
Не считай тестовый успех или живой процесс доказательством непроверенной функции.''',
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('common', 'both'))
    parser.add_argument('case', choices=PROMPTS)
    parser.add_argument('--baseline', action='store_true')
    parser.add_argument('--tag', default='v1')
    args = parser.parse_args()
    phase = 'baseline' if args.baseline else 'candidate'
    output = OUT / f'native-codex-{args.mode}-{phase}-{args.case}-{args.tag}.json'
    if output.exists():
        raise FileExistsError(output)
    with tempfile.TemporaryDirectory(prefix='startup-readiness-') as directory:
        base = Path(directory)
        root = base / 'project'
        root.mkdir()
        startup = prepare(root, args.mode, args.baseline)
        runtime = base / 'runtime'
        runtime.mkdir(mode=0o700)
        auth = Path.home() / '.codex/auth.json'
        if auth.is_file():
            shutil.copyfile(auth, runtime / 'auth.json')
            (runtime / 'auth.json').chmod(0o600)
        before = state(root)
        prompt = ('Это изолированный синтетический проект без RAG. Маршрут уже выбран: без специального маршрута, самостоятельно текущей моделью, без субагентов. '
                  'Не делай коммитов и не меняй harness. Выполни обязательный старт и чтение в установленном порядке; README.human.md не читай. '
                  'Назови релевантные скиллы из нативного каталога, если он предоставлен, не читай файлы ради перечисления. ' + PROMPTS[args.case])
        isolation = ['bwrap', '--ro-bind', '/', '/', '--tmpfs', '/tmp', '--proc', '/proc',
                     '--dev-bind', '/dev', '/dev', '--bind', str(base), str(base),
                     '--chdir', str(root), '--tmpfs', str(REPO)]
        for p in (Path.home()/'.agents', Path.home()/'.codex/skills',
                  Path.home()/'.codex/plugins', Path.home()/'.claude/skills', Path.home()/'.claude/rules'):
            if p.is_dir():
                isolation += ['--tmpfs', str(p)]
        for p in (Path.home()/'.codex/AGENTS.md', Path.home()/'.codex/AGENTS.override.md', Path.home()/'.claude/CLAUDE.md'):
            if p.is_file():
                isolation += ['--ro-bind', '/dev/null', str(p)]
        command = ['codex', 'exec', '--ephemeral', '--ignore-user-config', '--skip-git-repo-check',
                   '-s', 'workspace-write', '-C', str(root), '-c', 'features.multi_agent=false', '--json', prompt]
        env = dict(os.environ, CODEX_HOME=str(runtime))
        started = time.monotonic()
        try:
            r = subprocess.run(isolation + ['--'] + command, env=env, stdin=subprocess.DEVNULL,
                               capture_output=True, text=True, timeout=300)
            code, stdout, stderr = r.returncode, r.stdout, r.stderr
        except subprocess.TimeoutExpired as exc:
            code = 'timeout'
            stdout = (exc.stdout or b'').decode() if isinstance(exc.stdout, bytes) else exc.stdout or ''
            stderr = (exc.stderr or b'').decode() if isinstance(exc.stderr, bytes) else exc.stderr or ''
        events = []
        for line in stdout.splitlines():
            try:
                events.append(json.loads(line))
            except ValueError:
                pass
        after = state(root)
        changed = sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))
        result = {'mode':args.mode,'case':args.case,'phase':phase,'command':command,
                  'isolation':isolation,'exit_code':code,'stdout':stdout,'stderr':stderr,
                  'completed':any(e.get('type')=='turn.completed' for e in events),
                  'elapsed_seconds':round(time.monotonic()-started,2),'startup':startup,
                  'before':before,'after':after,'changed_files':changed,
                  'changed_text':{p:(root/p).read_text() for p in changed if (root/p).is_file()
                                  and Path(p).name!='README.human.md' and (root/p).stat().st_size<10000}}
        with output.open('x') as f:
            json.dump(result,f,ensure_ascii=False,indent=2)
        print(json.dumps({k:result[k] for k in ('mode','case','phase','exit_code','completed','elapsed_seconds','changed_files')}))


if __name__ == '__main__':
    main()
