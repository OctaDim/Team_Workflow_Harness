import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path('/home/octadim/MyProjects/Multi_User_RAG_Assist_System')
E = ROOT / 'harness/common/testing/evidence/2026-10-16-application-config-git'
C = ROOT / 'harness/common/inbox/2026-10-16-application-config-git/candidate'
NAME = 'comm-separate-application-config'
RULE = 'comm-application-config-git.md'
spec = importlib.util.spec_from_file_location('publication_native', E/'native-validation-v3.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)
record = E / 'publication-result-v1-20261016.json'
assert not record.exists()
summary = json.loads((E/'native-publication-summary-v1-20261016.json').read_text())
assert len(summary['scenarios']) == 6 and all(r['status']=='passed' for r in summary['scenarios'])
pre = json.loads((E/'prepublication-v1-20261016.json').read_text())
assert pre['records'][-1]['status'] == 'passed'
baseline = json.loads((E/'publication-baseline-v1-20261016.json').read_text())
def verify_protected():
    for group in ('protected_files','prior_evidence'):
        for p,h in baseline[group].items():
            assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h, p

native.ordinary(ROOT/'harness')
verify_protected()
sources = [(C/'rules'/RULE, ROOT/'harness/common/rules'/RULE),
           (C/'rules'/RULE, ROOT/'.claude/rules'/RULE)]
folders = [(C/'skills'/NAME, ROOT/p/NAME) for p in
           ('harness/common/skills','.agents/skills','.claude/skills')]
for src,dst in sources+folders:
    for part in (dst,*dst.parents):
        assert not part.is_symlink(), str(part)
    assert not dst.exists(), f'Unexpected existing target: {dst}'
expected = {'rules/'+RULE:'f83eb86bea352f1cdc487d1c28c9075af132b8b8adad8a8ec0de1aaefac40333',
            'skills/'+NAME+'/SKILL.md':'e9c43d44cb7a3714f7a18e71587af732ef72cf009d1e04957261506335732af0'}
for p,h in expected.items():
    assert hashlib.sha256((C/p).read_bytes()).hexdigest() == h
for src,dst in folders:
    shutil.copytree(src,dst)
for src,dst in sources:
    with dst.open('xb') as f:
        f.write(src.read_bytes())
for src,dst in folders:
    assert native.state(src) == native.state(dst)
for src,dst in sources:
    assert src.read_bytes() == dst.read_bytes()
records = []
def run(command, expected=0):
    r = subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    records.append(dict(command=command,exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr))
    assert r.returncode == expected, (command,r.stderr,r.stdout)
    return r
for index in range(2):
    run(['python3','-B','harness/common/checks/ensure_entrypoint_links.py'])
    verify_protected()
run([str(ROOT/'backend/.venv/bin/python'),'-B','-m','pytest','-c','harness/common/testing/pytest.ini',
     'harness/common/testing/tests/test_rule_copies.py::TestRuleCopies::test_installed_rule_copies',
     'harness/common/testing/tests/test_human_guide_reader.py',
     'harness/common/testing/tests/test_skills_first_knowledge.py','-q','-p','no:cacheprovider'])
paths = [str(dst.relative_to(ROOT)) for _,dst in sources]
paths += [str(p.relative_to(ROOT)) for _,dst in folders for p in dst.rglob('*') if p.is_file()]
for p in paths:
    run(['git','check-ignore','--no-index','--',p], expected=1)
run(['git','diff','--check'])
native.ordinary(ROOT/'harness')
for _,p in folders+sources:
    native.ordinary(p)
verify_protected()
result = dict(timestamp=datetime.now(ZoneInfo('Europe/Minsk')).isoformat(),version='v1',
              status='published',hashes=expected,paths=paths,checks=records,
              full_candidate_native_equality='passed',protected_file_count=len(baseline['protected_files']),
              prior_evidence_unchanged='passed',codex=summary['codex'],
              claude={'check':'skip','status':'unverified'},overall='unverified')
with record.open('x') as f:
    json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({'status':'published','paths':paths,'checks':len(records)},ensure_ascii=False))
