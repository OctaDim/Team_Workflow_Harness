import hashlib,json,re,sys
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v3.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);source=Path(loc['source']);skill=Path(loc['skill'])
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(p):return {str(x.relative_to(p)):digest(x) for x in p.rglob('*') if x.is_file()}
def norm(t):return re.sub(r'\s+',' ',re.sub(r'[*`>]','',t)).strip()
def visible(r):
 calls={};rows=[]
 for m in r['model_tool_messages']:
  if m['type'] in ['custom_tool_call','function_call']:calls[m['call_id']]=m;continue
  value=m.get('output','');blocks=[{'text':value}] if isinstance(value,str) else value;decoded=[];texts=[]
  for b in blocks if isinstance(blocks,list) else []:
   if b.get('type','text') not in ['text','input_text','output_text']:continue
   t=b.get('text','');texts.append(t)
   try:v=json.loads(t)
   except ValueError:decoded.append(t);continue
   decoded.append(v['output'] if isinstance(v,dict) and isinstance(v.get('output'),str) else t)
  c=calls.get(m.get('call_id'),{});rows.append({'input':c.get('input',c.get('arguments','')),'outputs':decoded,'visible_text_bytes':sum(len(t.encode()) for t in texts),'visible_text_chars':sum(map(len,texts))})
 return rows

def coverage(text,outputs):
 joined='\n'.join(outputs);return all(s.strip() in joined for s in text.splitlines() if s.strip())
def bootstrap(r,rows):
 outs=['\n'.join(v['outputs']) for v in rows]
 def positions(text):return [i for i in range(len(rows)) if coverage(text,outs[:i+1])]
 required=['harness/common/START.md','harness/project/START.md','harness/common/rules/comm-skill-rule-ownership.md','harness/common/rules/comm-human-folder-guides.md'];p={k:min(positions((repo/k).read_text()),default=None) for k in required};listing=[i for i,v in enumerate(rows) if all(s in v['input'] for s in ['rg --files','--no-ignore','.claude/rules'])];rules=[r['source_text'] if f.name=='comm-confirm-development-workflow.md' else f.read_text() for f in (repo/'.claude/rules').rglob('*.md') if f.name!='README.human.md'];end=next((i for i in range(len(rows)) if listing and i>min(listing) and all(coverage(t,outs[min(listing)+1:i+1]) for t in rules)),None);ci=min(positions((repo/'harness/common/INDEX.md').read_text()),default=None);pi=min(positions((repo/'harness/project/INDEX.md').read_text()),default=None);procs=[p.read_text() for p in (repo/'harness/common/skills').rglob('SKILL.md')]+[(skill/'SKILL.md').read_text()];
 if r.get('extra_skills'):
  vendor=Path('/home/octadim/.codex/plugins/cache/openai-curated-remote/superpowers/7.0.1/skills');procs.extend((vendor/name/'SKILL.md').read_text() for name in r['extra_skills'])
 first=min((i for t in procs for i in positions(t)),default=len(rows));valid=bool(listing) and all(v is not None for v in p.values()) and p[required[0]]<=p[required[1]]<=min(listing) and all(p[k]<min(listing) for k in required[2:]) and end is not None and ci is not None and pi is not None and min(listing)<end<=ci<=pi<first
 return {'passed':valid,'listing':listing,'rules_end':end,'indexes':[ci,pi],'first_procedure':first,'guards':p}

