import json,importlib.util,tempfile,shutil,subprocess,os
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');sp=importlib.util.spec_from_file_location('h',repo/'harness/common/testing/evidence/2026-10-19-instruction-form-selection/validate.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h);rows=[]
for kind in ['method-b','method-a','choice','pr-readonly','dirty','unknown-intent','sql','protected-harness']:
 c=json.loads((w/(kind+'.json')).read_text())
 with tempfile.TemporaryDirectory(prefix='update-preflight-') as d:
  root=Path(d)/'project';root.mkdir();h.prepare(root,'common','baseline')
  for name,s in c['files'].items():p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
  for name,src in c['copy_files'].items():p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,p)
  for cmd in c['setup']:
   r=h.run(cmd,cwd=root);assert r['exit_code']==0,(kind,r)
  for p in (root/'src').glob('*.py'):compile(p.read_text(),str(p),'exec')
  r=h.run(c['probes'][0],cwd=root);assert r['exit_code']==1 and 'Ran 8 tests' in r['stderr'] and 'errors=' not in r['stderr'],(kind,r)
  rows.append({'kind':kind,'checks':r});print(kind,'behavioral RED, 8 tests, no import/errors',flush=True)
with (Path(loc['out'])/'fixture-preflight.json').open('x') as f:json.dump(rows,f,ensure_ascii=False,indent=2)
