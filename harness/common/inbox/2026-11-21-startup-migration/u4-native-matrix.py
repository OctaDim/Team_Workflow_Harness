"""List the balanced V5 sequence or execute the eight offline initialization cells."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import runpy


def model_schedule():
    for repeat in (1, 2):
        for task in ('answer', 'history', 'explain', 'change'):
            for mode in ('common-only', 'common-project'):
                for client in ('codex', 'claude'):
                    policies = ('mandatory', 'optional')
                    if repeat == 2:
                        policies = tuple(reversed(policies))
                    for policy in policies:
                        yield {'client': client, 'install': mode, 'policy': policy,
                               'task': task, 'repeat': repeat}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline-initialization', type=Path, metavar='BOOTSTRAPPED_PARENT',
                        help='Use both candidate installations. No online model sessions.')
    parser.add_argument('--codex-wave', type=Path, metavar='BOOTSTRAPPED_PARENT',
                        help='Run four Codex model cells for the selected task and repeat.')
    parser.add_argument('--task', choices=('answer','history','explain','change'))
    parser.add_argument('--repeat', type=int, choices=(1,2))
    args = parser.parse_args()
    if args.codex_wave and args.offline_initialization:
        parser.error('Select one run mode')
    if not args.offline_initialization and not args.codex_wave:
        print(json.dumps(list(model_schedule()), indent=2))
        return
    evaluate = runpy.run_path(str(Path(__file__).with_name('u4-native.py')))['evaluate']
    if args.codex_wave:
        if not args.task or not args.repeat:
            parser.error('Select the task and repeat for the Codex wave.')
        score = runpy.run_path(str(Path(__file__).with_name('u4-native-score.py')))['score']
        selected = [r for r in model_schedule() if r['client']=='codex' and r['task']==args.task and r['repeat']==args.repeat]
        def run_cell(r):
            result = evaluate(args.codex_wave.resolve()/r['install'], 'codex', r['policy'],
                              r['task'], r['repeat'])
            result['score'] = score(Path(result['local_trace']),r['task'])
            return result
        with ThreadPoolExecutor(max_workers=4) as pool:
            for result in pool.map(run_cell, selected):
                print(json.dumps(result, ensure_ascii=False), flush=True)
        return
    cells = []
    for row in model_schedule():
        if row['task'] != 'answer' or row['repeat'] != 1:
            continue
        result = evaluate(args.offline_initialization.resolve() / row['install'],
                          row['client'], row['policy'], row['task'], row['repeat'], local_only=True)
        result.pop('local_trace', None)
        cells.append(result)
    print(json.dumps({'scope': 'local CLI initialization; no model responses or token measurements',
                      'cells': cells}, indent=2))


if __name__ == '__main__':
    main()
