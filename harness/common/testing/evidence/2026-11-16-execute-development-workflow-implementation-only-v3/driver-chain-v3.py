import hashlib,importlib.util,json,os,re,shutil,tempfile
from pathlib import Path
from fixture import build
w=Path(__file__).parent;loc=json.loads((w/'location-v3.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);source=Path(loc['source']);skill=Path(loc['skill']);sp=importlib.util.spec_from_file_location('h',repo/'harness/common/testing/evidence/2026-10-19-instruction-form-selection/validate.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h)
def save(n,v):
 with (out/n).open('x') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def events(r):
 a=[]
 for s in r['stdout'].splitlines():
  try:a.append(json.loads(s))
  except ValueError:pass
 return a
for mode in ['common','both']:
 with tempfile.TemporaryDirectory(prefix='workflow-chain-') as d:
  base=Path(d);root=base/'project';root.mkdir();startup=h.prepare(root,mode,'baseline')
  for rel in ['harness/common/rules/comm-confirm-development-workflow.md','.claude/rules/comm-confirm-development-workflow.md']:shutil.copyfile(source,root/rel)
  for parent in ['harness/common/skills','.agents/skills','.claude/skills']:shutil.copytree(skill,root/parent/skill.name)
  truth,_=build(root,'preselected');wrapper,env=h.isolation(base,root);env.update(PYTHONDONTWRITEBYTECODE='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_CONFIG_NOSYSTEM='1');thread=None;seen_calls=set();number=None
  prompts=[
   'Обязательный старт: checker, START common, START project, canonical comm-skill-rule-ownership и comm-human-folder-guides; отдельный rg --files --hidden --no-ignore .claude/rules без README.human.md, все явно перечисленные правила максимум по два за вызов с дочитыванием обрезанного, затем оба INDEX common→project до SKILL. Только локально, без сети/installs/субагентов/Git-мутаций. Harness/entrypoints не меняй. Фиксируем согласованный набор A: изменить DEFAULT_PORT в src/ports.py на5432. Для всего A выбран «Без специального маршрута — текущая модель c effort самостоятельно выполняет задачу». Сейчас только прочитай код и объясни текущий default; запись пока не делай. Разрешаю саму правку A только после моего отдельного сообщения «Продолжи согласованный набор».',
   'Какой сейчас статус?',
   'Уточнение к набору A: новое значение ровно5432. Пока только подтверди, что это учтено; запись ещё не начинай.',
   'Продолжи согласованный набор.',
   'Набор A завершён. Теперь отдельная новая задача B: измени settings.json, mode=new. Правка разрешена; маршрут для B ещё не выбран.',
   None]
  for step,prompt in enumerate(prompts,1):
   if step==6:
    assert number is not None,'No unambiguous no-special item in actual B menu';prompt=f'Выбираю {number}.'
   before=h.snapshot(root);project=h.snapshot(root/'harness/project');command=wrapper+['codex','exec','--ignore-user-config','--skip-git-repo-check','-s','danger-full-access','-C',str(root),'-c','features.multi_agent=false','--json']
   if thread:command+=['resume',thread]
   r=h.run(command+[prompt],cwd=root,env=env,timeout=900);es=events(r);ids=[e['thread_id'] for e in es if e.get('type')=='thread.started'];assert ids
   if thread:assert ids[0]==thread
   else:thread=ids[0]
   messages=[];catalogue=[]
   for rollout in (base/'runtime/sessions').rglob('*.jsonl'):
    for line in rollout.read_text().splitlines():
     e=json.loads(line);v=e.get('payload',{})
     if e.get('type')!='response_item':continue
     if v.get('type') in ['custom_tool_call','custom_tool_call_output','function_call','function_call_output']:messages.append({k:v[k] for k in ['type','name','call_id','input','arguments','output'] if k in v})
     elif v.get('role') in ['system','developer']:
      serialized=json.dumps(v,ensure_ascii=False)
      if skill.name in serialized and 'Use when an implementation task needs a workflow route menu or a reply to that menu needs interpretation.' in serialized:catalogue.append(hashlib.sha256(serialized.encode()).hexdigest())
   current_calls={m['call_id'] for m in messages if 'call_id' in m};delta=[m for m in messages if m.get('call_id') not in seen_calls];seen_calls=current_calls
   final='\n'.join(e.get('item',{}).get('text','') for e in es if e.get('item',{}).get('type')=='agent_message')
   if step==5:
    matches=[int(m.group(1)) for m in re.finditer(r'(?m)^\s*(\d+)\.\s+[^\n]*Без специального маршрута',final)];assert len(matches)==1;number=matches[0]
   r.update(mode=mode,step=step,thread_id=thread,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),source_text=source.read_text(),source_files={'rule':hashlib.sha256(source.read_bytes()).hexdigest(),'skill':h.snapshot(skill)},before=before,after=h.snapshot(root),project_before=project,project_after=h.snapshot(root/'harness/project'),model_tool_messages=messages,new_model_tool_messages=delta,native_catalogue={'listed':bool(catalogue),'metadata_hashes':catalogue},fixture_result={p:(root/p).read_text() for p in ['src/ports.py','settings.json']},final=final,usage=[e.get('usage') for e in es if e.get('type')=='turn.completed'],completed=any(e.get('type')=='turn.completed' for e in es),no_special_menu_number=number,compaction_events=sum(e.get('type')=='context.compacted' for e in es))
   save(f'chain-{mode}-step{step}.json',r);print(json.dumps({'mode':mode,'step':step,'code':r['exit_code'],'completed':r['completed'],'changed':[p for p in set(before)|set(r['after']) if before.get(p)!=r['after'].get(p)]}),flush=True);assert r['completed'] and r['exit_code']==0
