import importlib.util,json,os,tempfile,subprocess
from pathlib import Path
repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');spec=importlib.util.spec_from_file_location('h',repo/'harness/common/testing/evidence/2026-10-19-instruction-form-selection/validate.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
results=[]
for kind in ['positive','race','host-failure']:
 c=json.loads(Path('/tmp/branch-'+kind+'-fixture-v2-20261115.json').read_text())
 with tempfile.TemporaryDirectory(prefix='branch-proxy-preflight-') as d:
  base=Path(d);root=base/'project';root.mkdir();h.prepare(root,'common','baseline')
  for rel,text in c['files'].items():(root/rel).write_text(text)
  for cmd in c['setup']:r=h.run(cmd,cwd=root);assert r['exit_code']==0,r
  wrapper,env=h.isolation(base,root);wrapper=wrapper[:-1]+['--ro-bind',str(base/'shim/git'),'/usr/bin/git','--'];env.update(GIT_CONFIG_GLOBAL='/dev/null',GIT_CONFIG_NOSYSTEM='1',GIT_EXEC_PATH='/usr/lib/git-core')
  truth=json.loads((base/'oracle/truth.json').read_text());reads=[]
  for cmd in [['git','status','--porcelain'],['git','ls-remote','--heads','central']]:
   r=h.run(wrapper+cmd,cwd=root,env=env);assert r['exit_code']==0,r;reads.append(r)
  create=h.run(wrapper+['git','worktree','add','-b','branch.actor/add-agent-summary-tool',str(base/'new-worktree'),truth['target']],cwd=root,env=env)
  assert (create['exit_code']==0)==(kind=='positive'),create
  audit=json.loads((base/'oracle/audit.json').read_text());assert len(audit['attempts'])==1,audit
  if kind=='race':assert audit['race_injected']
  results.append({'kind':kind,'reads':reads,'create':create,'audit':audit})
  print(kind,'proxy passed',flush=True)
out=repo/'harness/common/testing/evidence/2026-11-15-execute-create-git-branch'
with (out/'proxy-preflight-v2.json').open('x') as f:json.dump(results,f,ensure_ascii=False,indent=2)
