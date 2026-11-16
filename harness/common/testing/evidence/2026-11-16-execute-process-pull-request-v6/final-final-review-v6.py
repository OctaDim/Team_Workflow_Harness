import json,hashlib,importlib.util
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v6.json').read_text());out=Path(loc['out']);source=Path(loc['source']);repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):return json.loads((out/name).read_text())
actual={str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file()};review=read('native-review-v1.json');assert review['source']==actual and len(review['case_results'])==33 and all(r['passed'] for r in review['case_results'])
for name in ['readonly-command-audit.json','preoperation-gate-audit.json','draft-write-audit.json','description-semantics-audit.json','fixture-contract-oracle-audit.json']:assert read(name)['passed'],name
semantic=read('description-semantics-audit.json');assert semantic['source']==actual;expected={r['file'] for r in review['case_results'] if r['kind']=='summary' or (r['kind']=='create1' and r['case']!='unrelated')};assert {r['file'] for r in semantic['case_results']}==expected and len(expected)==6
for row in semantic['case_results']:
 data=read(row['file']);assert row['body_sha256']==hashlib.sha256(data['git_after']['oracle']['host']['prs']['52']['body'].encode()).hexdigest() and row['passed']
raw_hashes={r['file']:sha(out/r['file']) for r in review['case_results']}
for row in review['case_results']:
 data=read(row['file']);assert data['source']==actual==data['candidate'] and data['completed'] and data['exit_code']==0
for mode in ['common','both']:
 suite=read(f'prepublication-suite-{mode}.json');assert suite['source']==actual and suite['suite']['exit_code']==0 and '168 passed' in suite['suite']['stdout']
 install=read(f'local-installation-{mode}.json');assert install['suite']['exit_code']==0
assert read('project-only-negative.json')['refused_before_writes']
for stage in ['profile','start','analyze','explain-budget']:assert read('local-comm-process-pull-request-'+stage+'.json')['exit_code']==0
analysis=json.loads(read('local-comm-process-pull-request-analyze.json')['stdout']);assert analysis['summary']['grade']=='A' and not any(c['status'] in ['fail','error'] for c in analysis['checks']);assert not read('local-comm-process-pull-request-brief.json').get('requiredFixes')
deps=read('external-dependencies.json')
for name,item in deps.items():
 p=Path(item['source']);p=p if p.is_absolute() else repo/p;assert sha(p)==item['sha256'],name
spec=importlib.util.spec_from_file_location('guard',repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard);assert guard.protect()==read('before.json')['protected'];assert read('before.json')['candidates'][source.name]==actual
artifacts=['native-review-v1.json','readonly-command-audit.json','preoperation-gate-audit.json','draft-write-audit.json','description-semantics-audit.json','fixture-contract-oracle-audit.json','external-dependencies.json','context-accounting.json','prepublication-suite-common.json','prepublication-suite-both.json','project-only-negative.json','local-summary.json']
result={'source':actual,'Codex':'passed','modes':{'common':'verified in specified full source/native/behavior scope','both':'verified in specified full source/native/behavior scope'},'Claude':'not run/unverified','overall':'unverified','case_results':review['case_results'],'raw_sha256':raw_hashes,'artifact_sha256':{name:sha(out/name) for name in artifacts},'scope':'Composite final verdict: current exact source, all 33 native scenarios plus operation timing/unresolved-data checks, local/draft effects, all six actual descriptions, formal/install/full canonical suites/project-only/dependency/protected checks. Prior failed versions are not upgraded.'}
with (out/'native-review-final.json').open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print('composite Codex passed: 33/33; current source and all required audits')
