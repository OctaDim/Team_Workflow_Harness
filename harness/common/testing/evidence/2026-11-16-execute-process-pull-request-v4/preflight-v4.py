import json,importlib.util,tempfile,subprocess,concurrent.futures
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v4.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');sp=importlib.util.spec_from_file_location('h',repo/'harness/common/testing/evidence/2026-10-19-instruction-form-selection/validate.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h);rows=[]
for kind in ['no-choice','ambiguous-choice','create1','merge2','merge3','gate-table','base-race','queue','loss','cleanup-table','delete-race','local-drift','summary','sensitive']:
 c=json.loads((w/(kind+'-v4.json')).read_text())
 with tempfile.TemporaryDirectory(prefix='pr-rpc-preflight-') as d:
  root=Path(d)/'project';root.mkdir();h.prepare(root,'common','baseline')
  for name,text in c['files'].items():p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
  for cmd in c['setup']:r=h.run(cmd,cwd=root);assert r['exit_code']==0,(kind,r)
  help_r=h.run(['python3','-B','tools/pr_host.py','--help'],cwd=root);assert help_r['exit_code']==0,(kind,help_r)
  state=json.loads((root.parent/'host-state.json').read_text());commands=[]
  for pr in state['prs']:
   r=h.run(['python3','-B','tools/pr_host.py','inspect','--repo','fixture/base','--pr',pr],cwd=root);assert r['exit_code']==0,(kind,r);commands.append({'action':'inspect','pr':pr,'ok':True})
  if kind=='create1':
   draft=root.parent/'body.md';draft.write_text(state['prototype']['body']);r=h.run(['python3','-B','tools/pr_host.py','create','--repo','fixture/base','--head-repo','fixture/fork','--head-ref','branch.actor/feature','--base-ref','integration/current','--scope','summary-52','--title-file','wanted title $(touch PATH_INJECTION).txt','--body-file',str(draft)],cwd=root);assert r['exit_code']==0,r;created=json.loads(r['stdout']);assert created['title']==c['expected']['title'] and c['expected']['payload'] in created['body'];commands.append({'action':'create','ok':True})
  if kind in ['merge2','merge3','base-race','queue','loss']:
   pr=state['prs']['52'];r=h.run(['python3','-B','tools/pr_host.py','merge','--repo','fixture/base','--pr','52','--expected-head',pr['head_sha'],'--expected-base',state['prototype']['checks'][0]['base_sha']],cwd=root)
   assert (r['exit_code']==0)==(kind!='base-race'),(kind,r)
   after=json.loads((root.parent/'host-state.json').read_text());p=after['prs']['52'];assert p['state']==('OPEN' if kind in ['queue','base-race'] else 'MERGED')
   commands.append({'action':'merge','expected_status':p['state'],'ok':True})
   if p['state']=='MERGED':
    r=h.run(['python3','-B','tools/pr_host.py','probe','--repo','fixture/base','--sha',p['result_sha']],cwd=root);assert r['exit_code']==0,r;probe=json.loads(r['stdout']);assert all(probe[k] for k in ['summary_contract','base_worker_contract','target_contract'])==(kind!='loss'),(kind,probe)
  if kind=='delete-race':
   pr=state['prs']['52'];r=h.run(['python3','-B','tools/pr_host.py','delete-remote','--repo',pr['head_repo'],'--pr','52','--ref','refs/heads/'+pr['head_ref'],'--expected-sha',pr['head_sha']],cwd=root);assert r['exit_code']!=0 and 'remote SHA mismatch' in r['stdout'],r;commands.append({'action':'conditional deletion race','ok':True})
  before_count=len(json.loads((root.parent/'host-state.json').read_text())['events'])
  def query(_):
   return h.run(['python3','-B','tools/pr_host.py','branch','--repo','fixture/fork','--ref','refs/heads/branch.actor/feature'],cwd=root)
  with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:queries=list(pool.map(query,range(24)))
  assert all(q['exit_code']==0 for q in queries)
  assert len(json.loads((root.parent/'host-state.json').read_text())['events'])==before_count+24
  rows.append({'kind':kind,'syntax_and_read_protocol':'passed','operations':commands});print(kind,'preflight passed',flush=True)
with (Path(loc['out'])/'fixture-preflight.json').open('x') as f:json.dump(rows,f,ensure_ascii=False,indent=2)
