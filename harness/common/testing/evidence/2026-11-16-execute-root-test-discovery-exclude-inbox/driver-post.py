import hashlib,importlib.util,json,os,shutil
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v2.json').read_text());repo=Path(loc['repo']);out=Path(loc['out']);spec=importlib.util.spec_from_file_location('g',repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
for name,cmd in [('pytest',[g.PYTHON,'-m','pytest','-q']),('runner',[g.PYTHON,'harness/common/scripts/run_tests.py'])]:
 r=g.h.run(cmd,cwd=repo,env=env,timeout=300);g.save(out/f'installed-root-{name}.json',r);print(name,r['exit_code'],r['stdout'][-500:],r['stderr'][-500:],flush=True);assert r['exit_code']==0
before=json.loads((out/'before-v2.json').read_text());assert g.protect()==before['protected']
g.save(out/'postpublication-final.json',{'passed':True,'root_pytest':'installed-root-pytest.json','root_runner':'installed-root-runner.json','source':json.loads((out/'publication.json').read_text())['source_hashes'],'implementation':before['implementation'],'protected_unchanged':True})
shutil.copyfile(w/'publish.py',out/'driver-publish.py');shutil.copyfile(w/'post.py',out/'driver-post.py')
