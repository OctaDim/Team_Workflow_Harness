from pathlib import Path
import json,hashlib,tempfile,shutil,subprocess
cfg=json.loads(Path('/tmp/ce-route-install-config-v3.json').read_text());source=Path(cfg['candidate']);e=Path(cfg['evidence']);results=[]
def state(p):return {str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest()for f in p.rglob('*')if f.is_file()and '__pycache__'not in f.parts}
for mode in ['common','both']:
 with tempfile.TemporaryDirectory(prefix='evidence-install-')as tmp:
  dest=Path(tmp)
  for package in ['common']if mode=='common'else ['common','project']:shutil.copytree(source/'harness'/package,dest/'harness'/package)
  for folder in ['.agents/skills','.claude/skills','.claude/rules']:shutil.copytree(source/folder,dest/folder)
  for name in ['AGENTS.md','CLAUDE.md']:shutil.copyfile(source/name,dest/name)
  project=dest/'harness/project';before=state(project);cmd=['python3','-B',str(dest/'harness/common/checks/ensure_entrypoint_links.py'),str(dest)];r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0,r.stderr
  if mode=='both':assert state(project)==before
  else:
   for branch in ['work','harness']:assert(project/'testing/evidence'/branch/'README.human.md').is_file()
   assert 'RAG'not in(project/'INDEX.md').read_text()
  after=state(dest);r2=subprocess.run(cmd,capture_output=True,text=True);assert r2.returncode==0,r2.stderr;assert state(dest)==after
  for skill in cfg['skills']:
   expected=state(dest/'harness/common/skills'/skill)
   for folder in ['.agents/skills','.claude/skills']:assert state(dest/folder/skill)==expected
  if mode=='common':
   skeleton=state(project);(project/'testing/evidence/work/old.log').write_text('removed previous history');shutil.rmtree(project);r3=subprocess.run(cmd,capture_output=True,text=True);assert r3.returncode==0;assert state(project)==skeleton
  shutil.rmtree(dest/'harness/common');blocked_before=state(dest);r4=subprocess.run(['python3','-B',str(source/'harness/common/checks/ensure_entrypoint_links.py'),str(dest)],capture_output=True,text=True);assert r4.returncode==2;assert state(dest)==blocked_before
  results.append({'mode':mode,'startup':'pass','repeat_unchanged':True,'project':'original bytes preserved'if mode=='both'else 'neutral both branches created and recreated without old history','source_native_sets':'equal','project_only':'refused without writes'})
(e/'installation-modes-v3.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
