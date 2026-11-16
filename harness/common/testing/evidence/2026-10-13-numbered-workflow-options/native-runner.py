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
    spec = importlib.util.spec_from_file_location('probe', ROOT / 'harness/common/testing/evidence/2026-10-11-always-offer-ce-workflows/native-probe-enabled-v2.py')
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)
    probe.REPO, probe.REQUEST, probe.CANDIDATE = ROOT, EVIDENCE, FIXTURE
    probe.PROMPTS = {'menu': 'New task: change one label in an existing text file. Present the applicable workflow choices, request one explicit choice and stop. Answer in Russian. First run the mandatory startup and follow the repository startup instructions. List relevant native catalog skills honestly. Do not read README.human.md bodies. No implementation, publication or commits are authorized.'}
    for suffix in ('events.json', 'response.txt', 'observation.json'):
        assert not (EVIDENCE / f'{agent}-{mode}-menu-{suffix}').exists(), 'Raw evidence is immutable'
    result = probe.probe(agent, mode, 'menu', capture_files=True, timeout_seconds=150)
    with (EVIDENCE / f'{agent}-{mode}-menu-observation.json').open('x') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(result, ensure_ascii=False))
