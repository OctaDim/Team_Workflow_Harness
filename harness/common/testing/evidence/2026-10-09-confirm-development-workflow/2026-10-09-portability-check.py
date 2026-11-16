from pathlib import Path
import hashlib
import json
import runpy
import shutil
import subprocess
import tempfile

ROOT = Path('/home/octadim/MyProjects/Multi_User_RAG_Assist_System')
EVIDENCE = ROOT / 'harness/common/testing/evidence/2026-10-09-confirm-development-workflow'
RULE = ROOT / 'harness/common/inbox/2026-10-09-confirm-development-workflow/comm-confirm-development-workflow.md'
check_copies = runpy.run_path(str(ROOT / 'harness/common/testing/tests/test_rule_copies.py'))['check_rule_copies']

def state(folder):
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.rglob('*') if p.is_file()}

results = []
for mode in ['common-only', 'common+project']:
    with tempfile.TemporaryDirectory(prefix='workflow-portability-') as directory:
        root = Path(directory)
        common = root / 'harness/common'
        shutil.copytree(ROOT / 'harness/common', common,
                        ignore=shutil.ignore_patterns('inbox', 'evidence', '__pycache__'))
        if mode == 'common+project':
            shutil.copytree(ROOT / 'harness/project', root / 'harness/project')
        project_before = state(root / 'harness/project')
        for base in ['.agents/skills', '.claude/skills']:
            shutil.copytree(common / 'skills', root / base)
        shutil.copytree(common / 'rules', root / '.claude/rules')
        for folder in [common / 'rules', root / '.claude/rules']:
            shutil.copyfile(RULE, folder / RULE.name)
        command = ['python3', '-B', str(common / 'checks/ensure_entrypoint_links.py'), str(root)]
        startup = subprocess.run(command, capture_output=True, text=True)
        assert startup.returncode == 0, startup.stderr
        assert (root / 'harness/project/START.md').is_file()
        if mode == 'common+project':
            assert state(root / 'harness/project') == project_before
        else:
            assert 'RAG' not in (root / 'harness/project/START.md').read_text()
        before_repeat = state(root)
        repeat = subprocess.run(command, capture_output=True, text=True)
        assert repeat.returncode == 0, repeat.stderr
        assert state(root) == before_repeat
        assert check_copies(root) == 8
        agents = (root / 'AGENTS.md').read_text()
        assert '.claude/rules/' in agents and 'README.human.md' in agents
        assert agents.index('harness/common/START.md') < agents.index('.claude/rules/') < agents.index('harness/common/INDEX.md')
        assert (root / '.claude/rules' / RULE.name).read_bytes() == RULE.read_bytes()
        results.append({'mode': mode, 'startup': 'pass', 'repeat_no_changes': 'pass',
                        'project': 'preserved byte-for-byte' if project_before else 'neutral created',
                        'canonical_rule_copies': 8, 'Codex_rules_pointer': 'pass',
                        'candidate_copy_equal': 'pass'})
with tempfile.TemporaryDirectory(prefix='workflow-project-only-') as directory:
    root = Path(directory)
    (root / 'harness/project/rules').mkdir(parents=True)
    try:
        check_copies(root)
    except ValueError as error:
        assert 'common' in str(error)
        results.append({'mode': 'project-only', 'refusal': 'pass', 'reason': str(error)})
    else:
        raise AssertionError('project-only incorrectly accepted')
report = {'candidate_sha256': hashlib.sha256(RULE.read_bytes()).hexdigest(),
          'checks': results, 'scope': 'structural installation checks; no native behavior claim'}
(EVIDENCE / '2026-10-09-portability.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
