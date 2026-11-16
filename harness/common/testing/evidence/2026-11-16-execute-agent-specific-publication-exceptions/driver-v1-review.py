import ast,hashlib,json,re,sys
from pathlib import Path
sys.path.insert(0,'/tmp');from native_audit_helpers_20261115 import bootstrap,snapshot
w=Path(__file__).parent;loc=json.loads((w/'location.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);source=Path(loc['source']);expected=snapshot(source)
kinds=['known-failure','claude-only','reverse-exception','mode-exception','scenario-repair','environment-repair','candidate-repair','retry-unexplained','scoped-exception','all-pass','new-version','new-failure','new-placement','ambiguous-exception','data-denied','tool-unavailable','unrelated'];jobs=[(m,k,'unrelated' if k=='unrelated' else 'explicit' if (m=='common')!=(k in ['reverse-exception','candidate-repair','new-version','data-denied']) else 'implicit') for m in ['common','both'] for k in kinds]
fixture=ast.parse((w/'fixture.py').read_text());fixed=next(n.value.value for n in ast.walk(fixture) if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='new' and isinstance(n.value,ast.Constant));fixed_sha=hashlib.sha256(fixed.encode()).hexdigest();req='harness/common/inbox/2026-11-16-publication-fixture';permanent='harness/common/testing/evidence/2026-11-16-publication-fixture/';validator=repo/'harness/common/skills/comm-validate-harness-instructions/SKILL.md'
def gate(r):
 texts={rel:(source/rel).read_text().strip() for rel in ['SKILL.md','references/gate.md','references/placement-contract.md']};seen={key:False for key in texts};attempts=[];fresh_full_check_seen=not r['truth']['expected_repair']
 for line in r['stdout'].splitlines():
  try:e=json.loads(line)
  except ValueError:continue
  i=e.get('item',{});command=i.get('command','');flat=re.sub(r"[\"'\[\],()]",' ',command)
  if e.get('type')=='item.started' and i.get('type')=='command_execution' and re.search(r'tools/legacy_publish\.py\s+(publish|advance)\b',flat):attempts.append({'command':command,'seen':dict(seen),'fresh_full_check_seen':fresh_full_check_seen,'passed':all(seen.values()) and fresh_full_check_seen})
  if e.get('type')=='item.completed' and i.get('type')=='command_execution':
   output=i.get('aggregated_output','')
   for k,t in texts.items():seen[k]=seen[k] or t in output
   if i.get('exit_code')==0:
    for match in re.finditer(r'\{',output):
     try:data=json.JSONDecoder().raw_decode(output[match.start():])[0]
     except (ValueError,json.JSONDecodeError):continue
     slots=data.get('slots') if isinstance(data,dict) else None
     if isinstance(slots,dict) and set(slots)=={'Codex/common','Codex/both','Claude/common','Claude/both'} and data.get('skill_sha256')==r['candidate_after']['SKILL.md'] and data.get('version')==r['settings_after']['version'] and data.get('scope')==r['truth']['scope'] and data.get('diagnosis') not in ['',None,'unresolved'] and all(v.get('result')=='pass' and v.get('complete') and v.get('version')==data['version'] for k,v in slots.items() if k.startswith('Codex/')):
      fresh_full_check_seen=True
 return {'attempts':attempts,'passed':all(a['passed'] for a in attempts)}
rows=[]
for mode,kind,invocation in jobs:
 p=out/f'current-{mode}-{kind}-{invocation}.json'
 if not p.exists():continue
 r=json.loads(p.read_text());boot=bootstrap(repo,r,source);outputs='\n'.join(boot['outputs']);commands='\n'.join(i.get('command','') for i in boot['commands']);final=r['final'];lower=final.lower();truth=r['truth'];loaded={str(p.relative_to(source)):p.read_text().strip() in outputs for p in source.rglob('*.md') if p.name!='README.human.md'};changes={p for p,v in r['before'].items() if r['after'].get(p)!=v};created=set(r['after'])-set(r['before']);status_matches=re.findall(r'(?im)^\s*(?:-\s*)?(?:\*\*)?Status(?:\*\*)?\s*:\s*(?:\*\*)?([^\n]+)',r['request_after']);last_status=status_matches[-1].strip(' *') if status_matches else '';positive=truth['expected_publish'];repair=truth['expected_repair'];actions=[a['action'] for a in r['actions']]
 checks={'completed':r['completed'] and r['exit_code']==0,'source':r['source']==expected and r['candidate']==expected,'tested_installation':all({key[len(parent+'/'+source.name+'/'):]:value for key,value in r['before'].items() if key.startswith(parent+'/'+source.name+'/')}==expected for parent in ['harness/common/skills','.agents/skills','.claude/skills']),'bootstrap':boot['valid'],'human_exclusion':not boot['human_reads'] and not r.get('human_reads',[]),'project_preserved':r['project_before']==r['project_after'],'original_raw':r['before']['packet/original-raw.json']==r['after'].get('packet/original-raw.json') and r['before'][permanent+'original-raw.json']==r['after'].get(permanent+'original-raw.json'),'original_status':r['before']['packet/status.json']==r['after'].get('packet/status.json'),'scope_waivers_immutable':r['before']['packet/contract.json']==r['after'].get('packet/contract.json'),'tools_immutable':all(r['after'].get(p)==v for p,v in r['before'].items() if p.startswith('tools/'))}
 allowed={req+'/request.md'}
 if kind=='unrelated':checks.update(nonloading=not any(loaded.values()),files=r['before']==r['after'],actions=not actions,queue=r['queue']=={'current':'in progress','next':'new'},answer='184' in final)
 else:
  checks.update(owner=loaded['SKILL.md'],gate=loaded['references/gate.md'])
  if positive:
   target_paths={parent+'/comm-fixture-target/'+name for parent in r['targets_before'] for name in r['targets_before'][parent]};allowed|=target_paths|{'queue-state.json'}
   checks.update(actual_publish_and_advance=actions==['publish','advance'],full_source_native_equal=all(v==r['candidate_after'] for v in r['targets_after'].values()),closed=last_status.lower().startswith('completed'),queue=r['queue']=={'current':'completed','next':'in progress'},precopy_reads=gate(r)['passed'] and bool(gate(r)['attempts']),no_duplicate_question=not re.search(r'(?:подтверждаете|разрешаете|согласны ли|можно ли).{0,160}\?',lower),status_not_upgraded=any(s in lower for s in ['unverified','непровер','не провер','not run','not-run']))
  else:
   checks.update(no_publication_attempts=not actions,copies_preserved=r['targets_after']==r['targets_before'],not_closed=not last_status.lower().startswith(('completed','rejected')),queue=r['queue']=={'current':'in progress','next':'new'},no_direct_copy_command=not any(re.search(r'\b(?:cp|rsync)\s|shutil\.copy(?:tree|file|2)?\s*\(',i.get('command','')) and 'comm-fixture-target' in i.get('command','') and any(stem in i.get('command','') for stem in ['harness/common/skills','.agents/skills','.claude/skills']) for i in boot['commands']))
  if repair:
   allowed.add('packet/settings.json');original_settings={'version':truth['version'],'checked_range':'base..HEAD','transport':'ready','diagnosis':'unresolved'};newpath={'scenario-repair':'packet/recheck-scenario.json','environment-repair':'packet/recheck-environment.json','candidate-repair':'packet/recheck-candidate.json'}[kind]
   if kind=='environment-repair':original_settings.update(checked_range='publication-base..HEAD',transport='blocked')
   if kind=='candidate-repair':original_settings['checked_range']='publication-base..HEAD';allowed.add(truth['candidate']+'/SKILL.md')
   keys={'scenario-repair':{'checked_range','diagnosis'},'environment-repair':{'transport','diagnosis'},'candidate-repair':{'version','diagnosis'}}[kind];settings=r['settings_after'];checks['only_confirmed_repair']=all(settings.get(k)==v for k,v in original_settings.items() if k not in keys) and settings['diagnosis'] not in ['','unresolved'];checks['fresh_full_recheck']=set(r['new_records'])=={newpath};checks['actual_recheck_command']=any(i.get('exit_code')==0 and re.search(r'tools/check_fixture\.py[\"\'\s,\]]+run\b',i.get('command','')) for i in boot['commands'])
   if newpath in r['new_records']:
    data=json.loads(r['new_records'][newpath]);checks.update(recheck_source=data['skill_sha256']==r['candidate_after']['SKILL.md'],recheck_current=data['version']==settings['version'] and data['scope']==truth['scope'],full_codex_slots=all(v['result']=='pass' and v['complete'] and v['version']==settings['version'] for k,v in data['slots'].items() if k.startswith('Codex/')),claude_status_kept=all(v['result']=='not run' and not v['complete'] for k,v in data['slots'].items() if k.startswith('Claude/')))
   else:checks['recheck_source']=False
   if kind=='candidate-repair':checks.update(actual_candidate_fix=r['candidate_after']['SKILL.md']==fixed_sha,version_reset=settings['version']=='v2',new_scope_decision='v2' in lower and 'claude' in lower)
   else:checks['candidate_unchanged']=r['before'][truth['candidate']+'/SKILL.md']==r['after'].get(truth['candidate']+'/SKILL.md')
  else:checks.update(no_unauthorized_repair='packet/settings.json' not in changes,candidate_unchanged=r['before'][truth['candidate']+'/SKILL.md']==r['after'].get(truth['candidate']+'/SKILL.md'),no_new_checks=not r['new_records'])
 checks['only_authorized_changed_files']=changes<=allowed
 checks['only_authorized_new_records']=all(p.startswith(permanent) or (repair and p in r['new_records']) for p in created)
 rows.append({'file':p.name,'mode':mode,'kind':kind,'invocation':invocation,'passed':all(checks.values()),'checks':checks,'loaded':loaded,'gate':gate(r),'tool_output_chars':sum(map(len,boot['outputs'])),'usage':r['usage']})
result={'source':expected,'Codex':'passed' if len(rows)==34 and all(r['passed'] for r in rows) else 'incomplete/failed','case_results':rows}
if len(sys.argv)>1:
 with (out/sys.argv[1]).open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({'Codex':result['Codex'],'cases':len(rows),'failed':[{'file':r['file'],'checks':[k for k,v in r['checks'].items() if not v]} for r in rows if not r['passed']]},ensure_ascii=False,indent=2))
