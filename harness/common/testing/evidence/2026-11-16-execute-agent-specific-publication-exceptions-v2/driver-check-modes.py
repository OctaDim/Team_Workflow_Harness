import importlib.util,json,os,shutil,tempfile
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/('location-v2.json' if (w/'location-v2.json').exists() else 'location.json')).read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);source=Path(loc['source']);sp=importlib.util.spec_from_file_location('g',repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
for mode in ['common','both']:
 with tempfile.TemporaryDirectory(prefix='publication-gate-mode-') as d:
  root=Path(d);startup=g.h.prepare(root,mode,'baseline');project=g.h.snapshot(root/'harness/project');shutil.copyfile(repo/'pytest.ini',root/'pytest.ini')
  for parent in ['harness/common/skills','.agents/skills','.claude/skills']:
   target=root/parent/source.name
   if target.exists():shutil.rmtree(target)
   shutil.copytree(source,target)
  previous=None
  for _ in range(2):
   r=g.h.run(['python3','-B','harness/common/checks/ensure_entrypoint_links.py'],cwd=root);assert r['exit_code']==0
   now=g.h.snapshot(root);assert previous is None or now==previous;previous=now
  r=g.h.run([g.PYTHON,'-m','pytest','-q'],cwd=root,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'),timeout=300);assert r['exit_code']==0,r['stdout'][-1500:]+r['stderr'];assert project==g.h.snapshot(root/'harness/project')
  g.save(out/f'prepublication-suite-{mode}.json',{'source':g.h.snapshot(source),'suite':r,'startup':startup,'project_preserved':True,'repeat_startup_unchanged':True});print(mode,r['stdout'].splitlines()[-1],flush=True)
with tempfile.TemporaryDirectory(prefix='publication-gate-project-only-') as d:
 root=Path(d);shutil.copytree(repo/'harness/project',root/'harness/project');prior=g.h.snapshot(root);r=g.h.run(['python3','-B',str(repo/'harness/common/checks/ensure_entrypoint_links.py')],cwd=root);assert r['exit_code']!=0 and prior==g.h.snapshot(root);g.save(out/'project-only-negative.json',{'refused_before_writes':True,'result':r})
