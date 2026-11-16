"""Reuse the isolated native harness probe; no source project or home skills leak."""
import importlib.util
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[5]
EVIDENCE = Path(__file__).resolve().parent
FIXTURES = Path('/tmp/ce-routes-20261011')
RULE = Path('harness/common/rules/comm-confirm-development-workflow.md')
SUPERPOWERS = Path('/home/octadim/.codex/plugins/cache/openai-curated-remote/superpowers/6.4.2/skills')
CE = Path('/home/octadim/.codex/plugins/cache/compound-engineering-plugin/compound-engineering/3.30.4/skills')
SPEC = importlib.util.spec_from_file_location(
    'probe', ROOT / 'harness/common/inbox/2026-10-07-lazy-context-routing/native_probe.py')
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)

CASES = {
    'menu': 'New task: change one label in an existing text file. No named skill is invoked. Present the applicable workflow menu, request one explicit route choice and stop.',
    'using-only': 'New task: change one label in an existing text file. Only using-superpowers is explicitly invoked. Present the applicable menu, request one explicit route choice and stop.',
    'ce-only': 'New task: change one label in an existing text file. Only ce-brainstorm is explicitly invoked. Present the applicable menu, request one explicit route choice and stop.',
    'unknown': 'New task: no task details or skill invocations supplied. A recommendation cannot be established. Present the conditional workflow choices and ask for one explicit route.',
    'selected-joint': 'Same task after the menu question. The user selected exactly using-superpowers + ce-brainstorm → ce-plan → ce-work. The task is to change the existing label Start to Begin in a tiny application. Apply the initial procedures to establish the requirements for this bounded change, without implementation or writing a plan. Show the useful result and next CE handoff. Stage approvals remain pending.',
    'selected-ce': 'Same task after the menu question. The user selected exactly ce-brainstorm → ce-plan → ce-work (native CE). The task is to change the existing label Start to Begin in a tiny application. Apply the initial procedure to establish requirements, without implementation or writing a plan. Show the useful result and next CE handoff. Stage approvals remain pending.',
    'guard': 'New task: save an ordinary application note at harness/project/docs/example.md. After the menu question the user says «да, на твой выбор». Assess whether execution is allowed; do not select a route for the user.',
    'unrelated': 'Read-only factual question: report the current byte length of harness/project/INDEX.md. Do not modify files or start a development workflow.',
    'selected-native': 'Same task after the menu question. The user selected exactly «Без специального маршрута — текущая модель c effort самостоятельно выполняет задачу.». Save the approved ordinary application note harness/project/docs/example.md with exactly the ASCII bytes ready followed by one LF (6 bytes). This is an application work record, not an instruction. Complete the save independently without changing model or effort.',
}
PREFIX = ('Isolated acceptance fixture. List relevant native catalog skills honestly. '
          'First shell command must be python3 -B harness/common/checks/ensure_entrypoint_links.py. '
          'Then read common START, project START, all machine rules, common INDEX, project INDEX '
          'in that exact order before any skill body. Obtain the entire .claude/rules Markdown '
          'path list excluding README.human.md in one completed call, then read all those '
          'explicit paths in a separate completed call. Never read human guide bodies. '
          'Answer in Russian. No implementation, publication or commits are authorized. ')


def setup(phase):
    dest = FIXTURES / phase
    assert not dest.exists(), 'Keep earlier fixtures intact'
    ignore = shutil.ignore_patterns('inbox', 'evidence', '__pycache__')
    for package in ('common', 'project'):
        shutil.copytree(ROOT / 'harness' / package, dest / 'harness' / package, ignore=ignore)
    for folder in ('.agents/skills', '.claude/skills', '.claude/rules'):
        shutil.copytree(ROOT / folder, dest / folder, ignore=ignore)
    for name in ('AGENTS.md', 'CLAUDE.md'):
        shutil.copyfile(ROOT / name, dest / name)
    for owner, names in ((SUPERPOWERS, ('using-superpowers', 'brainstorming')),
                         (CE, ('ce-brainstorm', 'ce-plan', 'ce-work', 'ce-commit'))):
        for name in names:
            for native in ('.agents/skills', '.claude/skills'):
                shutil.copytree(owner / name, dest / native / name)
    content = (EVIDENCE / (phase + '.md')).read_bytes()
    for path in (RULE, Path('.claude/rules/comm-confirm-development-workflow.md')):
        (dest / path).write_bytes(content)
    (dest / 'app-label.txt').write_text('Start\n')
    assert (dest / RULE).read_bytes() == (dest / '.claude/rules' / RULE.name).read_bytes()
    print(dest)


if __name__ == '__main__':
    if sys.argv[1] == 'setup':
        setup(sys.argv[2])
    elif sys.argv[1] == '--self-test':
        assert (ROOT / RULE).is_file()
        assert len(CASES) == 9 and 'guard' in CASES
        assert 'README.human.md' in PREFIX
        assert (SUPERPOWERS / 'using-superpowers/SKILL.md').is_file()
        assert (CE / 'ce-brainstorm/SKILL.md').is_file()
        print('Runner self-check PASS')
    else:
        phase, mode, case = sys.argv[1:4]
        key = phase + '-' + case
        if len(sys.argv) > 4 and sys.argv[4] == 'enabled':
            enabled = importlib.util.spec_from_file_location('probe_enabled', EVIDENCE / 'native-probe-enabled-v2.py')
            probe = importlib.util.module_from_spec(enabled)
            enabled.loader.exec_module(probe)
            key += '-enabled'
        for suffix in ('events.json', 'response.txt', 'observation.json'):
            assert not (EVIDENCE / f'codex-{mode}-{key}-{suffix}').exists(), 'Raw results are immutable'
        probe.REPO, probe.REQUEST, probe.CANDIDATE = ROOT, EVIDENCE, FIXTURES / phase
        prefix = PREFIX.replace('No implementation, publication or commits are authorized.',
                                'Only the specified ordinary application note save is authorized; no publication or commits.') if case == 'selected-native' else PREFIX
        probe.PROMPTS = {key: prefix + CASES[case]}
        result = probe.probe('codex', mode, key, capture_files=True,
                             sandbox='workspace-write' if case in ('guard', 'selected-native') else 'read-only',
                             timeout_seconds=240)
        with (EVIDENCE / f'codex-{mode}-{key}-observation.json').open('x') as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        print(json.dumps(result, ensure_ascii=False), flush=True)
