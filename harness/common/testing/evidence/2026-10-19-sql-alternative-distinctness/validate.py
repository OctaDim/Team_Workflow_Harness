"""Sequential native SQL probes; reuse immutable fixture and preserve all receipts."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil

OUT = Path(__file__).absolute().parent
REPO = OUT.parents[4]
REQUEST = REPO / 'harness/common/inbox/2026-10-19-sql-alternative-distinctness'
NAME = 'comm-confirm-database-design'
OLD = OUT.parent / '2026-10-19-sequential-rule-to-lazy-skills/stage2-sql/validate_sql.py'
spec = importlib.util.spec_from_file_location('prior_sql', OLD)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.OUT = OUT
original_prepare = m.prepare


def prepare(root, mode, variant):
    startup = original_prepare(root, mode, 'published')
    candidate = REQUEST / ('candidate-' + variant) / NAME
    m.base.helpers.ordinary(candidate)
    for parent in ('harness/common/skills', '.agents/skills', '.claude/skills'):
        shutil.copytree(candidate, root / parent / NAME, dirs_exist_ok=True)
    previous = None
    for _ in range(2):
        result = m.base.helpers.run(['python3', '-B', 'harness/common/checks/ensure_entrypoint_links.py'], cwd=root)
        assert result['exit_code'] == 0, result
        startup.append(result)
        current = m.base.helpers.snapshot(root)
        assert previous is None or previous == current
        previous = current
    expected = m.base.helpers.snapshot(candidate)
    for parent in ('harness/common/skills', '.agents/skills', '.claude/skills'):
        assert m.base.helpers.snapshot(root / parent / NAME) == expected
    return startup


m.prepare = prepare
m.TASKS['counterexample'] = (
    'Примени $comm-confirm-database-design. Read-only проверка предложения для '
    'storage.py и APPROVALS.md: схема — «явный SQL; SQLAlchemy + Alembic; '
    'SQL с PRAGMA user_version». Исполнитель третьего варианта не описан. '
    'Запросы — raw SQL, SQLAlchemy Core/ORM, Peewee; ownership — функции/контекст, '
    'класс-владелец, внешнее соединение приложения. Можно ли считать схему '
    'сравненной по трём различным механизмам и запросить согласование? '
    'Объясни недостаточность или достаточность, ничего не записывай.'
)
m.TASKS['validmarker'] = (
    'Примени $comm-confirm-database-design. Read-only проверка, файлы не менять. '
    'Для маленького sync sqlite3-хранилища даны три способа эволюции схемы: '
    '(1) оператор запускает наши рукописные SQL-скрипты через sqlite3.execute, '
    'это оставляет текущий стек; (2) оператор запускает ревизии Alembic с '
    'SQLAlchemy-моделями, это даёт историю модели ценой новых зависимостей; '
    '(3) оператор запускает отдельный schema-diff инструмент: он сравнивает '
    'заданную декларативную целевую схему с текущей, вычисляет и показывает '
    'DDL-план, после согласования применяет его; PRAGMA user_version служит '
    'только отметкой версии. Третий механизм уменьшает ручное сопровождение '
    'изменений для этого модуля, но требует проверки преобразований данных. '
    'Это концептуальный механизм, существование готового инструмента не '
    'утверждается. Достаточно ли механизмы различаются, несмотря на user_version, '
    'и что ещё неизвестно для утверждения пригодности третьего? '
    'Не принимай архитектуру и не выдумывай название инструмента.'
)


def run(variant, mode, case, tag):
    m.probe(variant, mode, case, tag)
    path = OUT / f'{tag}-codex-{variant}-{mode}-{case}.json'
    record = json.loads(path.read_text())
    if not all(record['checks'].values()):
        raise SystemExit(f'Mechanical check failed: {path.name}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('variant', choices=('v0', 'v1', 'v2'))
    parser.add_argument('mode', choices=('common', 'both'))
    parser.add_argument('case', choices=m.TASKS)
    parser.add_argument('--tag', required=True)
    args = parser.parse_args()
    run(args.variant, args.mode, args.case, args.tag)
