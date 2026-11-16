import json,hashlib,importlib.util,tempfile,subprocess
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v6.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);sp=importlib.util.spec_from_file_location('h',repo/'harness/common/testing/evidence/2026-10-19-instruction-form-selection/validate.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h);rows=[]
for kind in ['merge2','merge3','loss']:
 cfg=json.loads((w/(kind+'-v6.json')).read_text())
 with tempfile.TemporaryDirectory(prefix='pr-contract-oracle-') as d:
  root=Path(d)/'project';root.mkdir();h.prepare(root,'common','baseline')
  for name,text in cfg['files'].items():p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
  for cmd in cfg['setup']:assert h.run(cmd,cwd=root)['exit_code']==0
  state=json.loads((root.parent/'host-state.json').read_text());pr=state['prs']['52'];target=pr['checks'][0]['base_sha'];args=['python3','-B','tools/pr_host.py'];r=h.run(args+['merge','--repo','fixture/base','--pr','52','--expected-head',pr['head_sha'],'--expected-base',target],cwd=root);assert r['exit_code']==0
  state=json.loads((root.parent/'host-state.json').read_text());pr=state['prs']['52'];sha=pr['result_sha'];bare=state['repos']['fixture/base']
  def git(*args):return subprocess.run(['git','--git-dir',bare,*args],capture_output=True,text=True)
  contracts={};digests={}
  for path,name,argument,wanted in [('src/summary.py','summarize',[7],[7]),('src/worker.py','worker_base',None,'base-v2'),('src/target.py','target_contract',None,42)]:
   result=git('show',sha+':'+path)
   if result.returncode:contracts[name]=False;continue
   namespace={};exec(compile(result.stdout,'trusted_synthetic_fixture','exec'),namespace);value=namespace[name](argument) if argument is not None else namespace[name]();contracts[name]=value==wanted;digests[path]=hashlib.sha256(result.stdout.encode()).hexdigest()
  probe=h.run(args+['probe','--repo','fixture/base','--sha',sha],cwd=root);assert probe['exit_code']==0;actual=json.loads(probe['stdout']);reported={key:actual[field] for key,field in [('summarize','summary_contract'),('worker_base','base_worker_contract'),('target_contract','target_contract')]};assert reported==contracts
  tree=git('rev-parse',sha+'^{tree}').stdout.strip();assert tree==state['loss_tree' if kind=='loss' else 'combined_tree'];assert git('rev-list','--parents','-n','1',sha).stdout.strip().split()[1:]==[target]
  rows.append({'kind':kind,'config_sha256':hashlib.sha256((w/(kind+'-v6.json')).read_bytes()).hexdigest(),'result_sha':sha,'parent':target,'actual_tree':tree,'source_sha256':digests,'executed_contracts':contracts,'public_probe_equals_real_execution':reported==contracts,'passed':all(contracts.values()) if kind!='loss' else contracts=={'summarize':False,'worker_base':False,'target_contract':True}})
assert all(r['passed'] for r in rows)
with (out/'fixture-contract-oracle-audit.json').open('x') as f:json.dump({'passed':True,'case_results':rows,'limits':'Public probe executes summary; worker/target public booleans use presence. Independent parent executes all three exact functions on real merged commits and checks actual tree/parent, proving public probe sound for every merge shape used here. Native candidate, public fixture code and configs unchanged.'},f,ensure_ascii=False,indent=2)
print('independent fixture contracts passed',len(rows))
