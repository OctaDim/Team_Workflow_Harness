"""Run one live Codex link-timing scenario on a disposable bootstrapped installation."""
import argparse
import json
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REQUEST = Path(__file__).absolute().parent
NATIVE = runpy.run_path(str(REQUEST / 'u4-native.py'))
DECODE = runpy.run_path(str(REQUEST / 'u4-native-score.py'))['rollout_outputs']
BASE = Path('harness/common')
ALWAYS = 'comm-fixture-entry'
CONDITIONAL = 'comm-fixture-amber'
SCENARIOS = ('conditional-at-start', 'conditional-mid-task', 'inactive')


def setup(root, scenario):
    rule = BASE / 'rules/comm-fixture-reading.md'
    for name, description, contract in (
            (ALWAYS, 'Use for the initial fixture receipt.', 'В конце ответа укажи код начала 4319.'),
            (CONDITIONAL, 'Use before measuring an amber order.', 'Для янтарного заказа добавь к измерению 17.')):
        folder = root / BASE / 'skills' / name
        folder.mkdir()
        (folder / 'SKILL.md').write_text(f'---\nname: {name}\ndescription: {description}\n---\n\n{contract}\n')
    (root / rule).write_text(
        f'Сразу после получения этого always loaded правила прочитай файл `{BASE}/skills/{ALWAYS}/SKILL.md`.\n'
        f'Если заказ янтарный, до чтения его измерения прочитай файл SKILL.md контекстного lazy скилла {CONDITIONAL}.\n')
    (root / 'order.txt').write_text('Тип заказа — янтарный.\n' if scenario != 'inactive' else 'Тип заказа — обычный.\n')
    (root / 'measure.txt').write_text('84\n')
    install = [sys.executable, '-B', str(BASE / 'checks/ensure_entrypoint_links.py')]
    for expected in (3, 0):
        completed = subprocess.run(install, cwd=root, capture_output=True)
        if completed.returncode != expected:
            raise RuntimeError(completed.stderr.decode())
    return rule


def score(directory, rule, scenario):
    root = directory / 'workspace'
    logs = list((directory / 'client/.codex/sessions').rglob('rollout-*.jsonl'))
    if len(logs) != 1:
        return {'status': 'unverified', 'reason': 'no unique model-input trace'}
    rules = {str(p.relative_to(root)): p.read_text().rstrip('\n') for p in (root / '.claude/rules').rglob('*.md')}
    skills = {name: (root / BASE / 'skills' / name / 'SKILL.md').read_text().rstrip('\n')
              for name in (ALWAYS, CONDITIONAL)}
    received = {key: [] for key in rules | skills}
    native = set()
    commands, accesses, final = {}, {}, ''
    task_calls = []
    for i, line in enumerate(logs[0].read_text().splitlines()):
        event = json.loads(line)
        if event.get('type') != 'response_item':
            continue
        item = event['payload']
        kind = item.get('type')
        if kind in ('function_call', 'custom_tool_call'):
            cmd = item.get('arguments') or item.get('input', '')
            commands[item['call_id']] = (i, cmd)
            for filename in ('order.txt', 'measure.txt'):
                if filename in cmd:
                    task_calls.append(i)
        if kind == 'message' and item.get('role') == 'assistant' and item.get('phase') == 'final_answer':
            final = DECODE(item.get('content', []))
        if kind in ('custom_tool_call_output', 'function_call_output'):
            text = DECODE(item.get('output', ''))
        elif kind == 'message' and item.get('role') in ('user', 'system', 'developer') and not commands:
            text = DECODE(item.get('content', []))
        else:
            continue
        for path, body in (rules | skills).items():
            if body in text:
                received[path].append(i)
                if kind == 'message':
                    native.add(path)
        if kind in ('custom_tool_call_output', 'function_call_output'):
            call, cmd = commands.get(item.get('call_id'), (-1, ''))
            if 'order.txt' in cmd and (root/'order.txt').read_text().strip() in text:
                accesses.setdefault('order.txt', call)
                accesses.setdefault('order result', i)
            if 'measure.txt' in cmd and re.search(r'(?m)^84$', text):
                accesses.setdefault('measure.txt', call)

    first = min(task_calls, default=-1)
    accesses['first task command'] = first
    owner = str(Path('.claude/rules') / rule.name)
    seen = lambda k: received[k][0] if received[k] else -1
    missing = [k for k in rules if not 0 <= seen(k) < first]
    problems = []
    repeats = {key: len(returns)-1 for key, returns in received.items() if len(returns)>1}
    if repeats:
        problems.append('repeated complete text')
    if missing:
        problems.append('incomplete startup before first task command')
    if not (0 <= seen(owner) < first and 0 <= seen(ALWAYS) < first):
        problems.append('unconditional skill missing or late')
    elif any(seen(owner) < i < seen(ALWAYS) and ALWAYS not in cmd and 'SKILL.md' not in cmd
             for i, cmd in commands.values()):
        problems.append('intervening tool call before unconditional skill')
    if scenario == 'inactive':
        if received[CONDITIONAL]:
            problems.append('premature conditional load')
    else:
        if not 0 <= seen(CONDITIONAL) < accesses.get('measure.txt', -1):
            problems.append('conditional skill missing before dependent action')
        if scenario == 'conditional-mid-task' and not 0 <= accesses.get('order result', -1) < seen(CONDITIONAL):
            problems.append('mid-task condition not established before skill')
    result = 84 if scenario == 'inactive' else 101
    if not all(re.search(rf'(?<!\d){number}(?!\d)', final) for number in (4319, result)):
        problems.append('expected receipt or measurement missing')
    return {'status': 'pass' if not problems else 'failed', 'problems': problems,
            'rules_expected': len(rules), 'missing_before_action': missing,
            'observed_native_rules': len(native & rules.keys()),
            'rules_read_before_action': sum(0 <= seen(k) < first for k in rules),
            'repeated_full_rules': sum(max(len(received[k])-1, 0) for k in rules),
            'repeated_paths': repeats, 'owner_return': seen(owner), 'unconditional_return': seen(ALWAYS),
            'conditional_return': seen(CONDITIONAL), 'task_events': accesses}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('installation', type=Path)
    parser.add_argument('scenario', choices=SCENARIOS)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='link-scenario-') as folder:
        root = Path(folder) / args.installation.name
        shutil.copytree(args.installation, root, ignore=shutil.ignore_patterns('.pytest_cache', '__pycache__'))
        rule = setup(root, args.scenario)
        prompt = ('Заказ янтарный. ' if args.scenario == 'conditional-at-start'
                  else 'Определи тип заказа из order.txt. ')
        NATIVE['PROMPTS']['answer'] = prompt + 'Сообщи итоговое измерение по значению из measure.txt.'
        run = NATIVE['evaluate'](root, 'codex', 'mandatory', 'answer', 1)
        result = score(Path(run['local_trace']), rule, args.scenario) if run.get('model_answers') else {
            'status': 'unverified', 'reason': run['error_classes']}
        print(json.dumps({'mode': root.name, 'scenario': args.scenario, **result}, ensure_ascii=False))


if __name__ == '__main__':
    main()
