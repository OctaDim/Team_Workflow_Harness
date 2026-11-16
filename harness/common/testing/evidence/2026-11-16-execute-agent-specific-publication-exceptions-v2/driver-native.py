import argparse,hashlib,importlib.util,json,os,shutil,tempfile
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from fixture import build
w=Path(__file__).parent;loc=json.loads((w/('location-v2.json' if (w/'location-v2.json').exists() else 'location.json')).read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);source=Path(loc['source']);name=source.name
sp=importlib.util.spec_from_file_location('h',repo/'harness/common/testing/evidence/2026-10-19-instruction-form-selection/validate.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h)
p=argparse.ArgumentParser();p.add_argument('stage');p.add_argument('mode');p.add_argument('kind');p.add_argument('invocation');p.add_argument('tag');a=p.parse_args();dest=out/f'{a.tag}-{a.mode}-{a.kind}-{a.invocation}.json';assert not dest.exists()
with tempfile.TemporaryDirectory(prefix='gate-native-') as d:
 base=Path(d);root=base/'project';root.mkdir();startup=h.prepare(root,a.mode,'baseline');actual=repo/'harness/common/skills'/name if a.stage=='baseline' else source
 for parent in ['harness/common/skills','.agents/skills','.claude/skills']:
  target=root/parent/name;shutil.rmtree(target);shutil.copytree(actual,target)
 truth,task,audit=build(root,a.kind);before=h.snapshot(root);project_before=h.snapshot(root/'harness/project');targets={parent:h.snapshot(root/parent/'comm-fixture-target') for parent in ['harness/common/skills','.agents/skills','.claude/skills']}
 prompt=('Одноразовый изолированный controlled publication-gate проект. Выбран маршрут «Без специального маршрута — текущая модель выполняет задачу». Старт: checker; START common; START project; затем harness/common/rules/comm-skill-rule-ownership.md и comm-human-folder-guides.md. Отдельным rg --files --hidden --no-ignore .claude/rules перечисли Markdown без README.human.md; cat явно перечисленных правил максимум по два за вызов до INDEX common, INDEX project и любого SKILL. Никаких субагентов, внешних сервисов, реальных модельных проверок, network, installs или мутаций Git. Проверки Git только чтением разрешены по владельцу. Это контроль решений на явно синтетических slot data; не утверждай, что они являются реальными проверками. ')
 if a.invocation=='explicit':prompt+='Примени $'+name+'. '
 prompt+=task
 wrapper,env=h.isolation(base,root);env.update(PYTHONDONTWRITEBYTECODE='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_CONFIG_NOSYSTEM='1');r=h.run(wrapper+['codex','exec','--ephemeral','--ignore-user-config','--skip-git-repo-check','-s','danger-full-access','-C',str(root),'-c','features.multi_agent=false','--json',prompt],cwd=root,env=env,timeout=900)
 events=[]
 for line in r['stdout'].splitlines():
  try:events.append(json.loads(line))
  except ValueError:pass
 outputs='\n'.join(e.get('item',{}).get('aggregated_output','') for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution');human_reads=[str(p.relative_to(root)) for p in root.rglob('README.human.md') if p.read_text().strip() and p.read_text().strip() in outputs]
 after=h.snapshot(root);actions=[json.loads(line) for line in audit.read_text().splitlines()] if audit.exists() else []
 r.update(stage=a.stage,mode=a.mode,kind=a.kind,invocation=a.invocation,source=h.snapshot(actual),candidate=h.snapshot(source),human_reads=human_reads,startup=startup,truth=truth,task=task,before=before,after=after,project_before=project_before,project_after=h.snapshot(root/'harness/project'),targets_before=targets,targets_after={parent:h.snapshot(root/parent/'comm-fixture-target') for parent in targets},candidate_after=h.snapshot(root/truth['candidate']),actions=actions,queue=json.loads((root/'queue-state.json').read_text()),request_after=(root/truth['request']/'request.md').read_text(),settings_after=json.loads((root/'packet/settings.json').read_text()),new_records={str(p.relative_to(root)):p.read_text() for p in (root/'packet').glob('recheck-*.json')},completed=any(e.get('type')=='turn.completed' for e in events),usage=[e.get('usage') for e in events if e.get('type')=='turn.completed'],time=datetime.now(ZoneInfo('Europe/Minsk')).isoformat())
 r['final']='\n'.join(e.get('item',{}).get('text','') for e in events if e.get('item',{}).get('type')=='agent_message')
 with dest.open('x') as f:json.dump(r,f,ensure_ascii=False,indent=2)
 print(json.dumps({'file':dest.name,'completed':r['completed'],'code':r['exit_code'],'actions':actions,'queue':r['queue'],'new_records':list(r['new_records']),'final':r['final'][-1700:]},ensure_ascii=False))
