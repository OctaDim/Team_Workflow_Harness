import json,hashlib,sys
from pathlib import Path
sys.path.insert(0,'/tmp');from native_audit_helpers_20261115 import items
repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=repo/'harness/common/testing/evidence/2026-11-16-execute-process-pull-request-v6';review=json.loads((out/'native-review-v1.json').read_text());selected=[row['file'] for row in review['case_results']];records=[json.loads((out/name).read_text()) for name in selected]
assert len(records)==33,len(records)
paths=[p for p in (repo/'harness/common/skills').rglob('*.md') if p.name!='README.human.md' and 'comm-process-pull-request' not in p.parts]
deps={}
for p in paths:
 rel=str(p.relative_to(repo));sha=hashlib.sha256(p.read_bytes()).hexdigest();assert all(r['before'][rel]==sha for r in records),rel
 deps[rel]={'source':rel,'sha256':sha,'kind':'available canonical dependency'}
for name,p in {'plugin-eval':Path('/home/octadim/.codex/plugins/cache/openai-curated-remote/plugin-eval/0.1.2/scripts/plugin-eval.js'),'skill-creator':Path('/home/octadim/.codex/skills/.system/skill-creator/scripts/quick_validate.py'),'human-filter':repo/'harness/common/scripts/plugin_eval_without_human.mjs','installation-isolation-helper':repo/'harness/common/testing/evidence/2026-10-19-instruction-form-selection/validate.py'}.items():deps[name]={'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'kind':'check runtime'}
with (out/'external-dependencies.json').open('x') as f:json.dump(deps,f,ensure_ascii=False,indent=2)
reads=[]
for p in [out/name for name in selected]:
 r=json.loads(p.read_text())
 if 'completed' not in r:continue
 output='\n'.join(i.get('aggregated_output','') for i in items(r));reads.append({'file':p.name,'external_complete_machine_bodies':[str(s.relative_to(repo)) for s in paths if s.read_text().strip() in output]})
with (out/'actual-external-reads.json').open('x') as f:json.dump(reads,f,ensure_ascii=False,indent=2)
print('dependency manifest',len(deps),'native runs',len(records))
