import argparse, importlib.util, json, os, shutil, subprocess, tempfile
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

REPO=Path('/home/octadim/MyProjects/Team_Workflow_Harness')
spec=importlib.util.spec_from_file_location('helpers',REPO/'harness/common/testing/evidence/2026-10-19-instruction-form-selection/validate.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
p=argparse.ArgumentParser();p.add_argument('config');p.add_argument('mode');p.add_argument('case');p.add_argument('tag');a=p.parse_args()
c=json.loads(Path(a.config).read_text());out=REPO/c['out'];source=REPO/c['source'];name=source.name
dest=out/f'{a.tag}-{a.mode}-{a.case}.json'
assert not dest.exists()
h.ordinary(REPO/'harness');h.ordinary(source)
with tempfile.TemporaryDirectory(prefix='git-skill-native-') as d:
 base=Path(d);root=base/'project';root.mkdir();startup=h.prepare(root,a.mode,'baseline')
 for parent in ('harness/common/skills','.agents/skills','.claude/skills'):
  target=root/parent/name
  if target.exists():shutil.rmtree(target)
  if a.case!='control':shutil.copytree(source,target)
 for rel,body in c.get('files',{}).items():
  f=root/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(body)
 for command in c.get('setup',[]):
  r=h.run(command,cwd=root);assert r['exit_code']==0,r
 prompt=('Изолированный синтетический acceptance-проект. Пользователь явно выбрал маршрут '
 '«Без специального маршрута — текущая модель c effort самостоятельно выполняет задачу». '
 'Выполни обязательный старт и чтение в указанном порядке, исключая README.human.md. '
 'Разрешены только локальные read-only действия. Не меняй файлы, не делай коммитов, '
 'не публикуй, не отправляй данные наружу, не используй субагентов. ')
 if a.case=='explicit':prompt+='Примени $'+name+'. '
 prompt+=('Вычисли 23*8; тела скиллов без соответствующей задачи не открывай.' if a.case=='unrelated' else c['task'])
 before=h.snapshot(root);wrapper,env=h.isolation(base,root)
 record=h.run(wrapper+['codex','exec','--ephemeral','--ignore-user-config','--skip-git-repo-check','-s','read-only','-C',str(root),'-c','features.multi_agent=false','--json',prompt],cwd=root,env=env,timeout=600)
 events=[]
 for line in record['stdout'].splitlines():
  try:events.append(json.loads(line))
  except ValueError:pass
 record.update(mode=a.mode,case=a.case,time=datetime.now(ZoneInfo('Europe/Minsk')).isoformat(),startup=startup,unchanged=h.snapshot(root)==before,source=h.snapshot(source),completed=any(e.get('type')=='turn.completed' for e in events))
 record['final']='\n'.join(e.get('item',{}).get('text','') for e in events if isinstance(e.get('item'),dict) and e['item'].get('type')=='agent_message')
 record['commands']=[e['item'].get('command') for e in events if isinstance(e.get('item'),dict) and e['item'].get('type')=='command_execution']
 record['usage']=[e.get('usage') for e in events if e.get('type')=='turn.completed']
 with dest.open('x') as f:json.dump(record,f,ensure_ascii=False,indent=2)
 print(json.dumps({k:record[k] for k in ['exit_code','completed','unchanged','final']},ensure_ascii=False))
