import base64,hashlib,importlib.util,json,os,re,shutil,stat,tempfile
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v2.json').read_text());repo=Path(loc['repo']);out=Path(loc['out']);req=Path(loc['request']);code=req/'implementation-v2'
spec=importlib.util.spec_from_file_location('g',repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);h=g.h
before=json.loads((out/'before-v2.json').read_text());sourcebefore=json.loads((out/'before-source.json').read_text());native=json.loads((out/'native-review-final.json').read_text());assert native['Codex']=='passed' and len(native['case_results'])==12 and all(r['passed'] for r in native['case_results']);assert native['source']==before['candidates'] and native['implementation']==before['implementation']
sources={n:req/'candidate-v2'/n for n in before['candidates']}
assert g.protect()==before['protected']
for rel,item in sourcebefore.items():assert hashlib.sha256((repo/rel).read_bytes()).hexdigest()==item['sha256'],rel
assert not (repo/'harness/common/testing/tests/test_root_test_discovery.py').exists()
for n,s in sources.items():
 assert h.snapshot(s)==before['candidates'][n]
 for parent in ['harness/common/skills','.agents/skills','.claude/skills']:
  target=repo/parent/n;assert h.snapshot(target)==before['targets'][str(target.relative_to(repo))]
 for p in s.rglob('*.md'):
  if p.name=='README.human.md':continue
  original=repo/'harness/common/skills'/n/p.relative_to(s)
  if str(p.relative_to(s)) not in ['references/testing.md','references/workflow.md']:assert original.read_bytes()==p.read_bytes()
 a=json.loads(json.loads((out/f'candidate-{n}-analyze.json').read_text())['stdout']);assert a['summary']['grade']=='A' and not any(c['status'] in ['fail','error'] for c in a['checks'])
for rel,digest in before['implementation'].items():assert hashlib.sha256((code/rel).read_bytes()).hexdigest()==digest
for mode in ['common','both']:
 r=json.loads((out/f'prepublication-v2-suite-{mode}.json').read_text());assert r['suite']['exit_code']==0 and r['implementation']==before['implementation'] and r['source']==before['candidates'] and r['project_preserved']
assert json.loads((out/'project-only-negative.json').read_text())['refused_before_writes']
deps=json.loads((out/'external-dependencies.json').read_text())
for k,v in deps.items():
 p=Path(v['source']);p=p if p.is_absolute() else repo/p
 assert hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256'],k
raws={r['file']:hashlib.sha256((out/r['file']).read_bytes()).hexdigest() for r in native['case_results']}
# In-process schema-only source scan: never emit matching data.
patterns=[rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',rb'gh[pousr]_[A-Za-z0-9]{30,}',rb'AKIA[A-Z0-9]{16}',rb'sk-(?:proj-)?[A-Za-z0-9_-]{40,}'];matches=0;scanned=[]
for p in [*(p for s in sources.values() for p in s.rglob('*') if p.is_file()),*(code/rel for rel in before['implementation'])]:
 data=p.read_bytes();matches+=sum(len(re.findall(pattern,data)) for pattern in patterns);scanned.append(str(p.relative_to(repo)))
assert matches==0
with (out/'publication-gate.json').open('x') as f:json.dump({'passed':True,'source':before['candidates'],'implementation':before['implementation'],'raw_sha256':raws,'review_sha256':hashlib.sha256((out/'native-review-final.json').read_bytes()).hexdigest(),'data_check':{'files':len(scanned),'credential_matches':matches,'scope':scanned},'Claude':'not run/unverified','Overall':'unverified'},f,ensure_ascii=False,indent=2)
# All code and instruction preconditions have passed before any canonical transfer.
for rel in before['implementation']:
 target=repo/rel;h.ordinary(target.parent)
 old=target.read_bytes() if target.exists() else None;expected=base64.b64decode(sourcebefore[rel]['base64']) if rel in sourcebefore else None;assert old==expected
 fd,tmp=tempfile.mkstemp(prefix='.publication-',dir=target.parent)
 try:
  with os.fdopen(fd,'wb') as f:f.write((code/rel).read_bytes())
  os.chmod(tmp,stat.S_IMODE((code/rel).stat().st_mode));assert (target.read_bytes() if target.exists() else None)==old;os.replace(tmp,target)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
g.publish(None,req,sources,out)
for rel,digest in before['implementation'].items():assert hashlib.sha256((repo/rel).read_bytes()).hexdigest()==digest
assert g.protect()==before['protected']
with (out/'code-publication.json').open('x') as f:json.dump({'source':before['implementation'],'full_copies_equal':True,'protected_unchanged':True,'project_skeleton_unchanged':hashlib.sha256((repo/'harness/common/base/project-skeleton.json').read_bytes()).hexdigest()==sourcebefore['harness/common/base/project-skeleton.json']['sha256']},f,indent=2)