def assess(p):
 r=json.loads(p.read_text());rows=visible(r);outs=['\n'.join(v['outputs']) for v in rows];allout='\n'.join(outs);final=r['final'];lower=final.lower();f=norm(final);kind=r['kind'];before=r['before'];after=r['after'];changes=sorted(k for k in set(before)|set(after) if before.get(k)!=after.get(k));boot=bootstrap(r,rows);loaded=any(coverage((skill/'SKILL.md').read_text(),outs[:i+1]) for i in range(len(rows)));menu_read=coverage((skill/'references/menu.md').read_text(),outs);choice_read=coverage((skill/'references/choice.md').read_text(),outs);numbered=re.findall(r'(?m)^\s*(\d+)\.\s+(.+)',final);menu='Compound Engineering' in final and len(numbered)>=3;checks={'completed':r['completed'] and r['exit_code']==0,'actual_model_outputs':bool(rows),'bootstrap':boot['passed'],'project_preserved':r['project_before']==r['project_after'],'human_exclusion':r['truth']['human_marker'] not in allout and not r.get('human_reads',[])}
 if r['stage']=='candidate':
  checks['exact_current_source']=r['source_files']=={'rule':digest(source),'skill':snapshot(skill)}
  checks['tested_rule_copies']=all(before.get(rel)==digest(source) for rel in ['harness/common/rules/comm-confirm-development-workflow.md','.claude/rules/comm-confirm-development-workflow.md'])
  checks['tested_full_skill_copies']=all({k[len(prefix)+1:]:v for k,v in before.items() if k.startswith(prefix+'/')}==snapshot(skill) for prefix in ['harness/common/skills/'+skill.name,'.agents/skills/'+skill.name,'.claude/skills/'+skill.name])
 write=kind in r['truth']['write_cases'];menu_case=kind in r['truth']['menu_cases'];clarify=kind in r['truth']['clarify_cases']
 if write:
  expected='DEFAULT_PORT = 5432\n\ndef selected_port(value=None):\n    return DEFAULT_PORT if value is None else int(value)\n';checks.update(only_port_file=changes==['src/ports.py'],changed_to_5432=(__import__('ast').dump(__import__('ast').parse(r['fixture_result']['src/ports.py']))==__import__('ast').dump(__import__('ast').parse(expected)) if 'src/ports.py' in r.get('fixture_result',{}) else after.get('src/ports.py')==hashlib.sha256(expected.encode()).hexdigest()),no_new_menu=not menu,verified_result='5432' in final)
 elif kind=='record':
  prefix='harness/common/inbox/2026-11-16-fixture-port-validation/';checks.update(preparation_only=bool(changes) and all(c.startswith(prefix) for c in changes),request_created=prefix+'request.md' in after,no_route_menu=not menu,no_implementation=after.get('src/ports.py')==before.get('src/ports.py'))
 else:checks['no_changes']=not changes
 if menu_case:
  literal=(skill/'references/menu.md').read_text();ce=literal[literal.index('1. **Superpowers +'):literal.index('\n\nЗнак')];items=[re.sub(r'^\d+\.\s*','',line) for line in ce.splitlines()];checks.update(menu_present=menu,owner_loaded=loaded,menu_resource_read=menu_read,continuous_numbering=[int(n) for n,t in numbered]==list(range(1,len(numbered)+1)),literal_alternatives=all(norm(t) in f for t in items),waiting_for_choice=bool(re.search(r'выбер|выбира|выбор|соглас|подтверд',lower)))
  full=kind=='menu-full' or 'subagent-driven-development' in final or 'brainstorming → writing-plans → executing-plans' in final
  if full:
   warning=literal[literal.index('> **Самостоятельная реализация'):literal.index('\n\nЯвный вызов')];checks['full_warning_literal']=norm(warning) in f;items=re.findall(r'(?ms)^\s*\d+\.\s+(.*?)(?=^\s*\d+\.\s+|\Z)',final);one=any('через одного агента' in norm(t).lower() and re.search(r'brainstorming.*writing-plans.*executing-plans',norm(t)) for t in items);delegated=any('через субагентов' in norm(t).lower() and re.search(r'brainstorming.*writing-plans.*subagent-driven-development',norm(t)) for t in items);checks['both_full_choices']=one and delegated
  if kind=='mixed':checks['research_before_menu']='4321' in final and ('src/ports.py' in final)
 elif clarify:checks.update(owner_loaded=loaded,choice_resource_read=choice_read,clarification=bool(re.search(r'уточн|выбер|выбира|какой|конфликт|неоднознач|номер|вариант',lower)))
 elif kind=='executor-number':checks.update(owner_loaded=loaded,choice_resource_read=choice_read,one_executor=bool(re.search(r'одн(?:ого|им) агент|executing-plans|основн.{0,15}агент',lower)),no_new_menu=not menu)
 elif kind!='record' and not write:
  checks['no_route_menu']=not menu
  if kind=='audit':checks['correct_value']='4321' in final
  if kind=='diagnose':checks['cause']='ValueError' in final and 'int(' in final
  if kind=='proposal':checks['proposal_delivered']=bool(re.search(r'предлаг|валидац|провер|рекоменд',lower))
  if kind=='scope-explanation':checks['analytics_exempt']=bool(re.search(r'без меню|не требует|не нуж|не требуется|не нужно',lower))
  if kind=='explicit-skill':checks['requested_skill_read']=coverage((repo/'harness/common/skills/comm-verify-project-facts/SKILL.md').read_text(),outs);checks['correct_value']='4321' in final
  if kind=='separate-approval':checks['separate_permissions']=bool(re.search(r'недостат|не разреш|не замен|нельзя|нужн|требу',lower))
  if kind in ['audit','diagnose','proposal','explicit-skill']:checks['menu_owner_nonloading']=not loaded and not menu_read and not choice_read
 return {'file':p.name,'mode':r['mode'],'kind':kind,'rep':r['rep'],'stage':r['stage'],'passed':all(checks.values()),'checks':checks,'bootstrap':boot,'changed_paths':changes,'loaded':loaded,'menu_resource_read':menu_read,'choice_resource_read':choice_read,'menu':menu,'usage':r['usage'],'actual_tool_text_chars':sum(v['visible_text_chars'] for v in rows),'actual_tool_text_bytes':sum(v['visible_text_bytes'] for v in rows)}

if __name__=='__main__':
 files=[p for p in sorted(out.glob('candidate-*.json')) if re.match(r'candidate-(?:common|both)-.+-\d+\.json$',p.name) and '-review-contract-' not in p.name];files=[p for p in files if not (p.name in ['candidate-common-record-1.json','candidate-both-record-1.json'] and (out/p.name.replace('-record-','-record-prepared-')).exists())];rows=[assess(p) for p in files];result={'rule_sha256':digest(source),'skill':snapshot(skill),'case_results':rows,'Codex':'passed' if len(rows)==65 and all(r['passed'] for r in rows) else 'incomplete/failed','method':'Actual post-truncation model tool text; raw filesystem hashes; all available instruction lines across bounded chunks. API metadata/system messages omitted from text reads and counted separately in raw. Semantic/format matches are manually reviewed if flagged.'}
 if len(sys.argv)>1:
  with (out/sys.argv[1]).open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2)
 print(json.dumps({'cases':len(rows),'Codex':result['Codex'],'failed':[{'file':r['file'],'failed':[k for k,v in r['checks'].items() if not v]} for r in rows if not r['passed']]},ensure_ascii=False,indent=2))
