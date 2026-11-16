import hashlib,json,subprocess
from pathlib import Path
repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness')
out=repo/'harness/common/testing/evidence/2026-11-15-execute-git-work-and-message-safety'
source=repo/'harness/common/inbox/2026-11-14-02-git-work-and-message-safety/candidate/comm-commit-task-stages'
review=json.loads((out/'native-review-v1.json').read_text());actual={str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*') if p.is_file()}
assert review['source']==actual and review['Codex']=='passed'
assert len(review['case_results'])==18 and all(row['passed'] for row in review['case_results'])
for mode in ('common','both'):
 r=json.loads((out/f'prepublication-suite-{mode}.json').read_text());assert r['source']==actual and r['suite']['exit_code']==0
assert json.loads((out/'project-only-negative.json').read_text())['refused_before_writes']
deps=json.loads((out/'external-dependencies.json').read_text())
for name,entry in deps.items():
 p=Path(entry['source']);p=p if p.is_absolute() else repo/p
 assert hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256'],name
subprocess.run(['python3','-B',str(repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py'),'publish','2026-11-14-02-git-work-and-message-safety','--out-name',out.name],cwd=repo,check=True)
