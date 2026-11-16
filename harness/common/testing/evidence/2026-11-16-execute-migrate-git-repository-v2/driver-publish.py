import hashlib,importlib.util,json,re,subprocess
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v2.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);source=Path(loc['source']);sp=importlib.util.spec_from_file_location('g',repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
assert json.loads((out/'operation-audit.json').read_text())['passed']
gate=json.loads((out/'publication-gate.json').read_text());assert gate['passed'] and gate['source']==g.h.snapshot(source)
for name,digest in {**gate['raw_sha256'],**gate['artifact_sha256']}.items():assert hashlib.sha256((out/name).read_bytes()).hexdigest()==digest,name
review=json.loads((out/'native-review-final.json').read_text());assert review['Codex']=='passed' and len(review['case_results'])==20 and all(r['passed'] for r in review['case_results'])
for mode in ['common','both']:
 r=json.loads((out/f'prepublication-suite-{mode}.json').read_text());assert r['source']==gate['source'] and r['suite']['exit_code']==0 and r['project_preserved'] and r['repeat_startup_unchanged']
assert json.loads((out/'project-only-negative.json').read_text())['refused_before_writes']
for name,e in json.loads((out/'external-dependencies.json').read_text()).items():
 p=Path(e['source']);p=p if p.is_absolute() else repo/p
 assert hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256'],name
patterns=[rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',rb'gh[pousr]_[A-Za-z0-9]{30,}',rb'AKIA[A-Z0-9]{16}',rb'sk-(?:proj-)?[A-Za-z0-9_-]{40,}'];files=[p for p in source.rglob('*') if p.is_file()];counts=sum(sum(len(re.findall(pattern,p.read_bytes())) for pattern in patterns) for p in files);assert counts==0
g.save(out/'source-data-check.json',{'files':len(files),'credential_matches':counts,'scope':'exact full candidate folder; public synthetic identifiers; no source data emitted'})
g.publish(None,source.parent.parent,{source.name:source},out)
