import ast,hashlib,importlib.util,json,re
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v3.json').read_text());out=Path(loc['out']);source=Path(loc['source']);skill=Path(loc['skill']);sp=importlib.util.spec_from_file_location('review',w/'review-v3.py');review=importlib.util.module_from_spec(sp);sp.loader.exec_module(review);rows=[]
for mode in ['common','both']:
 thread=None
 for step in range(1,7):
  p=out/f'chain-{mode}-step{step}.json'
  if not p.exists():continue
  r=json.loads(p.read_text());before=r['before'];after=r['after'];changed=sorted(k for k in set(before)|set(after) if before.get(k)!=after.get(k));text=r['final'];menu='Compound Engineering' in text and len(re.findall(r'(?m)^\s*\d+\. ',text))>=3
  if thread is None:thread=r['thread_id']
  checks={'completed':r['completed'] and r['exit_code']==0,'same_actual_thread':r['thread_id']==thread,'source':r['source_files']=={'rule':review.digest(source),'skill':review.snapshot(skill)},'project_preserved':r['project_before']==r['project_after'],'rules_and_native_copies':all(before.get(rel)==review.digest(source) for rel in ['harness/common/rules/comm-confirm-development-workflow.md','.claude/rules/comm-confirm-development-workflow.md']),'all_skill_copies':all({k[len(prefix)+1:]:v for k,v in before.items() if k.startswith(prefix+'/')}==review.snapshot(skill) for prefix in ['harness/common/skills/'+skill.name,'.agents/skills/'+skill.name,'.claude/skills/'+skill.name])}
  if step in [1,2,3]:checks.update(no_changes=not changed,no_menu=not menu)
  elif step==4:
   expected='DEFAULT_PORT = 5432\n\ndef selected_port(value=None):\n    return DEFAULT_PORT if value is None else int(value)\n';checks.update(only_port=changed==['src/ports.py'],correct_source=ast.dump(ast.parse(r['fixture_result']['src/ports.py']))==ast.dump(ast.parse(expected)),no_menu=not menu)
  elif step==5:
   required=(skill/'references/menu.md').read_text();ce=required[required.index('1. **Superpowers +'):required.index('\n\nЗнак')];items=[re.sub(r'^\d+\.\s*','',line) for line in ce.splitlines()];checks.update(new_choice_requested=menu,no_changes=not changed,actual_menu_number=r['no_special_menu_number'] is not None,literals=all(review.norm(t) in review.norm(text) for t in items))
  elif step==6:checks.update(only_config=changed==['settings.json'],configured=json.loads(r['fixture_result']['settings.json'])=={'mode':'new'},no_repeat_menu=not menu,numeric_reply_only=bool(re.fullmatch(r'Выбираю \d+\.',r['command'][-1])))
  rows.append({'file':p.name,'mode':mode,'step':step,'passed':all(checks.values()),'checks':checks,'changed':changed,'usage':r['usage'],'native_catalogue':r['native_catalogue']})
result={'passed':len(rows)==12 and all(r['passed'] for r in rows),'cases':rows,'method':'Two actual Codex threads, six real CLI resume turns each; route named only in turn1. A status/clarification precedes continue; new independent B must show its own menu, then actual displayed no-special item chosen by number. No platform compaction forced; separate fresh-context supplied-summary cases test the compaction input boundary.'}
with (out/'chain-audit.json').open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({'passed':result['passed'],'cases':len(rows),'failed':[{'file':r['file'],'checks':[k for k,v in r['checks'].items() if not v]} for r in rows if not r['passed']]},ensure_ascii=False,indent=2))
