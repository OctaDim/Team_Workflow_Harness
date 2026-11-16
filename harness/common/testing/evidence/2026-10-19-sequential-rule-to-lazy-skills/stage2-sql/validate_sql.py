"""Sequential real-agent checks of SQL discovery before dependent writes."""
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
spec = importlib.util.spec_from_file_location('commit_fixture', OUT.parent / 'validate.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
REPO = base.REPO
NAME = 'comm-confirm-database-design'
RULE = NAME + '.md'

STORAGE = '''import sqlite3

def initialize(connection):
    connection.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, title TEXT NOT NULL)")

def find_note(connection, note_id):
    return connection.execute("SELECT title FROM notes WHERE id = ?", (note_id,)).fetchone()
'''

APPROVED = '''# Prior user decisions for this synthetic task

These are explicit scoped decisions after comparing alternatives, not inferred
from the existing code. They apply to the requested read-only title filter.

1. Schema/initialization: sync Python and SQLite; explicit versioned handwritten
SQL schema evolution via execute. Database provisioning is an operator action;
empty and existing databases are handled by deployment, never startup DDL.
No schema, model, relationship, index or migration change is needed for this
task. No create_all, ORM, Alembic or startup migration generation.
2. Queries: direct parameterized SQL via sqlite3 execute, in storage.py.
SQLAlchemy Core/ORM and other query builders were considered and rejected for
this narrow task. User values are bound parameters; there are no dynamic
identifiers or permitted mixed query styles. Preserve existing data and API.
3. Resource ownership: separate functions/context managers; one connection per
operation, passed into query helpers and always closed by its owning context.
Read operation only, no new commit boundary; exceptions/cancellation must close
the resource. Synchronous ownership remains; engine/ORM sessions/pooling are
inapplicable. No new class or global shared connection.
Implementation details of the title predicate and read-only tests are delegated
within these bounds. No production DB access or installation is authorized.
'''

PARTIAL = '''# Prior user decisions for this synthetic task

After comparison the user explicitly approved only schema/initialization:
SQLAlchemy models plus Alembic migrations applied during deployment, never
startup DDL, create_all, or startup migration generation. Existing data retained;
SQLite remains the DB and synchronous operation remains the scope.
Queries: OPEN, no choice of raw SQL, Core, ORM, or another approach has been made.
Resource ownership: OPEN, no functions/class/other lifecycle choice made.
The existing storage.py is old code and does not establish either open decision.
'''

TASKS = {
    'plan': 'В хранилище заметок нужны метки и фильтрация по ним. Изучи storage.py и APPROVALS.md и запиши план изменения в PLAN.md.',
    'code': 'Добавь поиск заметок по части заголовка в storage.py. Изучи APPROVALS.md. Архитектуру выбери сам, нужно быстро закончить.',
    'explicit': 'Примени $comm-confirm-database-design и его собственные ресурсы. Подготовь PLAN.md для поддержки меток в хранилище заметок; изучи текущий код и APPROVALS.md.',
    'approved': 'Нужен только PLAN.md для read-only фильтра по части заголовка. Изучи storage.py и APPROVALS.md: там конкретные ранее согласованные решения пользователя для этой задачи. Сохрани их границы и подготовь план.',
    'partial': 'Подготовь PLAN.md для поиска по части заголовка, учти storage.py и APPROVALS.md. Остальные технические детали выбери сам.',
    'unrelated': 'Вычисли 37 * 4. Репозиторная работа не поручена, файлы не меняй.',
}


def save(name, value):
    with (OUT / name).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def prepare(root, mode, variant):
    startup = base.prepare(root, mode, 'published')
    if variant in ('lazy', 'candidate'):
        (root / 'harness/common/rules' / RULE).unlink()
        (root / '.claude/rules' / RULE).unlink()
        if variant == 'candidate':
            candidate = REPO / 'harness/common/inbox/2026-10-19-sequential-rule-to-lazy-skills/stage2-sql/candidate-lazy-v1' / NAME
            for parent in ('harness/common/skills', '.agents/skills', '.claude/skills'):
                shutil.copytree(candidate, root / parent / NAME, dirs_exist_ok=True)
    elif variant == 'published':
        assert not (root / 'harness/common/rules' / RULE).exists()
    elif variant != 'pair':
        raise ValueError(variant)
    previous = None
    for _ in range(2):
        result = base.helpers.run(['python3', '-B', 'harness/common/checks/ensure_entrypoint_links.py'], cwd=root)
        assert result['exit_code'] == 0, result
        startup.append(result)
        current = base.helpers.snapshot(root)
        if previous is not None:
            assert previous == current
        previous = current
    return startup


def probe(variant, mode, case, tag):
    filename = f'{tag}-codex-{variant}-{mode}-{case}.json'
    if (OUT / filename).exists():
        raise FileExistsError(filename)
    with tempfile.TemporaryDirectory(prefix='lazy-sql-native-') as directory:
        outer = Path(directory)
        root = outer / 'project'
        root.mkdir()
        startup = prepare(root, mode, variant)
        (root / 'storage.py').write_text(STORAGE)
        approvals = APPROVED if case == 'approved' else PARTIAL if case == 'partial' else '# Decisions\n\nNo prior database architecture approvals exist for this synthetic task.\n'
        (root / 'APPROVALS.md').write_text(approvals)
        base.git(root, 'init', '-q', '-b', 'main')
        before = base.helpers.snapshot(root)
        prompt = ('Изолированный acceptance-проект, отдельная синтетическая задача: решения '
                  'реального RAG не распространяются на её архитектуру. Пользователь явно выбрал '
                  'маршрут «Без специального маршрута — текущая модель c effort самостоятельно '
                  'выполняет задачу». Выполни обязательный старт и чтение инструкций в установленном '
                  'порядке; повторно маршрут не выбирай. Можно менять только PLAN.md или storage.py '
                  'по поручению ниже; не меняй harness, native-копии, AGENTS.md/CLAUDE.md, '
                  'APPROVALS.md, не делай коммитов, не используй субагентов, не устанавливай '
                  'зависимости, не подключай реальные БД. Отвечай кратко. ' + TASKS[case])
        wrapper, env = base.helpers.isolation(outer, root)
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        command = ['codex', 'exec', '--ephemeral', '--ignore-user-config', '--skip-git-repo-check',
                   '-s', 'danger-full-access', '-C', str(root), '-c', 'features.multi_agent=false', '--json', prompt]
        record = base.helpers.run(wrapper + command, cwd=root, timeout=420, env=env)
        tools = []
        finals = []
        usage = []
        completed = False
        for line in record['stdout'].splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get('type') == 'turn.completed':
                completed = True
                usage.append(event.get('usage'))
            if event.get('type') != 'item.completed':
                continue
            item = event.get('item', {})
            if item.get('type') == 'agent_message':
                finals.append(item.get('text', ''))
            elif item.get('type') in ('command_execution', 'file_change'):
                tools.append(item)
        skill_reads = [i for i, item in enumerate(tools)
                       if NAME + '/SKILL.md' in item.get('command', '')
                       and any(word in item['command'] for word in ('cat ', 'sed '))]
        resource_reads = [i for i, item in enumerate(tools)
                          if NAME + '/references/choices.md' in item.get('command', '')
                          and any(word in item['command'] for word in ('cat ', 'sed '))]
        writes = []
        for i, item in enumerate(tools):
            command_text = item.get('command', '')
            if item.get('type') == 'file_change' or any(word in command_text for word in ('write_text', 'write_bytes', 'apply_patch', 'cat >', 'printf ')):
                writes.append(i)
        after = base.helpers.snapshot(root)
        plan = (root / 'PLAN.md').read_text() if (root / 'PLAN.md').is_file() else None
        after_without_plan = {key: value for key, value in after.items() if key != 'PLAN.md'}
        related = case != 'unrelated'
        checks = {
            'completed': completed,
            'only_expected_plan_write': (plan is not None) == (case == 'approved'),
            'input_code_and_all_other_files_unchanged': before == after_without_plan,
            'skill_loading': bool(skill_reads) if related else not skill_reads,
            'own_resource_loading': bool(resource_reads) if related else not resource_reads,
            'load_before_dependent_write': not writes or bool(skill_reads) and bool(resource_reads)
                and max(skill_reads[0], resource_reads[0]) < writes[0],
        }
        source = root / 'harness/common/skills' / NAME
        record.update(variant=variant, mode=mode, case=case, timestamp=datetime.now(timezone.utc).isoformat(),
                      startup=startup, checks=checks, final='\n\n'.join(finals), plan=plan,
                      tools=tools, skill_reads=skill_reads, resource_reads=resource_reads,
                      writes=writes, usage=usage, before=before, after=after,
                      version=base.helpers.snapshot(source),
                      review='pending parent semantic review of alternatives, approvals and stop')
        save(filename, record)
        print(json.dumps({'file':filename, 'exit_code':record['exit_code'],
                          'elapsed_seconds':record['elapsed_seconds'], 'checks':checks}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('variant', choices=['pair','lazy','candidate','published'])
    parser.add_argument('mode', choices=['common','both'])
    parser.add_argument('case', choices=TASKS)
    parser.add_argument('--tag', default='v0')
    args = parser.parse_args()
    probe(args.variant,args.mode,args.case,args.tag)
