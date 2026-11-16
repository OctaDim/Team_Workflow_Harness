import hashlib,json,re,sys
from pathlib import Path
from audit import bootstrap,content_reads
w=Path(__file__).parent;loc=json.loads((w/('location-v2.json' if (w/'location-v2.json').exists() else 'location.json')).read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);source=Path(loc['source']);expected=hashlib.sha256(source.read_bytes()).hexdigest();rows=[]
for mode in ['common','both']:
 for kind in ['ordinary','selected','triage','history','unrelated']:
  p=out/f'current-{mode}-{kind}.json'
  if not p.exists():continue
  r=json.loads(p.read_text());a=bootstrap(repo,r);commands=a['commands'];outputs='\n'.join(a['outputs']);t=r['truth'];final=r['final'];lower=final.lower();historical=[m for m in t['historical_markers'] if m in outputs];history_refs=[path for path in t['historical_copies'] if content_reads(commands,path)];closed=t['closed_marker'] in outputs;human=t['human_marker'] in outputs or bool(r['human_reads']);canonical=content_reads(commands,t['canonical'],'FW-CURRENT-41');selected=content_reads(commands,t['selected'],'FW-SELECTED-CURRENT-42');report=content_reads(commands,t['report'],'FW-REPORT-65');raw=content_reads(commands,t['raw'],'FW-RAW-66')
  checks={'completed':r['completed'] and r['exit_code']==0,'current_index':r['source_sha256']==expected and r['tested_sha256']==expected,'bootstrap':a['valid'],'project_preserved':r['project_before']==r['project_after'],'files_unchanged':r['before']==r['after'],'human_exclusion':not human,'no_unselected_historical_bodies':not historical and not history_refs and not closed}
  if kind in ['selected','triage']:
   status=[]
   for i,item in enumerate(commands):
    output=item.get('aggregated_output','');command=item.get('command','')
    if re.search(r'Status\s*:\s*in progress',output) and (t['current_request'] in command or '/'.join(Path(t['current_request']).parts[-2:]) in command or t['current_request'] in output):status.append(i)
   guarded_same=any(re.search(r'\b(?:if|assert)\b[^\n]*(?:status|Status|in progress)',commands[i].get('command','')) for i in set(status)&set(selected))
   checks.update(status_first=bool(status) and bool(selected) and (min(status)<min(selected) or guarded_same),actual_selected=bool(selected),selected_source=Path(t['selected']).name in final,semantic_result=bool(re.search(r'utf[ -]?8',lower)) and any(s in lower for s in ['соответств','совпад','выполн','matches','compli']))
   if kind=='triage':checks['canonical_current']=bool(canonical)
  elif kind=='ordinary':checks.update(canonical_read=bool(canonical),current_encoding=bool(re.search(r'utf[ -]?8',lower)),actual_source='base/fixture-wire.json' in final)
  elif kind=='history':checks.update(needed_report=bool(report),needed_raw=bool(raw),canonical_read=bool(canonical),actual_difference=bool(re.search(r'utf[ -]?8',lower)) and bool(re.search(r'utf[ -]?16',lower)),not_blanket_history_ban=any(s in lower for s in ['наблюд','получ','ожид','вход','observ','expected']))
  else:checks.update(answer='184' in final,no_extra_lookup=not canonical and not selected and not report and not raw)
  if kind!='history':checks['no_unneeded_evidence']=not report and not raw and not any(m in outputs for m in t['evidence_markers'])
  rows.append({'file':p.name,'mode':mode,'kind':kind,'passed':all(checks.values()),'checks':checks,'observed':{'canonical_reads':canonical,'selected_reads':selected,'report_reads':report,'raw_reads':raw,'unselected_history_refs':history_refs,'historical_markers':historical,'closed_body':closed},'tool_output_chars':sum(map(len,a['outputs'])),'usage':r['usage']})
result={'source_sha256':expected,'Codex':'passed' if len(rows)==10 and all(r['passed'] for r in rows) else 'incomplete/failed','case_results':rows}
if len(sys.argv)>1:
 with (out/sys.argv[1]).open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({'Codex':result['Codex'],'cases':len(rows),'failed':[{'file':r['file'],'checks':[k for k,v in r['checks'].items() if not v]} for r in rows if not r['passed']]},ensure_ascii=False,indent=2))
