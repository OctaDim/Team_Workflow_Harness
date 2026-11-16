import importlib.util,json,os,hashlib,shutil,tempfile
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v2.json').read_text());repo=Path(loc['repo']);req=Path(loc['request']);out=Path(loc['out']);code=Path(loc['code']);sp=importlib.util.spec_from_file_location('guard',repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g);h=g.h
names=['comm-install-harness','comm-process-harness-inbox'];sources={n:req/'candidate-v2'/n for n in names};paths=['pytest.ini','harness/common/testing/pytest.ini','harness/common/scripts/run_tests.py','harness/common/docs/2026-10-06-run-tests.md','harness/common/testing/tests/test_root_test_discovery.py'];old=json.loads((out/'before.json').read_text());assert g.protect()==old['protected'];assert old['candidates']=={n:h.snapshot(p) for n,p in sources.items()}
state=dict(old,implementation={p:hashlib.sha256((code/p).read_bytes()).hexdigest() for p in paths},implementation_version='implementation-v2')
with (out/'before-v2.json').open('x') as f:json.dump(state,f,ensure_ascii=False,indent=2)
for mode in ['common','both']:
 with tempfile.TemporaryDirectory(prefix='discovery-v2-install-') as d:
  root=Path(d);startup=h.prepare(root,mode,'baseline');project=h.snapshot(root/'harness/project')
  for name,source in sources.items():
   for parent in ['harness/common/skills','.agents/skills','.claude/skills']:
    target=root/parent/name;shutil.rmtree(target);shutil.copytree(source,target)
  for rel in paths:
   p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(code/rel,p)
  first=None
  for _ in range(2):
   r=h.run(['python3','-B','harness/common/checks/ensure_entrypoint_links.py'],cwd=root);assert r['exit_code']==0,r
   snap=h.snapshot(root);assert first is None or snap==first;first=snap
  env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1');r=h.run([g.PYTHON,'-m','pytest','.','-q'],cwd=root,env=env,timeout=300);assert r['exit_code']==0,r['stdout'][-4000:]+r['stderr'];assert project==h.snapshot(root/'harness/project')
  with (out/f'prepublication-v2-suite-{mode}.json').open('x') as f:json.dump({'source':state['candidates'],'implementation':state['implementation'],'startup':startup,'project_preserved':True,'suite':r},f,ensure_ascii=False,indent=2)
  print(mode,r['stdout'].strip().splitlines()[-1],flush=True)
