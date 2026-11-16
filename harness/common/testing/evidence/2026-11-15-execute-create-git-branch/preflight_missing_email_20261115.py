import importlib.util,json,tempfile,os
from pathlib import Path
repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');sp=importlib.util.spec_from_file_location('h',repo/'harness/common/testing/evidence/2026-10-19-instruction-form-selection/validate.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h);c=json.loads(Path('/tmp/branch-missing-prefix-fixture-v3-20261115.json').read_text())
with tempfile.TemporaryDirectory(prefix='missing-email-preflight-') as d:
 base=Path(d);root=base/'project';root.mkdir();h.prepare(root,'common','baseline')
 for name,text in c['files'].items():(root/name).write_text(text)
 for cmd in c['setup']:r=h.run(cmd,cwd=root);assert r['exit_code']==0,r
 wrapper,env=h.isolation(base,root);home=base/'neutral-home';home.mkdir();env.update(HOME=str(home),GIT_CONFIG_GLOBAL='/dev/null',GIT_CONFIG_NOSYSTEM='1',GIT_EXEC_PATH='/usr/lib/git-core');env.pop('EMAIL',None)
 for k in list(env):
  if k.startswith('GIT_AUTHOR_') or k.startswith('GIT_COMMITTER_'):env.pop(k)
 wrapper=wrapper[:-1]+['--ro-bind',str(base/'shim/git'),'/usr/bin/git','--'];r=h.run(wrapper+['git','var','GIT_AUTHOR_IDENT'],cwd=root,env=env);assert r['exit_code']!=0 and not r['stdout'],r
 with (repo/'harness/common/testing/evidence/2026-11-15-execute-create-git-branch/missing-email-preflight-v3.json').open('x') as f:json.dump(r,f,ensure_ascii=False,indent=2)
 print('effective identity unavailable: confirmed',r['exit_code'])
