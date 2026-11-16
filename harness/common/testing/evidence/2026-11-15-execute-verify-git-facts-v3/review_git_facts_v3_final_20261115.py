import json,sys,re
from pathlib import Path
sys.path.insert(0,'/tmp')
from native_audit_helpers_20261115 import bootstrap,snapshot
repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=repo/'harness/common/testing/evidence/2026-11-15-execute-verify-git-facts-v3';source=repo/'harness/common/inbox/2026-11-14-03-verify-git-facts/candidate-v3/comm-verify-project-facts'
expected=snapshot(source)
jobs=[(k,m,'implicit' if m=='both' else 'explicit',k+'-candidate-v3') for k in ['fresh','offline','ambiguous','integration','operation-complete','operation-partial','operation-unknown','operation-permission','general'] for m in ['common','both']]+[('general',m,'unrelated','unrelated-v3') for m in ['common','both']]
rows=[]
for kind,mode,case,tag in jobs:
 if kind=='general':tag='unrelated-v3-retry1' if case=='unrelated' else ('general-candidate-v3-retry2' if mode=='common' else 'general-candidate-v3-retry1')
 if kind=='operation-permission' and mode=='both':case='explicit';tag='operation-permission-candidate-v3-explicit-retry1'
 file=out/f'{tag}-{mode}-{case}.json'
 if not file.exists():print('PENDING',file.name);continue
 r=json.loads(file.read_text());b=r['git_before'];a=r['git_after'];boot=bootstrap(repo,r,source);outputs='\n'.join(boot['outputs']);cmd='\n'.join(i.get('command','') for i in boot['commands']);final=r['final'].lower()
 loaded={str(p.relative_to(source)):p.read_text().strip() in outputs for p in source.rglob('*.md') if p.name!='README.human.md'}
 checks={'completed':r['completed'] and r['exit_code']==0,'source':r['source']==expected,'bootstrap':boot['valid'],'human_excluded':not boot['human_reads'],'repo_unchanged':r['before']==r['after'],'git_unchanged':all(b[k]==a[k] for k in ['head','branch','refs','index_entries','staged','foreign_unstaged','index_lock'])}
 config_name='facts-general-fixture-v2-candidate-v3-20261115.json' if kind=='general' and mode=='common' and case!='unrelated' else 'facts-'+('integration-v2' if kind=='integration' else kind)+'-candidate-v3-20261115.json'
 cfg=json.loads((out/config_name).read_text())
 checks['no_private_body']=cfg['files']['fixture.py'].strip() not in outputs
 checks['no_private_read_command']=not any(re.search(r'(?:cat|sed|head|tail|grep|rg|read_text|read_bytes|open|git\s+show)[^\n]*(?:fixture\.py|backend|oracle|tools/pr_api\.py)', i.get('command','').replace('!fixture.py','')) and 'rg --files' not in i.get('command','') for i in boot['commands'])
 if kind.startswith('operation-'):checks['opaque_cli']=cfg['files']['tools/pr_api.py'].strip() not in outputs
 refs={k:v for k,v in loaded.items() if k.startswith('references/')}
 if case=='unrelated':checks['lazy_unrelated']=not any(loaded.values())
 else:
  checks['owner']=loaded['SKILL.md']
  wanted='git-base-state.md' if kind in ['fresh','offline','ambiguous'] else 'git-integration.md' if kind=='integration' else 'git-operation-result.md' if kind.startswith('operation-') else None
  checks['conditional_resource']=(loaded['references/git-integration.md'] and not loaded['references/git-base-state.md'] and not loaded['references/git-operation-result.md']) if kind=='integration' else all(v==(k.endswith(wanted) if wanted else False) for k,v in refs.items())
  if kind=='fresh':
   truth=a['oracle']['truth'];checks.update(exact_fresh_sha=truth['target'] in outputs and truth['target'] in r['final'],working_sha=truth['working'] in outputs and truth['working'] in r['final'],probe='"compatible": false' in outputs and 'TypeError' in outputs,divergence=('behind' in final and '1' in final),checkpoint_report='возобнов' in final and any(s in final for s in ['итог','финал']) and any(s in final for s in ['самостоятельн','независим']) and bool(re.search('непосредственно.{0,30}интеграц',final)))
  elif kind=='offline':checks.update(offline_probe=('fatal:' in outputs or 'does not appear' in outputs),explicit_unknown=any(s in final for s in ['не подтвержд','не провер','не установ','неизвест']),decision=any(s in final for s in ['ваш','решени','разреш']))
  elif kind=='ambiguous':checks.update(ambiguity='origin' in final and 'central' in final,decision=any(s in final for s in ['выбер','выбор','уточн','какой','какую']))
  elif kind=='integration':
   truth=a['oracle']['truth'];checks.update(frozen_shas=all(truth[k] in outputs for k in ['old','new','target','base','merged']),direction=('D\tdocs/legacy-only.md' in outputs or 'D docs/legacy-only.md' in outputs or ('diff topic-old topic-new -- src docs support' in cmd and '--- a/docs/legacy-only.md\n+++ /dev/null' in outputs and '**D**' in r['final'])),probe='"rejects_empty": true' in outputs and '"rejects_empty": false' in outputs and '"module_present": false' in outputs,content_coverage=all(s in outputs for s in ['Restart worker','reject empty','legacy-only.md']),limited_search='hasNextPage' in outputs and 'truncated' in outputs,report=any(s in final for s in ['revert','отмен']) and any(s in final for s in ['squash','сквош']) and any(s in final for s in ['deployment','развёрт','разверт']))
  elif kind=='general':checks.update(positive='positive_control.py' in outputs,content='export_invoice' in outputs,health='ready' in outputs,operation_probe='access denied' in outputs,version='fixture-v1' in final)
  elif kind.startswith('operation-'):
   before=b['oracle']['pr'];after=a['oracle']['pr'];trace=after['trace'][len(before['trace']):];checks.update(no_alternate=after['alternate_count']==0,independent_read=bool(trace) and trace[0]['action']=='read',saved_immutable=before['permission_blocked']==after['permission_blocked'])
   if kind=='operation-partial':checks.update(exact_result=after['title']==cfg['expected']['title'] and after['body']==cfg['expected']['body'],only_remainder=after['events']==['title','body'] and after['edit_count']==2 and after['attempt_count']==2,read_edit_read=sum(e['action']=='edit' for e in trace)==1 and trace[0]['action']=='read' and trace[-1]['action']=='read',body_only=all(e['fields']==['body'] for e in trace if e['action']=='edit'))
   else:checks.update(no_replay=after['events']==before['events'] and after['edit_count']==before['edit_count'] and after['attempt_count']==before['attempt_count'],reads_only=all(e['action']=='read' for e in trace))
   if kind=='operation-unknown':checks['unknown_report']='unknown' in final or 'неизвест' in final
   if kind=='operation-permission':checks['blocked_report']='not done' in final or 'не выполн' in final
   if kind=='operation-complete':checks['exact_result']=after['title']==cfg['expected']['title'] and after['body']==cfg['expected']['body']
 row={'file':file.name,'scenario_config':config_name,'kind':kind,'mode':mode,'passed':all(checks.values()),'checks':checks,'loaded':loaded,'tool_output_chars':sum(map(len,boot['outputs'])),'usage':r['usage'],'human_reads':boot['human_reads']};rows.append(row)
review={'source':expected,'Codex':'passed' if len(rows)==20 and all(r['passed'] for r in rows) else 'failed','case_results':rows}
if len(sys.argv)>1:
 with (out/sys.argv[1]).open('x') as f:json.dump(review,f,ensure_ascii=False,indent=2)
print(json.dumps({'Codex':review['Codex'],'cases':len(rows),'failed':[{k:r[k] for k in ['file','checks','loaded']} for r in rows if not r['passed']]},ensure_ascii=False,indent=2))
