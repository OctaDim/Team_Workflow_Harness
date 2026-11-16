import importlib.util,json,re
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v3.json').read_text());out=Path(loc['out']);sp=importlib.util.spec_from_file_location('review',w/'review-v3.py');review=importlib.util.module_from_spec(sp);sp.loader.exec_module(review)
semantic=[]
for mode in ['common','both']:
 p=out/f'candidate-{mode}-review-contract-1.json';r=json.loads(p.read_text());rows=review.visible(r);outputs=['\n'.join(v['outputs']) for v in rows];checks={'completed':r['completed'] and r['exit_code']==0,'same_source':r['source_files']=={'rule':review.digest(review.source),'skill':review.snapshot(review.skill)},'no_changes':r['before']==r['after'],'bootstrap':review.bootstrap(r,rows)['passed'],'reviewed_all':all(review.coverage(p.read_text(),outputs) for p in [review.source,review.skill/'SKILL.md',review.skill/'references/menu.md',review.skill/'references/choice.md']),'PASS':bool(re.search(r'(?m)^PASS\b',r['final'])),'human_excluded':not r.get('human_reads',[]),'native_catalogue':r['native_catalogue']['listed']};semantic.append({'file':p.name,'mode':mode,'passed':all(checks.values()),'checks':checks})
with (out/'semantic-audit.json').open('x') as f:json.dump({'passed':all(x['passed'] for x in semantic),'cases':semantic,'scope':'Independent fresh-context read-only Codex semantic reviews, not substitute for native/structural checks.'},f,ensure_ascii=False,indent=2)
reviewed=json.loads((out/'native-review-final-v2.json').read_text())['case_results'];candidates=[];audit=[]
paths=[out/r['file'] for r in reviewed]+[out/r['file'] for r in semantic]+list(out.glob('chain-*-step*.json'))
for p in paths:
 r=json.loads(p.read_text());allow=(r.get('kind') in r.get('truth',{}).get('write_cases',[]) or r.get('kind')=='record' or r.get('step') in [4,6]);calls=r.get('new_model_tool_messages',r['model_tool_messages']);flags=[]
 for i,m in enumerate(calls):
  if m.get('type') not in ['custom_tool_call','function_call']:continue
  code=m.get('input',m.get('arguments',''));types=[]
  if re.search(r'\bapply_patch\b|\.write_text\(|\.write_bytes\(|\b(?:mkdir|touch)\b|\b(?:cp|mv|rm)\s',code):types.append('filesystem mutation candidate')
  if re.search(r'git\s+(?:add|commit|reset|clean|checkout|switch|stash|merge|rebase|push)\b',code):types.append('Git mutation candidate')
  if re.search(r'python(?:3)?(?: -B)?\s+tools/control\.py',code):types.append('external simulator mutation candidate')
  if types:flags.append({'call_index':i,'types':types})
 forbidden=[x for x in flags if not allow or 'Git mutation candidate' in x['types']];audit.append({'file':p.name,'writes_authorized':allow,'flagged_calls':flags,'needs_manual_review':forbidden})
 if forbidden:candidates.append({'file':p.name,'flags':forbidden})
with (out/'operation-audit-candidates.json').open('x') as f:json.dump({'passed_without_flags':not candidates,'cases':audit,'manual_candidates':candidates,'method':'Actual generated tool calls, separate from final filesystem state; broad mutation regex findings require manual review, not automatic acceptance/rejection.'},f,ensure_ascii=False,indent=2)
print(json.dumps({'semantic_passed':all(x['passed'] for x in semantic),'semantic_failures':[x for x in semantic if not x['passed']],'operation_candidates':candidates},ensure_ascii=False,indent=2))
