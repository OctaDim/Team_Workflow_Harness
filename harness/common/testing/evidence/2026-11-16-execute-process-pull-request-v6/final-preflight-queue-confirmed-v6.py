import importlib.util,tempfile,json,hashlib,subprocess,ast
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v6.json').read_text());out=Path(loc['out']);repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');c=json.loads((w/'queue-confirmed-v6.json').read_text());sp=importlib.util.spec_from_file_location('h',repo/'harness/common/testing/evidence/2026-10-19-instruction-form-selection/validate.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h)
known=[]
for node in ast.walk(ast.parse(c['files']['fixture.py'])):
 if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='git' and len(node.args)>=3 and all(isinstance(a,ast.Constant) for a in node.args[:3]) and [a.value for a in node.args[:2]]==['commit','-m']:known.append(node.args[2].value.strip())
with tempfile.TemporaryDirectory(prefix='confirmed-queue-') as d:
 root=Path(d)/'project';root.mkdir();h.prepare(root,'both','baseline')
 for rel,body in c['files'].items():p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(body)
 for command in c['setup']:r=h.run(command,cwd=root);assert r['exit_code']==0,r
 classification=json.loads((root/'public-classification.json').read_text());assert len(classification['items'])==1
 for item in classification['items']:
  msg=subprocess.check_output(['git','show','-s','--format=%B',item['commit']],cwd=root);assert hashlib.sha256(msg).hexdigest()==item['sha256'];assert msg.decode().strip() in known
 assert not (root.parent/'seed.txt').exists()
 state=json.loads((root.parent/'host-state.json').read_text());pr=state['prs']['52'];r=h.run(['python3','-B','tools/pr_host.py','merge','--repo','fixture/base','--pr','52','--expected-head',pr['head_sha'],'--expected-base',pr['checks'][0]['base_sha']],cwd=root);assert r['exit_code']==0;result=json.loads(r['stdout']);assert result['state']=='OPEN' and result['queue_state']=='QUEUED' and result['result_sha'] is None
 record={'config_sha256':hashlib.sha256((w/'queue-confirmed-v6.json').read_bytes()).hexdigest(),'classification':classification,'genuine_original_feature_message_matches_fixture_source':True,'sensitive_seed_absent':True,'public_protocol_unchanged':True,'expected_queue_verified':True,'passed':True,'limits':'Classification clarification only; no waiver of content inspection, PR checks/review, head/base guard, or local read-only restrictions.'}
with (out/'queue-confirmed-preflight.json').open('x') as f:json.dump(record,f,ensure_ascii=False,indent=2)
print('confirmed queue fixture preflight passed')
