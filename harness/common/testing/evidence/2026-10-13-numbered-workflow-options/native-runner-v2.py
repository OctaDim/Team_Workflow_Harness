import importlib.util, json, shutil, sys
from pathlib import Path
ROOT = Path('/home/octadim/MyProjects/Multi_User_RAG_Assist_System')
EVIDENCE = ROOT / 'harness/common/testing/evidence/2026-10-13-numbered-workflow-options'
FIXTURE = Path('/tmp/numbered-workflow-20261013-candidate')
RULE = Path('harness/common/rules/comm-confirm-development-workflow.md')
if sys.argv[1] == 'setup':
    assert not FIXTURE.exists()
    ignore = shutil.ignore_patterns('inbox', 'evidence', '__pycache__')
    for package in ('common', 'project'):
        shutil.copytree(ROOT / 'harness' / package, FIXTURE / 'harness' / package, ignore=ignore)
    for folder in ('.agents/skills', '.claude/skills', '.claude/rules'):
        shutil.copytree(ROOT / folder, FIXTURE / folder, ignore=ignore)
    for name in ('AGENTS.md', 'CLAUDE.md'):
        shutil.copyfile(ROOT / name, FIXTURE / name)
    for owner, names in ((Path('/home/octadim/.codex/plugins/cache/openai-curated-remote/superpowers/6.4.2/skills'), ('using-superpowers', 'brainstorming')), (Path('/home/octadim/.codex/plugins/cache/compound-engineering-plugin/compound-engineering/3.30.5/skills'), ('ce-brainstorm', 'ce-plan', 'ce-work', 'ce-commit'))):
        for name in names:
            for native in ('.agents/skills', '.claude/skills'):
                shutil.copytree(owner / name, FIXTURE / native / name)
    candidate = (ROOT / 'harness/common/inbox/2026-10-13-numbered-workflow-options/comm-confirm-development-workflow.md').read_bytes()
    for path in (RULE, Path('.claude/rules/comm-confirm-development-workflow.md')):
        (FIXTURE / path).write_bytes(candidate)
    assert (FIXTURE / RULE).read_bytes() == (FIXTURE / '.claude/rules' / RULE.name).read_bytes()
    print('Isolated candidate fixture ready')
else:
    agent, mode = sys.argv[1:3]
    case = sys.argv[3] if len(sys.argv) > 3 else 'retry-menu'
    spec = importlib.util.spec_from_file_location('probe', ROOT / 'harness/common/testing/evidence/2026-10-11-always-offer-ce-workflows/native-probe-enabled-v2.py')
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)
    probe.REPO, probe.REQUEST, probe.CANDIDATE = ROOT, EVIDENCE, FIXTURE
    prefix = 'Isolated acceptance fixture. Answer in Russian. First run mandatory startup and follow the repository reading order. List native catalog skills honestly. Never read README.human.md bodies. No publication, unrelated writes, commits or subagent execution. '
    menu = 'Previous assistant menu for this same task: 1. Без специального маршрута — текущая модель c effort самостоятельно выполняет задачу. 2. Compound Engineering: ce-brainstorm → ce-plan → ce-work. 3. Superpowers, через одного агента: brainstorming → writing-plans → executing-plans. 4. Superpowers, через субагентов: brainstorming → writing-plans → subagent-driven-development. '
    note = 'The task and its application note contents are approved. Save exactly ASCII bytes ready followed by one LF at harness/project/docs/example.md, then report the chosen route and result. This is an ordinary application record. Only that file save is authorized; do not change model/effort. '
    cases = {
        'retry-menu': 'New task: change one label in an existing text file. Present applicable workflow choices, request one explicit choice and stop. No implementation is authorized.',
        'selection-matrix': menu + 'Independently assess the following user replies to that same menu: «выбираю 1», «Без специального маршрута — текущая модель c effort самостоятельно выполняет задачу.», «3», «9», «1, то есть Compound Engineering», «1 или 2», silence, «на твой выбор». For each state the accepted route/executor or required clarification. These are separate examples, not a combined user choice. Do not implement anything. Do not ask again for executor when a full numbered item already identifies it.',
        'unknown': 'New task: task details and skills needed for a recommendation are unknown. Present conditional workflow choices and ask for one explicit route; stop.',
        'number': menu + 'User reply: «1». ' + note,
        'phrase': menu + 'User reply: «выбираю 1». ' + note,
        'words': menu + 'User reply: «Без специального маршрута — текущая модель c effort самостоятельно выполняет задачу.». ' + note,
        'full': menu + 'User reply: «3». Assess which route and executor this selected. Do not ask for a redundant executor choice. No design, plan or implementation stages are authorized yet.',
        'invalid': menu + 'User reply: «9». ' + note,
        'conflict': menu + 'User reply: «1, то есть Compound Engineering». ' + note,
        'multiple': menu + 'User reply: «1 или 2». ' + note,
        'unrelated': 'Read-only factual question: report the byte length of harness/project/INDEX.md. No new development task or route selection. Do not modify files.',
    }
    assert case in cases
    probe.PROMPTS = {case: prefix + cases[case]}
    for suffix in ('events.json', 'response.txt', 'observation.json'):
        assert not (EVIDENCE / f'{agent}-{mode}-{case}-{suffix}').exists(), 'Raw evidence is immutable'
    result = probe.probe(agent, mode, case, sandbox='workspace-write' if case in ('number', 'phrase', 'words', 'invalid', 'conflict', 'multiple') else 'read-only', capture_files=True, timeout_seconds=240)
    with (EVIDENCE / f'{agent}-{mode}-{case}-observation.json').open('x') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(result, ensure_ascii=False))
