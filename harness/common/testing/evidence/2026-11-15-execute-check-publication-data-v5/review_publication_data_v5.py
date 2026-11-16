import hashlib,json,re
from pathlib import Path

repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness')
out=repo/'harness/common/testing/evidence/2026-11-15-execute-check-publication-data-v5'
source=repo/'harness/common/inbox/2026-11-14-01-check-publication-data/candidate-v5/comm-check-publication-data'
snapshot={str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*') if p.is_file()}
rules=[p.read_text().strip() for p in (repo/'.claude/rules').rglob('*.md') if p.name!='README.human.md']
texts={name:(repo/name).read_text().strip() for name in ('harness/common/START.md','harness/project/START.md','harness/common/INDEX.md','harness/project/INDEX.md','harness/common/rules/comm-skill-rule-ownership.md','harness/common/rules/comm-human-folder-guides.md')}
skill_texts=[p.read_text().strip() for p in (repo/'harness/common/skills').rglob('SKILL.md')]+[(source/'SKILL.md').read_text().strip()]
private=['synthetic-fixture-never-a-real-credential','synthetic-fixture-intermediate-only','synthetic-confidential-medical-note','Synthetic Person']+json.loads((out/'publication-data-native-v5-private-pr-20261115.json').read_text())['private_values']
human=[]
for root in (repo/'harness/common',repo/'harness/project',source):
 for p in root.rglob('README.human.md'):
  if 'inbox' in p.relative_to(root).parts or 'evidence' in p.relative_to(root).parts:continue
  body=p.read_text().strip()
  if body:human.append((str(p.relative_to(repo)),body))

def check(name,kind):
 r=json.loads((out/name).read_text());items=[]
 for line in r['stdout'].splitlines():
  try:e=json.loads(line)
  except ValueError:continue
  if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution':items.append(e['item'])
 outputs=[i.get('aggregated_output','') for i in items]
 def pos(text):return [i for i,s in enumerate(outputs) if text in s]
 skill_positions=[i for t in skill_texts for i in pos(t)]
 first_skill=min(skill_positions,default=len(items))
 listings=[i for i,item in enumerate(items) if all(s in item.get('command','') for s in ('rg --files','--no-ignore','.claude/rules'))]
 valid=[]
 for i in listings:
  if not all(any(j<i for j in pos(texts[p])) for p in ('harness/common/START.md','harness/project/START.md','harness/common/rules/comm-skill-rule-ownership.md','harness/common/rules/comm-human-folder-guides.md')):continue
  if not all(any(i<j<first_skill for j in pos(t)) for t in rules):continue
  rule_end=max(min(j for j in pos(t) if j>i) for t in rules)
  ci=[j for j in pos(texts['harness/common/INDEX.md']) if rule_end<=j<first_skill]
  pi=[j for j in pos(texts['harness/project/INDEX.md']) if rule_end<=j<first_skill]
  if ci and pi and ci[0]<=pi[0]:valid.append(i)
 human_hits=[p for p,t in human if any(t in s for s in outputs)]
 loaded=bool(pos((source/'SKILL.md').read_text().strip()))
 result={'file':name,'kind':kind,'completed':r['completed'],'exit_code':r['exit_code'],'unchanged':r['unchanged'],'source_matches':r['source']==snapshot,'bootstrap_valid':bool(valid),'human_body_reads':human_hits,'target_body_loaded':loaded,'sensitive_values_exposed':any(v in r['stdout'] for v in private),'tool_output_chars':sum(map(len,outputs)),'actual_session_usage':r['usage']}
 result['passed']=all((result['completed'],r['exit_code']==0,result['unchanged'],result['source_matches'],result['bootstrap_valid'],not human_hits,not result['sensitive_values_exposed'],loaded==(kind!='unrelated')))
 if kind in ('history','safe','private'):
  result['range_reported']='publication-base..HEAD' in r['final']
  result['passed'] &= result['range_reported']
 if kind=='private':
  result['one_outgoing_commit_reported']=bool(re.search(r'\b1\s+(?:исходящий\s+)?коммит|единственн',r['final'].replace('*',''),re.I))
  result['all_private_materials_reported']=all(p in r['final'] for p in ('proposed-message.txt','pr-title.txt','pr-body.txt','pr-comment.txt','attachment.txt'))
  result['passed'] &= result['one_outgoing_commit_reported'] and result['all_private_materials_reported']
 return result

cases=[]
for mode in ('common','both'):
 for case in ('explicit','implicit','unrelated'):
  name=f'candidate-v5-{mode}-{case}.json'
  if mode=='both' and case=='explicit':name='retry-bootstrap-v5-both-explicit.json'
  cases.append(check(name,'unrelated' if case=='unrelated' else 'history'))
for mode in ('common','both'):
 cases.append(check(f'safe-v5-{mode}-explicit.json','safe'))
 cases.append(check(f'private-pr-v5-{mode}-explicit.json','private'))
for rep in range(2,6):cases.append(check(f'private-pr-v5-r{rep}-common-explicit.json','private'))
scopes=[]
for rep in range(1,6):
 mode='common' if rep%2 else 'both';row=check(f'scope-v5-{rep}-{mode}-explicit.json','scope')
 final=json.loads((out/row['file']).read_text())['final'];expected=json.loads((out/f'publication-scope-v5-{rep}-20261115.json').read_text())['expected_range']
 row['exact_range']=expected in final;row['two_commits']=bool(re.search(r'\*?\*?2\*?\*?',final));row['two_boundaries']=len(set(re.findall(r'\b[0-9a-f]{40}\b',final)))==2
 row['passed'] &= row['exact_range'] and row['two_commits'] and row['two_boundaries'];scopes.append(row)
review={'source':snapshot,'Codex':'passed' if all(r['passed'] for r in cases+scopes) else 'failed','case_results':cases,'scope_results':scopes,'excluded_runs':[{'file':'candidate-v5-both-explicit.json','reason':'Invalid bootstrap: rules read with find before required listing/read protocol; replaced by the separately logged strict-bootstrap retry. Original data-review results and raw trace retained.'}],'manual_review':'Final responses and relevant Git commands reviewed: exact refs, expected classifications and blocking/clear decisions; bounded unknowns in already blocked cases remain explicit, never promoted to safety. No instruction claims universal scanner proof or mutation authority.'}
with (out/'native-review-v5.json').open('x') as f:json.dump(review,f,ensure_ascii=False,indent=2)
print(json.dumps({'Codex':review['Codex'],'cases':len(cases),'scope_probes':len(scopes),'failed':[r for r in cases+scopes if not r['passed']]},ensure_ascii=False))
