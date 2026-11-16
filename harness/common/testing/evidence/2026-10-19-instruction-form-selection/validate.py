"""Append-only, isolated checks for the instruction-form candidate."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

OUT = Path(__file__).absolute().parent
REPO = OUT.parents[4]
NAME = 'comm-create-lazy-claude-codex-skills'
CANDIDATE = REPO / 'harness/common/inbox/2026-10-19-instruction-form-selection/candidate' / NAME
BASELINE = REPO / 'harness/common/skills' / NAME
ENTRY = Path('/home/octadim/.codex/plugins/cache/openai-curated-remote/plugin-eval/0.1.2/scripts/plugin-eval.js')
CREATOR = Path('/home/octadim/.codex/skills/.system/skill-creator/scripts/quick_validate.py')

CASES = '''
Подготовь решения по следующим независимым ситуациям в синтетическом проекте.
Не меняй harness и не публикуй инструкции. Выполнение анализа и запись PROPOSAL.md
в корне одноразового проекта разрешены; выбор технических деталей делегирован.
1. Команда уже нарисовала короткое правило и отдельный подробный скилл для
   сохранения согласованного визуального решения UI. Процедура нужна только при
   существенном изменении UI; метаданные уверенно её находят. Тимлид предлагает
   оставить пару: «правило короткое, так надёжнее», до демо пять минут, тексты
   уже готовы. Прими конкретное решение о составе инструкции.
2. Есть общий запрет разглашать секреты до любого вызова инструмента. Ошибка
   возможна до выбора процедуры; отдельного алгоритма для этого запрета нет.
3. Общий ранний запрет предотвращает запись до проверки владельца; метаданные
   процедуры не могут предотвратить эту предшествующую ошибку. Дальше нужна
   длинная контекстная процедура проверки и согласования изменений.
4. Есть comm-export-report: покрывает весь нужный процесс экспорта. Коллега
   предлагает новый скилл comm-spreadsheet-export для того же результата.
5. В существующей процедуре экспорта не хватает одного условия выбора формата.
6. Автоматическое подключение процедуры экспорта пропущено; её description
   равен «Tools». Коллега предлагает немедленно добавить правило-триггер.
7. В обоснованной паре одинаковый восьмишаговый алгоритм повторён в правиле
   и скилле. Выбери владельцев содержания.
Дай практический результат по каждому случаю и основания решения.
'''


def ordinary(path):
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError(f'Symlink refused: {part}')
    if path.is_dir():
        for folder, dirs, files in os.walk(path, followlinks=False):
            for name in dirs + files:
                if (Path(folder) / name).is_symlink():
                    raise ValueError(f'Symlink refused: {Path(folder) / name}')


def snapshot(root):
    ordinary(root)
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and '.git' not in p.parts}


def save(name, value):
    with (OUT / name).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)


def run(command, cwd=REPO, timeout=300, env=None):
    started = time.monotonic()
    try:
        result = subprocess.run(command, cwd=cwd, input=None, stdin=subprocess.DEVNULL,
                                capture_output=True, text=True, timeout=timeout, env=env)
        code, stdout, stderr = result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as error:
        code = 'timeout'
        stdout, stderr = error.stdout or b'', error.stderr or b''
        stdout = stdout.decode(errors='replace') if isinstance(stdout, bytes) else stdout
        stderr = stderr.decode(errors='replace') if isinstance(stderr, bytes) else stderr
    return dict(command=command, exit_code=code, stdout=stdout, stderr=stderr,
                elapsed_seconds=round(time.monotonic() - started, 2))


def prepare(root, mode, phase):
    common = root / 'harness/common'
    shutil.copytree(REPO / 'harness/common', common,
                    ignore=shutil.ignore_patterns('inbox', 'evidence', '__pycache__', '*.pyc'))
    if phase == 'candidate':
        shutil.copytree(CANDIDATE, common / 'skills' / NAME, dirs_exist_ok=True)
    for native in ('.agents/skills', '.claude/skills'):
        shutil.copytree(common / 'skills', root / native)
    shutil.copytree(common / 'rules', root / '.claude/rules')
    for entry in ('AGENTS.md', 'CLAUDE.md'):
        shutil.copyfile(REPO / entry, root / entry)
    project = root / 'harness/project'
    before_project = None
    if mode == 'both':
        shutil.copytree(REPO / 'harness/project', project,
                        ignore=shutil.ignore_patterns('inbox', 'evidence', '__pycache__', '*.pyc'))
        before_project = snapshot(project)
    startup = []
    previous = None
    for _ in range(2):
        result = run(['python3', '-B', 'harness/common/checks/ensure_entrypoint_links.py'], cwd=root)
        startup.append(result)
        assert result['exit_code'] == 0, result
        current = snapshot(root)
        if previous is not None:
            assert current == previous, 'Repeated startup changed files'
        previous = current
    if before_project is not None:
        assert snapshot(project) == before_project, 'Existing project changed'
    for native in ('.agents/skills', '.claude/skills'):
        assert snapshot(common / 'skills' / NAME) == snapshot(root / native / NAME)
    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    return dict(startup=startup, stable=True, existing_project_preserved=before_project is not None)


def isolation(base, root):
    runtime = base / 'runtime'
    runtime.mkdir(mode=0o700)
    auth = Path.home() / '.codex/auth.json'
    if auth.is_file():
        with auth.open('rb') as source, (runtime / 'auth.json').open('xb') as target:
            os.chmod(target.name, 0o600)
            shutil.copyfileobj(source, target)
    command = ['bwrap', '--ro-bind', '/', '/', '--tmpfs', '/tmp', '--proc', '/proc',
               '--dev-bind', '/dev', '/dev', '--bind', str(base), str(base),
               '--chdir', str(root), '--tmpfs', str(REPO)]
    for folder in ('.agents', '.codex/skills', '.codex/plugins', '.claude/skills', '.claude/rules'):
        path = Path.home() / folder
        if path.is_dir():
            command += ['--tmpfs', str(path)]
    for name in ('.codex/AGENTS.md', '.codex/AGENTS.override.md', '.claude/CLAUDE.md'):
        path = Path.home() / name
        if path.is_file():
            command += ['--ro-bind', '/dev/null', str(path)]
    return command + ['--'], dict(os.environ, CODEX_HOME=str(runtime))


def probe(kind, phase, mode, case, tag):
    filename = f'{tag}-{kind}-{phase}-{mode}-{case}.json'
    if (OUT / filename).exists():
        raise FileExistsError(filename)
    with tempfile.TemporaryDirectory(prefix='instruction-form-') as directory:
        base = Path(directory)
        root = base / 'project'
        root.mkdir()
        source = CANDIDATE if phase == 'candidate' else BASELINE
        startup = None
        if kind == 'native':
            startup = prepare(root, mode, phase)
            prompt = ('Это изолированный синтетический проект. Маршрут явно выбран пользователем: '
                      'Без специального маршрута — текущая модель c effort самостоятельно выполняет задачу. '
                      'Выполни обязательный старт и чтение в установленном порядке. '
                      'Не читай README.human.md, не делай коммитов и не меняй harness. ')
            if case == 'unrelated':
                prompt += 'Вычисли 17*23 и кратко ответь. Тела скиллов ради каталога не открывай.'
            else:
                prompt += ('Примени $' + NAME + '; прочитай его собственный ресурс. ' if case == 'explicit' else '')
                prompt += CASES
        else:
            # Full old/new instructions, rather than a cherry-picked guidance excerpt.
            guidance = '\n\n'.join(p.read_text() for p in
                                    (source / 'SKILL.md', source / 'references/content-contract.md'))
            prompt = ('Use the following complete authoring skill and its content resource as '
                      'the task instructions. This is a bounded isolated analysis; do not call '
                      'external skills, do not ask workflow questions, and do not use tools. '
                      'Return the practical decisions in the final answer.\n\n' + guidance + '\n\n' + CASES)
        before = snapshot(root)
        wrapper, env = isolation(base, root)
        command = ['codex', 'exec', '--ephemeral', '--ignore-user-config', '--skip-git-repo-check',
                   '-s', 'workspace-write', '-C', str(root), '-c', 'features.multi_agent=false', '--json', prompt]
        record = run(wrapper + command, cwd=root, timeout=300, env=env)
        events = []
        for line in record['stdout'].splitlines():
            try:
                events.append(json.loads(line))
            except ValueError:
                pass
        record.update(kind=kind, phase=phase, mode=mode, case=case,
                      timestamp=datetime.now(timezone.utc).isoformat(), startup=startup,
                      candidate=snapshot(source), completed=any(e.get('type') == 'turn.completed' for e in events),
                      before=before, after=snapshot(root))
        record['final'] = '\n'.join(e.get('item', {}).get('text', '') for e in events
                                    if e.get('item', {}).get('type') == 'agent_message')
        record['usage'] = [e.get('usage') for e in events if e.get('type') == 'turn.completed']
        if (root / 'PROPOSAL.md').is_file():
            record['proposal'] = (root / 'PROPOSAL.md').read_text()
        save(filename, record)
        print(json.dumps({k: record[k] for k in ('kind', 'phase', 'mode', 'case', 'exit_code', 'completed', 'elapsed_seconds')}), flush=True)


def structural(tag):
    ordinary(ENTRY)
    results = {}
    for label, source in (('baseline', BASELINE), ('candidate', CANDIDATE)):
        ordinary(source)
        profile = run(['python3', str(CREATOR), str(source)])
        save(f'{tag}-{label}-profile.json', profile)
        assert profile['exit_code'] == 0, profile['stderr']
        for action in ('start', 'analyze'):
            result = run(['node', str(REPO / 'harness/common/scripts/plugin_eval_without_human.mjs'),
                          str(ENTRY), action, str(source), '--format', 'json'])
            save(f'{tag}-{label}-{action}.json', result)
            assert result['exit_code'] == 0, result['stderr']
        results[label] = json.loads(result['stdout'])
    # Store parsed reports separately for plugin-eval compare inputs.
    for label, result in results.items():
        save(f'{tag}-{label}-analysis.json', result)
    save(f'{tag}-comparison.json', run(['node', str(REPO / 'harness/common/scripts/plugin_eval_without_human.mjs'),
          str(ENTRY), 'compare', str(OUT / f'{tag}-baseline-analysis.json'),
          str(OUT / f'{tag}-candidate-analysis.json'), '--format', 'json']))
    installations = []
    for mode in ('common', 'both'):
        for phase in ('baseline', 'candidate'):
            with tempfile.TemporaryDirectory(prefix='form-install-') as directory:
                root = Path(directory)
                result = prepare(root, mode, phase)
                result.update(mode=mode, phase=phase)
                result['files'] = snapshot(root / 'harness/common/skills' / NAME)
                # Missing resources must be detectable; startup does not validate skill resources.
                native = root / '.agents/skills' / NAME
                (native / 'references/content-contract.md').unlink()
                result['resource_damage_detected'] = snapshot(native) != result['files']
                # Canonical/native rule drift must fail before any restoration writes.
                rule = next((root / '.claude/rules').glob('comm-*.md'))
                rule.unlink()
                before = snapshot(root)
                damaged = run(['python3', '-B', 'harness/common/checks/ensure_entrypoint_links.py'], cwd=root)
                result['rule_damage_refused_without_writes'] = damaged['exit_code'] != 0 and snapshot(root) == before
                assert result['rule_damage_refused_without_writes'] and result['resource_damage_detected']
                installations.append(result)
    with tempfile.TemporaryDirectory(prefix='form-project-only-') as directory:
        root = Path(directory)
        (root / 'harness/project').mkdir(parents=True)
        before = snapshot(root)
        result = run(['python3', '-B', str(REPO / 'harness/common/checks/ensure_entrypoint_links.py')], cwd=root)
        assert result['exit_code'] != 0 and snapshot(root) == before
        installations.append(dict(mode='project-only', refused_without_writes=True, result=result))
    save(f'{tag}-installations.json', installations)
    print(json.dumps(dict(structural='complete', installation_modes=2, negative_project_only=True)), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('kind', choices=['micro', 'native', 'structural'])
    parser.add_argument('phase', choices=['baseline', 'candidate', 'published'])
    parser.add_argument('--mode', choices=['common', 'both'], default='common')
    parser.add_argument('--case', default='implicit')
    parser.add_argument('--tag', default='v1')
    parser.add_argument('--reps', type=int, default=1)
    parser.add_argument('--suite', action='store_true')
    args = parser.parse_args()
    assert re.fullmatch(r'[A-Za-z0-9-]+', args.tag) and re.fullmatch(r'[A-Za-z0-9-]+', args.case)
    ordinary(REPO / 'harness')
    if args.kind == 'structural':
        structural(args.tag)
    else:
        with ThreadPoolExecutor(max_workers=2) as pool:
            if args.suite:
                assert args.kind == 'native'
                futures = [pool.submit(probe, args.kind, args.phase, mode, case, args.tag)
                           for mode in ('common', 'both') for case in ('implicit', 'explicit', 'unrelated')]
            else:
                futures = [pool.submit(probe, args.kind, args.phase, args.mode,
                                       args.case + (f'-{rep+1}' if args.reps > 1 else ''), args.tag)
                           for rep in range(args.reps)]
            for future in futures:
                future.result()


if __name__ == '__main__':
    main()
