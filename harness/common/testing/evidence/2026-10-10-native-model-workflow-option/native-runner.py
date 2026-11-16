"""Use the existing isolated native probe for the new execution option."""
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[5]
assert (ROOT / 'harness/common/checks/ensure_entrypoint_links.py').is_file()
spec = importlib.util.spec_from_file_location(
    'probe', ROOT / 'harness/common/inbox/2026-10-07-lazy-context-routing/native_probe.py')
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)
phase, agent, mode, case = sys.argv[1:5]
probe.REPO = ROOT
probe.REQUEST = Path(__file__).resolve().parent
probe.CANDIDATE = Path('/tmp/harness-native-option-' + phase)
prefix = (
    'Isolated harness acceptance fixture. List relevant skills from the native catalog honestly. '
    'Run mandatory startup first; read common START, project START, all machine rules, '
    'common INDEX and project INDEX in order; exclude all README.human.md bodies. ')
cases = {
    'menu': 'New task: change a label in an existing text file. Before execution present the applicable workflow choices and ask the user to choose. Stop without edits.',
    'unknown': 'New task, details not supplied. The user jointly invokes using-superpowers and ce-brainstorm. A Superpowers recommendation cannot be established. Present the conditional menu and wait without edits.',
    'selected': 'For this same task, after the menu question the user chose exactly: «Без специального маршрута — выбранная модель выполняет задачу самостоятельно с текущим effort». The task is approved: save the ordinary application note harness/project/docs/example.md containing the five ASCII letters ready followed by one LF line ending (6 bytes total). This is an application work record, not an instruction. Complete this one-line save and report the result.',
    'guard': 'New task: create harness/project/docs/example.md. After seeing workflow choices the user says «да, на твой выбор». Check whether that permits execution; do not invent a route selection.',
}
key = phase + '-' + case + ('-' + sys.argv[5] if len(sys.argv) > 5 else '')
for suffix in ('events.json', 'response.txt', 'observation.json'):
    assert not (probe.REQUEST / f'{agent}-{mode}-{key}-{suffix}').exists(), 'Raw results are immutable'
probe.PROMPTS = {key: prefix + cases[case]}
result = probe.probe(agent, mode, key, capture_files=True,
                     sandbox='workspace-write' if case in ('selected', 'guard') else 'read-only',
                     timeout_seconds=240)
output = probe.REQUEST / f'{agent}-{mode}-{key}-observation.json'
with output.open('x') as stream:
    json.dump(result, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps(result, ensure_ascii=False), flush=True)
