import importlib.util,json,shutil,tempfile,os,hashlib
from pathlib import Path
repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path('/home/octadim/MyProjects/Team_Workflow_Harness/harness/common/testing/evidence/2026-11-16-execute-process-pull-request-v4');source=repo/'harness/common/inbox/2026-11-14-06-process-pull-request/candidate-v4/comm-process-pull-request'
spec=importlib.util.spec_from_file_location('h',repo/'harness/common/testing/evidence/2026-10-19-instruction-form-selection/validate.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
for mode in ['common','both']:
 with tempfile.TemporaryDirectory(prefix='facts-suite-') as d:
  root=Path(d);start=h.prepare(root,mode,'baseline')
  for parent in ['harness/common/skills','.agents/skills','.claude/skills']:
   target=root/parent/source.name;
   if target.exists():shutil.rmtree(target)
   shutil.copytree(source,target)
  env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
  r=h.run(['/tmp/harness-inbox-20261113-venv/bin/python','-m','pytest',str(root/'harness/common/testing/tests'),'-q','--import-mode=importlib'],cwd=root,env=env)
  with (out/f'prepublication-suite-{mode}.json').open('x') as f:json.dump({'startup':start,'source':h.snapshot(source),'suite':r},f,ensure_ascii=False,indent=2)
  print(mode,r['exit_code'],r['stdout'][-100:],flush=True)
with tempfile.TemporaryDirectory(prefix='facts-project-only-') as d:
 root=Path(d);shutil.copytree(repo/'harness/project',root/'harness/project');before=h.snapshot(root)
 r=h.run(['python3','-B',str(repo/'harness/common/checks/ensure_entrypoint_links.py')],cwd=root)
 record={'result':r,'refused_before_writes':r['exit_code']!=0 and h.snapshot(root)==before}
 with (out/'project-only-negative.json').open('x') as f:json.dump(record,f,ensure_ascii=False,indent=2)
 print('project only',record['refused_before_writes'])
