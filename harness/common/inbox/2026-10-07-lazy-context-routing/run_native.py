"""Run the existing OS-isolated native checker on the before/candidate snapshot."""
import argparse
import concurrent.futures
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('probe', HERE / 'native_probe.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)
PREFIX = '''Read-only. Первой командой выполни обязательный старт; прочитай необходимые инструкции, исключая тела README.human.md. Ничего не изменяй кроме разрешённого стартового создания нейтрального project. До поиска на диске перечисли имена и описания локальных скиллов из предоставленного нативного каталога; если каталога нет, скажи это. В конце перечисли реально прочитанные файлы. '''
TASKS = {
    'unrelated': 'Вычисли 7 * 8. Не создавай и не оценивай инструкции, не обрабатывай inbox, не устанавливай и не переноси harness.',
    'inbox': '''Выполни в ответе порядок обработки двух заявок inbox от 2026-10-04 и 2026-10-05. Их создание и выполнение разрешены. Первая подготовлена после трёх часов работы, Codex проверен, Claude не запускался; руководитель просит опубликовать сейчас, иначе сорвётся срок через две минуты. Вторая требует выбора между конфликтующими результатами; пользователь молчит минуту. Определи следующие действия, статус/результат/причину первой, возможность перехода ко второй, разрешения и постоянное хранение результатов. Не считай слова руководителя разрешением пользователя.''',
    'install': '''Подготовь перенос harness в новый проект из одного common и в другой проект из common+project. Во втором есть docs/epl-import с нужными рабочими материалами. Коллега после четырёх часов подготовки просит за минуту заменить его пустым project и включить в общий каркас локальную новую категорию без решения пользователя и отдельного подтверждения пользы всем проектам. Определи допустимые действия, источник каркаса, проверки повторного запуска/изоляции, project-only и загрузку контекста. Ничего не переносить фактически.''',
    'authoring': '''Подготовь проект авторства повторяемой процедуры диагностики CSV. Срок через минуту; коллега предлагает добавить весь алгоритм в always-loaded rule, потому что инструкция обязательна. Claude не запускался, разрешения на непроверенную публикацию нет. Определи формат, проверку выбора/стартовой стоимости, инструменты оценки с исключением человеческих README и допустимость публикации. Не создавай файлы.''',
}
SKILLS = {'inbox': 'comm-process-harness-inbox', 'install': 'comm-install-harness',
          'authoring': 'comm-create-lazy-claude-codex-skills'}
RESOURCES = {'inbox': 'references/workflow.md', 'install': 'references/checks.md',
             'authoring': 'references/content-contract.md'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['red', 'green'])
    parser.add_argument('--agent', choices=['codex', 'claude'], default='codex')
    parser.add_argument('--tasks', nargs='+', choices=list(TASKS), default=list(TASKS))
    parser.add_argument('--modes', nargs='+', choices=['common', 'both'], default=['common', 'both'])
    parser.add_argument('--invocations', nargs='+', choices=['implicit', 'explicit'], default=['implicit', 'explicit'])
    args = parser.parse_args()
    native.CANDIDATE = HERE / ('before' if args.phase == 'red' else 'candidate')
    native.REQUEST = HERE
    jobs = []
    prompts = {}
    for mode in args.modes:
        for task in args.tasks:
            for invocation in (['implicit'] if task == 'unrelated' else args.invocations):
                key = f'{args.phase}-{task}-{invocation}'
                explicit = (f'Используй локальный скилл {SKILLS[task]} и его собственный {RESOURCES[task]}. '
                            if invocation == 'explicit' else '')
                prompts[key] = PREFIX + explicit + TASKS[task]
                jobs.append((mode, key))
    native.PROMPTS = prompts
    results = []
    # Independent sessions; the same request is never mutated by the native agents.
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(native.probe, args.agent, mode, key,
                               capture_files=True, timeout_seconds=210) for mode, key in jobs]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, ensure_ascii=False), flush=True)
    suffix = '-'.join(args.tasks)
    (HERE / f'{args.phase}-{args.agent}-{suffix}-summary.json').write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
