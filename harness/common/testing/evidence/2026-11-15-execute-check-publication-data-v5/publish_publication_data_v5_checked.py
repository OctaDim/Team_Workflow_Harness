import hashlib, importlib.util, json, subprocess
from pathlib import Path

repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness')
out=repo/'harness/common/testing/evidence/2026-11-15-execute-check-publication-data-v5'
source=repo/'harness/common/inbox/2026-11-14-01-check-publication-data/candidate-v5/comm-check-publication-data'
review=json.loads((out/'native-review-v5.json').read_text())
actual={str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*') if p.is_file()}
assert review['source']==actual, 'The reviewed candidate changed'
assert review['Codex']=='passed', 'Codex acceptance is incomplete'
assert len(review['case_results'])==14 and all(row['passed'] for row in review['case_results'])
assert len(review['scope_results'])==5 and all(row['passed'] for row in review['scope_results'])
for mode in ('common','both'):
 record=json.loads((out/f'prepublication-suite-{mode}.json').read_text())
 assert record['source']==actual and record['suite']['exit_code']==0
assert json.loads((out/'project-only-negative.json').read_text())['refused_before_writes']
subprocess.run(['python3','-B',str(repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py'),'publish','2026-11-14-01-check-publication-data','--candidate','candidate-v5','--out-name',out.name],cwd=repo,check=True)
