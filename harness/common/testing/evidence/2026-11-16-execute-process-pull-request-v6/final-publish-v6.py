import hashlib,json,subprocess
from pathlib import Path
repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness')
out=repo/'harness/common/testing/evidence/2026-11-16-execute-process-pull-request-v6'
source=repo/'harness/common/inbox/2026-11-14-06-process-pull-request/candidate-v6/comm-process-pull-request'
final=json.loads((out/'native-review-final.json').read_text());assert final['Codex']=='passed'
for name,digest in {**final['raw_sha256'],**final['artifact_sha256']}.items():assert hashlib.sha256((out/name).read_bytes()).hexdigest()==digest,name
review=json.loads((out/'native-review-v1.json').read_text());actual={str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*') if p.is_file()}
assert review['source']==actual==final['source'] and review['Codex']=='passed'
assert len(review['case_results'])==33 and all(row['passed'] for row in review['case_results'])
for mode in ('common','both'):
 r=json.loads((out/f'prepublication-suite-{mode}.json').read_text());assert r['source']==actual and r['suite']['exit_code']==0
assert json.loads((out/'project-only-negative.json').read_text())['refused_before_writes']
assert json.loads((out/'readonly-command-audit.json').read_text())['passed']
assert json.loads((out/'preoperation-gate-audit.json').read_text())['passed']
assert json.loads((out/'fixture-contract-oracle-audit.json').read_text())['passed']
assert json.loads((out/'draft-write-audit.json').read_text())['passed']
semantic=json.loads((out/'description-semantics-audit.json').read_text());assert semantic['passed'] and semantic['source']==actual
assert len(semantic['case_results'])==6
expected_descriptions={row['file'] for row in review['case_results'] if row['kind']=='summary' or (row['kind']=='create1' and row['case']!='unrelated')}
assert {row['file'] for row in semantic['case_results']}==expected_descriptions
assert all(row['passed'] for row in semantic['case_results'])
for row in semantic['case_results']:
 raw=json.loads((out/row['file']).read_text());assert hashlib.sha256(raw['git_after']['oracle']['host']['prs']['52']['body'].encode()).hexdigest()==row['body_sha256']
deps=json.loads((out/'external-dependencies.json').read_text())
for name,entry in deps.items():
 p=Path(entry['source']);p=p if p.is_absolute() else repo/p
 assert hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256'],name
subprocess.run(['python3','-B',str(repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py'),'publish','2026-11-14-06-process-pull-request','--candidate','candidate-v6','--out-name',out.name],cwd=repo,check=True)
