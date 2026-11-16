import hashlib,importlib.util,json,subprocess,tempfile
from pathlib import Path
from fixture import build
w=Path(__file__).parent;loc=json.loads((w/'location-v2.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);sp=importlib.util.spec_from_file_location('h',repo/'harness/common/testing/evidence/2026-10-19-instruction-form-selection/validate.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h);rows=[]
for case in ['mirror-risk','receiver-blocked']:
 with tempfile.TemporaryDirectory(prefix='migrate-fixture-preflight-') as d:
  root=Path(d)/'project';root.mkdir();h.prepare(root,'common','baseline');truth,task,control=build(root,case);dest=Path(truth['destination']);old=Path(truth['old']);a=subprocess.check_output(['git','--git-dir='+str(old),'rev-parse','refs/heads/trunk'],text=True).strip();b=subprocess.check_output(['git','--git-dir='+str(dest),'rev-parse','refs/heads/trunk'],text=True).strip();assert a!=b;assert subprocess.run(['git','--git-dir='+str(dest),'cat-file','-e',b+'^{commit}']).returncode==0;refs=subprocess.check_output(['git','for-each-ref','--format=%(refname)'],cwd=root,text=True);assert 'destination-seed' not in refs;destrefs=subprocess.check_output(['git','--git-dir='+str(dest),'for-each-ref','--format=%(refname)'],text=True);assert 'refs/heads/destination-seed' in destrefs;rows.append({'case':case,'destination_object_present':True,'protected_trunk_differs':True,'destination_only_ref_present':True,'source_seed_removed':True})
with (out/'destination-fixture-preflight.json').open('x') as f:json.dump({'passed':True,'fixture_sha256':hashlib.sha256((w/'fixture.py').read_bytes()).hexdigest(),'cases':rows},f,indent=2)
print('destination fixture preflight passed')
