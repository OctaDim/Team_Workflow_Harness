import hashlib,importlib.util,json,os,re,shutil,stat,tempfile
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v3.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);source=Path(loc['source']);skill=Path(loc['skill']);sp=importlib.util.spec_from_file_location('g',repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def protected():
 d=g.protect();d['.claude/rules'].pop('comm-confirm-development-workflow.md',None);return d
def others():return {p:{k:v for k,v in g.h.snapshot(repo/p).items() if not k.startswith(skill.name+'/')} for p in ['harness/common/skills','.agents/skills','.claude/skills']}
gate=json.loads((out/'publication-gate.json').read_text());assert gate['passed'] and gate['rule_sha256']==digest(source) and gate['skill']==g.h.snapshot(skill)
for name,sha in {**gate['selected_raw_sha256'],**gate['artifact_sha256']}.items():assert digest(out/name)==sha,name
before=json.loads((out/'before-other-installed.json').read_text());assert protected()==before['protected'] and others()==before['other_skills']
for v in json.loads((out/'external-dependencies.json').read_text()).values():
 p=Path(v['path']);p=p if p.is_absolute() else repo/p;assert digest(p)==v['sha256'],str(p)
prior=json.loads((out/'before-source.json').read_text());files={repo/rel:source for rel in prior};old={repo/rel:v['sha256'] for rel,v in prior.items()}
for parent in ['harness/common/skills','.agents/skills','.claude/skills']:
 target=repo/parent/skill.name;assert not target.exists(),str(target)
 for p in skill.rglob('*'):
  if p.is_file():files[target/p.relative_to(skill)]=p;old[target/p.relative_to(skill)]=None
patterns=[rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',rb'gh[pousr]_[A-Za-z0-9]{30,}',rb'AKIA[A-Z0-9]{16}',rb'sk-(?:proj-)?[A-Za-z0-9_-]{40,}'];matches=sum(sum(len(re.findall(pat,p.read_bytes())) for pat in patterns) for p in set(files.values()));assert matches==0
g.save(out/'source-data-check.json',{'sources':len(set(files.values())),'destinations':len(files),'credential_matches':matches,'scope':'Exact current rule and complete skill folder, public instructions/human guides only. No source literals emitted.'})
# Stage complete ordinary folders before exposing their SKILL metadata; change
# the two rule pointers only after all three complete skill folders exist.
written=[];staged=[]
try:
 for parent in ['harness/common/skills','.agents/skills','.claude/skills']:
  target=repo/parent/skill.name;g.h.ordinary(target.parent);assert not target.exists()
  stage=Path(tempfile.mkdtemp(prefix='.publication-',dir=target.parent));staged.append((stage,target))
  for src in sorted((p for p in skill.rglob('*') if p.is_file()),key=lambda p:(len(p.relative_to(skill).parts),p.name!='README.human.md',str(p))):
   dest=stage/src.relative_to(skill);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest);os.chmod(dest,stat.S_IMODE(src.stat().st_mode))
  os.chmod(stage,stat.S_IMODE(skill.stat().st_mode));g.h.ordinary(stage);assert g.h.snapshot(stage)==gate['skill']
 assert all(not target.exists() for stage,target in staged)
 assert all(digest(repo/rel)==v['sha256'] for rel,v in prior.items())
 for stage,target in staged:
  assert not target.exists();os.replace(stage,target);written.extend(str(p.relative_to(repo)) for p in target.rglob('*') if p.is_file())
 for rel,v in prior.items():
  dest=repo/rel;assert digest(dest)==v['sha256'];fd,tmp=tempfile.mkstemp(prefix='.publication-',dir=dest.parent)
  try:
   with os.fdopen(fd,'wb') as f:f.write(source.read_bytes())
   os.chmod(tmp,stat.S_IMODE(source.stat().st_mode));assert digest(dest)==v['sha256'];os.replace(tmp,dest)
  finally:
   if os.path.exists(tmp):os.unlink(tmp)
  written.append(rel)
finally:
 for stage,target in staged:
  if stage.exists():shutil.rmtree(stage)
for parent in ['harness/common/skills','.agents/skills','.claude/skills']:
 target=repo/parent/skill.name;assert g.h.snapshot(target)==g.h.snapshot(skill);assert {str(p.relative_to(target)) for p in target.rglob('*')}=={str(p.relative_to(skill)) for p in skill.rglob('*')};g.h.ordinary(target)
assert protected()==before['protected'] and others()==before['other_skills']
startup=g.h.run(['python3','-B','harness/common/checks/ensure_entrypoint_links.py'],cwd=repo);assert startup['exit_code']==0
visibility=g.h.run(['git','check-ignore','--no-index',*written],cwd=repo);assert visibility['exit_code']==1 and not visibility['stdout']
g.save(out/'publication.json',{'time':g.now(),'paths':written,'rule_sha256':digest(source),'skill':g.h.snapshot(skill),'source_native_equal':True,'full_folder_sets_equal':True,'other_owners_preserved':True,'project_entrypoints_preserved':True,'startup':startup,'visibility':visibility})
installed=g.evaluate(out,repo/'harness/common/skills'/skill.name,skill.name,'installed');g.save(out/'installed-assessment-summary.json',installed)
assert protected()==before['protected'] and others()==before['other_skills'];assert g.h.snapshot(repo/'harness/common/skills'/skill.name)==gate['skill']
print('Published current rule + complete skill copies:',len(written),'files; installed assessment',installed['grade'],installed['score'])
