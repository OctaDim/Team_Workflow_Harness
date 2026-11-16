import argparse,hashlib,importlib.util,json,os,shutil,tempfile
from pathlib import Path
from fixture import build
w=Path(__file__).parent;loc=json.loads((w/('location-v3.json' if (w/'location-v3.json').exists() else 'location-v2.json' if (w/'location-v2.json').exists() else 'location.json')).read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);source=Path(loc['source']);sp=importlib.util.spec_from_file_location('h',repo/'harness/common/testing/evidence/2026-10-19-instruction-form-selection/validate.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h)
p=argparse.ArgumentParser();p.add_argument('stage');p.add_argument('mode');p.add_argument('kind');p.add_argument('rep',type=int);a=p.parse_args();dest=out/f'{a.stage}-{a.mode}-{a.kind}-{a.rep}.json';assert not dest.exists()
with tempfile.TemporaryDirectory(prefix='workflow-native-') as d:
 base=Path(d);root=base/'project';root.mkdir();startup=h.prepare(root,a.mode,'baseline');target=repo/'harness/common/rules/comm-confirm-development-workflow.md' if a.stage=='baseline' else source
 for rel in ['harness/common/rules/comm-confirm-development-workflow.md','.claude/rules/comm-confirm-development-workflow.md']:shutil.copyfile(target,root/rel)
 if a.stage!='baseline':
  for parent in ['harness/common/skills','.agents/skills','.claude/skills']:shutil.copytree(Path(loc['skill']),root/parent/Path(loc['skill']).name)
 check=h.run(['python3','-B','harness/common/checks/ensure_entrypoint_links.py'],cwd=root);assert check['exit_code']==0
 extra_skills={}
 if a.kind in ['menu-short','menu-full']:
  vendor=Path('/home/octadim/.codex/plugins/cache/openai-curated-remote/superpowers/7.0.1/skills');h.ordinary(vendor)
  for folder in vendor.iterdir():
   if folder.is_dir() and (folder/'SKILL.md').exists():
    shutil.copytree(folder,root/'.agents/skills'/folder.name);extra_skills[folder.name]=h.snapshot(folder)
 truth,task=build(root,a.kind);before=h.snapshot(root);project=h.snapshot(root/'harness/project');prompt=('Одноразовый изолированный project. Выполни обязательный старт: checker; START common; START project; canonical comm-skill-rule-ownership и comm-human-folder-guides; отдельный rg --files --hidden --no-ignore .claude/rules без README.human.md; затем все явно перечисленные правила максимум по два за завершённый вызов, дочитывая обрезанное; затем INDEX common и INDEX project. До правил/INDEX не открывай SKILL. Работай только локально; без сети, installs, Git-мутаций и субагентов. Нельзя изменять файлы harness и entrypoints, кроме создания ровно указанной подготовительной заявки, если она прямо поручена ниже; root fixture-файлы можно менять только в пределах поручения ниже. Не сохраняй другие отчёты/файлы. После старта выполни реальное поручение: ')+task
 wrapper,env=h.isolation(base,root);env.update(PYTHONDONTWRITEBYTECODE='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_CONFIG_NOSYSTEM='1');r=h.run(wrapper+['codex','exec','--ignore-user-config','--skip-git-repo-check','-s','danger-full-access','-C',str(root),'-c','features.multi_agent=false','--json',prompt],cwd=root,env=env,timeout=900);messages=[];initial=[]
 for rollout in (base/'runtime/sessions').rglob('*.jsonl'):
  for line in rollout.read_text().splitlines():
   e=json.loads(line);v=e.get('payload',{})
   if e.get('type')!='response_item':continue
   if v.get('type') in ['custom_tool_call','custom_tool_call_output','function_call','function_call_output']:messages.append({k:v[k] for k in ['type','call_id','name','input','arguments','output'] if k in v})
   elif v.get('role') in ['system','developer']:initial.append({'role':v['role'],'type':v.get('type'),'serialized_utf8_bytes':len(json.dumps(v,ensure_ascii=False).encode()),'sha256':hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True).encode()).hexdigest()})
 events=[]
 for line in r['stdout'].splitlines():
  try:events.append(json.loads(line))
  except ValueError:pass
 fixture_result={}
 for rel in ['src/ports.py','settings.json','deps.toml','remote-state.json','notes.txt','harness/common/inbox/2026-11-16-fixture-port-validation/request.md']:
  path=root/rel
  if path.is_file():fixture_result[rel]=path.read_text()
 r.update(fixture_result=fixture_result,extra_skills=extra_skills,source_files={'rule':hashlib.sha256(target.read_bytes()).hexdigest(),'skill':h.snapshot(Path(loc['skill'])) if a.stage!='baseline' else None},stage=a.stage,mode=a.mode,kind=a.kind,rep=a.rep,source_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),source_text=target.read_text(),truth=truth,startup=startup,before=before,after=h.snapshot(root),project_before=project,project_after=h.snapshot(root/'harness/project'),model_tool_messages=messages,initial_context=initial,completed=any(e.get('type')=='turn.completed' for e in events),usage=[e.get('usage') for e in events if e.get('type')=='turn.completed'],final='\n'.join(e.get('item',{}).get('text','') for e in events if e.get('item',{}).get('type')=='agent_message'))
 with dest.open('x') as f:json.dump(r,f,ensure_ascii=False,indent=2)
 print(json.dumps({'file':dest.name,'completed':r['completed'],'code':r['exit_code'],'unchanged':r['before']==r['after'],'tool_messages':len(messages),'final':r['final'][-2300:]},ensure_ascii=False))
