"""Sequential, isolated observations of commit-policy discovery and real Git."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

OUT = Path(__file__).absolute().parent
REPO = OUT.parents[4]
NAME = 'comm-commit-task-stages'
RULE = 'comm-commit-result-boundaries.md'
spec = importlib.util.spec_from_file_location(
    'prior_helpers', REPO / 'harness/common/testing/evidence/2026-10-19-instruction-form-selection/validate.py')
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


def save(name, data):
    with (OUT / name).open('x', encoding='utf-8') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def git(root, *args):
    result = subprocess.run(['git', *args], cwd=root, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout.strip()


def prepare(root, mode, variant):
    helpers.ordinary(REPO / 'harness')
    shutil.copytree(REPO / 'harness/common', root / 'harness/common',
                    ignore=shutil.ignore_patterns('inbox', 'evidence', '__pycache__', '*.pyc'))
    if variant == 'lazy':
        (root / 'harness/common/rules' / RULE).unlink()
    elif variant == 'published':
        assert not (root / 'harness/common/rules' / RULE).exists(), 'Rule still installed'
    elif variant != 'pair':
        raise ValueError(variant)
    for native in ('.agents/skills', '.claude/skills'):
        shutil.copytree(root / 'harness/common/skills', root / native)
        dependency = Path('/home/octadim/.codex/plugins/cache/compound-engineering-plugin/compound-engineering/3.31.0/skills/ce-commit')
        helpers.ordinary(dependency)
        shutil.copytree(dependency, root / native / 'ce-commit')
    shutil.copytree(root / 'harness/common/rules', root / '.claude/rules')
    for name in ('AGENTS.md', 'CLAUDE.md'):
        shutil.copyfile(REPO / name, root / name)
    before_project = None
    if mode == 'both':
        shutil.copytree(REPO / 'harness/project', root / 'harness/project',
                        ignore=shutil.ignore_patterns('inbox', 'evidence', '__pycache__', '*.pyc'))
        before_project = helpers.snapshot(root / 'harness/project')
    startup = []
    previous = None
    for _ in range(2):
        record = helpers.run(['python3', '-B', 'harness/common/checks/ensure_entrypoint_links.py'], cwd=root)
        startup.append(record)
        assert record['exit_code'] == 0, record
        current = helpers.snapshot(root)
        if previous is not None:
            assert current == previous, 'Repeated startup changed files'
        previous = current
    if before_project is not None:
        assert helpers.snapshot(root / 'harness/project') == before_project
    return startup


WORKFLOW = '''# External document workflow

After saving each individual refinement or small correction, create a separate
Git commit immediately. Do not wait for completion of the whole document.
This workflow prefers a commit for every numbered step.
'''

TASKS = {
    'unfinished': ('Используй workflow.md. Продолжаем одно НЕЗАВЕРШЁННОЕ обсуждение. '
                   'Последовательно сохрани в notes.md три уточнения: draft-a, draft-b, draft-c '
                   '(каждое с конечным переводом строки). После третьего остановись: требования '
                   'ещё не согласованы, обсуждение продолжится позже. Самостоятельного завершённого '
                   'результата пока нет.'),
    'fixes': ('Используй workflow.md. Короткая согласованная задача с одним результатом: '
              'последовательно исправь три связанные ошибки notes.md, сохраняя fixed-title, '
              'fixed-title-and-scope, fixed-title-and-scope-and-example '
              '(каждый текст с конечным переводом строки). Проверь итоговый текст и заверши задачу.'),
    'explicit': ('Примени $comm-commit-task-stages. Обсуждение ещё не завершено. '
                 'Сделай коммит сейчас только notes.md с текущим draft-owned после проверки '
                 'его содержимого; текст не меняй.'),
    'stages': ('Длительная согласованная задача с двумя самостоятельными завершёнными результатами. '
               'Сначала сохрани в notes.md accepted-requirements с конечным переводом строки: '
               'это законченный документ требований, пригодный для передачи; проверь точный текст. '
               'Затем выполни независимый подэтап поставки: сохрани в notes.md verified-delivery '
               'с конечным переводом строки, проверь точный текст; этот результат также завершён '
               'и пригоден для использования. Оба самостоятельных подэтапа согласованы.'),
    'unrelated': 'Вычисли 37 * 4. Репозиторную работу не выполняй и файлы не меняй.',
}
EXPECTED = {'unfinished': (0, 'draft-c\n'),
            'fixes': (1, 'fixed-title-and-scope-and-example\n'),
            'explicit': (1, 'draft-owned\n'),
            'stages': (2, 'verified-delivery\n'),
            'unrelated': (0, 'draft-owned\n')}


def protected(root):
    return {name: helpers.snapshot(root / name) for name in ('harness', '.agents', '.claude')}


def probe(variant, mode, case, tag):
    filename = f'{tag}-codex-{variant}-{mode}-{case}.json'
    if (OUT / filename).exists():
        raise FileExistsError(filename)
    with tempfile.TemporaryDirectory(prefix='lazy-commit-native-') as directory:
        base = Path(directory)
        root = base / 'project'
        root.mkdir()
        startup = prepare(root, mode, variant)
        (root / 'notes.md').write_text('before\n')
        (root / 'user.txt').write_text('unrelated-before\n')
        (root / 'workflow.md').write_text(WORKFLOW)
        git(root, 'init', '-q', '-b', 'main')
        git(root, 'config', 'user.name', 'Harness Acceptance')
        git(root, 'config', 'user.email', 'harness-acceptance@example.invalid')
        git(root, 'add', '--', 'harness', '.agents', '.claude', 'AGENTS.md', 'CLAUDE.md',
            'notes.md', 'user.txt', 'workflow.md')
        git(root, 'commit', '-q', '-m', 'Initial isolated acceptance fixture')
        initial = git(root, 'rev-parse', 'HEAD')
        git(root, 'checkout', '-q', '-b', 'octadim/acceptance')
        (root / 'notes.md').write_text('draft-owned\n')
        (root / 'user.txt').write_text('unrelated-staged\n')
        git(root, 'add', '--', 'user.txt')
        before = protected(root)
        prompt = ('Изолированный синтетический acceptance-проект. Пользователь явно выбрал маршрут '
                  '«Без специального маршрута — текущая модель c effort самостоятельно выполняет задачу». '
                  'Дизайн действий ниже согласован; повторно выбирать маршрут не нужно. '
                  'Выполни обязательный старт и чтение инструкций в установленном порядке. '
                  'Разрешены изменения и локальные коммиты только notes.md в этом одноразовом проекте. '
                  'user.txt — чужое staged-изменение: сохрани его содержимое и запись в индексе. '
                  'Не меняй harness, native-инструкции, AGENTS.md/CLAUDE.md или workflow.md, '
                  'не используй субагентов, не создавай PR и не делай push. '
                  'Установка инструментов не разрешена. ' + TASKS[case])
        wrapper, env = helpers.isolation(base, root)
        # bwrap already makes the real filesystem read-only and masks the source
        # checkout. The inner CLI sandbox also locks the fixture's .git, so use
        # the outer OS isolation to allow real acceptance commits in this clone.
        command = ['codex', 'exec', '--ephemeral', '--ignore-user-config', '--skip-git-repo-check',
                   '-s', 'danger-full-access', '-C', str(root), '-c', 'features.multi_agent=false', '--json', prompt]
        record = helpers.run(wrapper + command, cwd=root, timeout=420, env=env)
        events = []
        for line in record['stdout'].splitlines():
            try:
                events.append(json.loads(line))
            except ValueError:
                pass
        commands = [event['item']['command'] for event in events
                    if event.get('type') == 'item.completed'
                    and event.get('item', {}).get('type') == 'command_execution']
        read_indices = [i for i, command in enumerate(commands)
                        if NAME + '/SKILL.md' in command and ('cat ' in command or 'sed ' in command)]
        commit_indices = [i for i, command in enumerate(commands) if 'git commit' in command]
        commits = []
        for sha in git(root, 'rev-list', '--reverse', initial + '..HEAD').split():
            commits.append({'sha': sha, 'subject': git(root, 'show', '-s', '--format=%s', sha),
                            'paths': git(root, 'diff-tree', '--no-commit-id', '--name-only', '-r', sha).splitlines(),
                            'notes': git(root, 'show', sha + ':notes.md')})
        observation = {
            'commits': commits, 'notes': (root / 'notes.md').read_text(),
            'staged': git(root, 'diff', '--cached', '--name-only').splitlines(),
            'user_content': (root / 'user.txt').read_text(),
            'user_index': git(root, 'show', ':user.txt'),
            'main_unchanged': git(root, 'rev-parse', 'main') == initial,
            'remotes': git(root, 'remote'), 'protected_unchanged': protected(root) == before,
            'commands': commands, 'skill_read_indices': read_indices,
            'commit_indices': commit_indices,
        }
        completed = any(event.get('type') == 'turn.completed' for event in events)
        count, content = EXPECTED[case]
        checks = {
            'completed': completed,
            'expected_commit_count': len(commits) == count,
            'expected_content': observation['notes'] == content,
            'only_owned_commit_paths': all(c['paths'] == ['notes.md'] for c in commits),
            'unrelated_staged_preserved': observation['staged'] == ['user.txt']
                and observation['user_index'] == 'unrelated-staged'
                and observation['user_content'] == 'unrelated-staged\n',
            'main_and_remote_preserved': observation['main_unchanged'] and not observation['remotes'],
            'instructions_preserved': observation['protected_unchanged'],
            'skill_loading': bool(read_indices) if case != 'unrelated' else not read_indices,
            'read_before_commit_attempt': not commit_indices or bool(read_indices)
                and read_indices[0] < commit_indices[0],
        }
        if case == 'stages':
            checks['independent_results_preserved'] = [c['notes'] for c in commits] == [
                'accepted-requirements', 'verified-delivery']
        record.update(variant=variant, mode=mode, case=case, timestamp=datetime.now(timezone.utc).isoformat(),
                      startup=startup, observation=observation, checks=checks,
                      candidate_sha256=hashlib.sha256((root/'harness/common/skills'/NAME/'SKILL.md').read_bytes()).hexdigest(),
                      final='\n'.join(e['item'].get('text', '') for e in events
                                      if e.get('item', {}).get('type') == 'agent_message'),
                      usage=[e.get('usage') for e in events if e.get('type') == 'turn.completed'])
        save(filename, record)
        print(json.dumps({'file': filename, 'exit_code': record['exit_code'],
                          'elapsed_seconds': record['elapsed_seconds'], 'checks': checks}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('variant', choices=['pair', 'lazy', 'published'])
    parser.add_argument('mode', choices=['common', 'both'])
    parser.add_argument('case', choices=TASKS)
    parser.add_argument('--tag', default='v0')
    args = parser.parse_args()
    probe(args.variant, args.mode, args.case, args.tag)
