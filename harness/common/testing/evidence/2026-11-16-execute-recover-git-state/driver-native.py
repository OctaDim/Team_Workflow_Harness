import argparse,hashlib,importlib.util,json,os,shutil,subprocess,tempfile
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from fixture import build
w=Path(__file__).parent;loc=json.loads((w/'location.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);source=Path(loc['source']);name=source.name
sp=importlib.util.spec_from_file_location('h',repo/'harness/common/testing/evidence/2026-10-19-instruction-form-selection/validate.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h)
p=argparse.ArgumentParser();p.add_argument('stage');p.add_argument('mode');p.add_argument('kind');p.add_argument('invocation');p.add_argument('tag');a=p.parse_args();dest=out/f'{a.tag}-{a.mode}-{a.kind}-{a.invocation}.json';assert not dest.exists()
def state(root):
 def git(*args):return subprocess.run(['git',*args],cwd=root,capture_output=True,text=True).stdout
 return {'head':git('rev-parse','HEAD').strip(),'branch':git('branch','--show-current').strip(),'refs':git('for-each-ref','--format=%(refname) %(objectname)'),'index':git('ls-files','--stage','-z'),'staged':git('diff','--cached','--binary'),'unstaged':git('diff','--binary'),'status':git('status','--porcelain=v1','--untracked-files=all'),'reflogs':git('reflog','show','--all','--format=%H %gs'),'merge_head':(root/'.git/MERGE_HEAD').read_text() if (root/'.git/MERGE_HEAD').exists() else None,'config':hashlib.sha256((root/'.git/config').read_bytes()).hexdigest(),'worktrees':git('worktree','list','--porcelain')}
with tempfile.TemporaryDirectory(prefix='recover-native-') as d:
 base=Path(d);root=base/'project';root.mkdir();startup=h.prepare(root,a.mode,'baseline')
 if a.stage!='baseline':
  for parent in ['harness/common/skills','.agents/skills','.claude/skills']:
   target=root/parent/name
   if target.exists():shutil.rmtree(target)
   shutil.copytree(source,target)
 truth,task=build(root,a.kind);before=h.snapshot(root);gb=state(root)
 prompt=('Одноразовый изолированный Git-проект. Выбран маршрут «Без специального маршрута — текущая модель выполняет задачу». Старт: checker; START common; START project; затем harness/common/rules/comm-skill-rule-ownership.md и comm-human-folder-guides.md. Отдельным rg --files --hidden --no-ignore .claude/rules перечисли Markdown без README.human.md; cat явно перечисленных правил максимум по два за вызов до INDEX common, INDEX project и любого SKILL. Не используй субагентов, внешние сервисы, установку зависимостей. Не сохраняй отчёты/новые файлы; разрешён только ответ и явно названные Git-операции. ')
 if a.invocation=='explicit' and a.stage!='baseline':prompt+='Примени $'+name+'. '
 prompt+=task
 wrapper,env=h.isolation(base,root);env.update(PYTHONDONTWRITEBYTECODE='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_CONFIG_NOSYSTEM='1')
 for key in list(env):
  if key.startswith(('GIT_AUTHOR_','GIT_COMMITTER_')):env.pop(key)
 r=h.run(wrapper+['codex','exec','--ephemeral','--ignore-user-config','--skip-git-repo-check','-s','danger-full-access','-C',str(root),'-c','features.multi_agent=false','--json',prompt],cwd=root,env=env,timeout=900)
 events=[]
 for line in r['stdout'].splitlines():
  try:events.append(json.loads(line))
  except ValueError:pass
 ga=state(root);after_agent=h.snapshot(root);checks=h.run(['python3','-B','tests/invariants.py'],cwd=root,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')) if a.kind in ['abort','reset-exact'] else None
 r.update(stage=a.stage,mode=a.mode,kind=a.kind,invocation=a.invocation,source=h.snapshot(source),tested_source=h.snapshot(root/'harness/common/skills'/name) if a.stage!='baseline' else None,startup=startup,truth=truth,task=task,before=before,after=after_agent,snapshot_phase='before_parent_behavior',git_before=gb,git_after=ga,parent_behavior=checks,completed=any(e.get('type')=='turn.completed' for e in events),usage=[e.get('usage') for e in events if e.get('type')=='turn.completed'],time=datetime.now(ZoneInfo('Europe/Minsk')).isoformat())
 r['final']='\n'.join(e.get('item',{}).get('text','') for e in events if e.get('item',{}).get('type')=='agent_message')
 with dest.open('x') as f:json.dump(r,f,ensure_ascii=False,indent=2)
 print(json.dumps({'file':dest.name,'completed':r['completed'],'code':r['exit_code'],'head_changed':gb['head']!=ga['head'],'final':r['final'][-1800:]},ensure_ascii=False))
