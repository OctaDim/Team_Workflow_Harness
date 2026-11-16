import hashlib,importlib.util,json,os,re,tempfile
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v2.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);source=Path(loc['source']);target=repo/'harness/common/INDEX.md';sp=importlib.util.spec_from_file_location('g',repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
gate=json.loads((out/'publication-gate.json').read_text());assert gate['passed'] and digest(source)==gate['source_sha256'] and digest(target)==gate['target_before_sha256']
for name,v in {**gate['raw_sha256'],**gate['artifact_sha256']}.items():assert digest(out/name)==v,name
assert g.protect()==json.loads((out/'before.json').read_text())['protected']
for rel,v in json.loads((out/'external-dependencies.json').read_text()).items():
 p=Path(v['source']);p=p if p.is_absolute() else repo/p;assert digest(p)==v['sha256'],rel
patterns=[rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',rb'gh[pousr]_[A-Za-z0-9]{30,}',rb'AKIA[A-Z0-9]{16}',rb'sk-(?:proj-)?[A-Za-z0-9_-]{40,}'];assert not any(re.search(p,source.read_bytes()) for p in patterns)
g.save(out/'source-data-check.json',{'exact_file':str(source),'credential_matches':0,'source_data_emitted':False})
fd,tmp=tempfile.mkstemp(prefix='.publication-',dir=target.parent)
try:
 with os.fdopen(fd,'wb') as f:f.write(source.read_bytes())
 os.chmod(tmp,target.stat().st_mode & 0o777);assert digest(target)==gate['target_before_sha256'];os.replace(tmp,target)
finally:
 if os.path.exists(tmp):os.unlink(tmp)
assert digest(target)==gate['source_sha256'];startup=g.h.run(['python3','-B','harness/common/checks/ensure_entrypoint_links.py'],cwd=repo);assert startup['exit_code']==0;assert g.protect()==json.loads((out/'before.json').read_text())['protected'];visibility=g.h.run(['git','check-ignore','--no-index','harness/common/INDEX.md'],cwd=repo);assert visibility['exit_code']==1 and not visibility['stdout'];g.save(out/'publication.json',{'time':g.now(),'paths':['harness/common/INDEX.md'],'source_sha256':digest(source),'installed_sha256':digest(target),'protected_unchanged':True,'startup':startup,'visibility':visibility})
print('INDEX published after current complete Codex gate.')
