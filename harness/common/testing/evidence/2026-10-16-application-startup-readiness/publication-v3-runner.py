from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json,os,subprocess
root=Path('/home/octadim/MyProjects/Multi_User_RAG_Assist_System')
e=root/'harness/common/testing/evidence/2026-10-16-application-startup-readiness'
plan=json.loads((e/'publication-plan-v3.json').read_text())

def ordinary(path):
 for p in (path,*path.parents):
  if p.is_symlink():raise RuntimeError(f'Symlink: {p}')

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def state(folder):
 result={}
 for d,dirs,files in os.walk(folder,followlinks=False):
  for n in dirs+files:ordinary(Path(d)/n)
  for n in files:
   p=Path(d)/n;result[str(p.relative_to(folder))]=digest(p)
 return result

ordinary(root)
state(root/'harness')
summary=json.loads((e/'measurements-and-native-summary-v3.json').read_text())
assert len(summary['native_runs'])==10 and all(r['completed'] and r['exit_code']==0 for r in summary['native_runs'])
assert all(r['exit_code']==0 for r in json.loads((e/'static-commands-v3-review.json').read_text()))
for kind in ('skill','rule'):
 a=json.loads((e/f'{kind}-analyze-v3-review.json').read_text())
 assert a['summary']['grade']=='A' and a['summary']['checkCounts']['error']==0
for item in plan['transfers']:
 src=root/item['source'];dst=root/item['target']
 ordinary(src);ordinary(dst)
 assert digest(src)==item['sha256'],f'Changed source: {src}'
 assert not dst.exists(),f'Target collision: {dst}'
 assert subprocess.run(['git','check-ignore','--no-index','--',item['target']],cwd=root,capture_output=True).returncode==1
candidate=root/'harness/common/inbox/2026-10-16-application-startup-readiness/comm-verify-application-startup/SKILL.md'
assert digest(candidate)=='f94252cf1f55f21c5a8ee2637e4d1e0d0905ed32556c701d25425cbfea4b0c68'
project_before=state(root/'harness/project')
protected_before={name:digest(root/name) for name in ('AGENTS.md','CLAUDE.md','.gitignore')}
installed=[]
for item in sorted(plan['transfers'],key=lambda i:(Path(i['target']).name!='README.human.md',i['target'])):
 src=root/item['source'];dst=root/item['target'];ordinary(dst)
 dst.parent.mkdir(parents=True,exist_ok=True)
 with dst.open('xb') as f:f.write(src.read_bytes())
 assert digest(dst)==item['sha256']
 installed.append({'path':item['target'],'sha256':digest(dst)})
assert state(root/'harness/project')==project_before
assert {name:digest(root/name) for name in protected_before}==protected_before
for src in (root/'harness/common/rules').glob('comm-*.md'):
 assert src.read_bytes()==(root/'.claude/rules'/src.name).read_bytes(),src
source_names={p.name for p in (root/'harness/common/rules').glob('comm-*.md')}
native_names={p.name for p in (root/'.claude/rules').glob('comm-*.md')}
assert source_names==native_names
for folder in ('harness/common/skills','.agents/skills','.claude/skills'):
 assert state(root/folder/'comm-verify-application-startup')==state(root/'harness/common/skills/comm-verify-application-startup')
record={'version':'v3','time':datetime.now(ZoneInfo('Europe/Minsk')).isoformat(timespec='seconds'),
'authorization':'User answered yes to the separate exact unverified-v3 publication question in this chat.',
'installed':installed,'full_common_rule_set_equal':True,'all_skill_folder_copies_equal':True,
'project_preserved':True,'protected_inputs_preserved':protected_before,'codex_status':'passed in tested scope','claude_status':'unverified','overall_status':'unverified'}
with (e/'publication-v3-result.json').open('x') as f:json.dump(record,f,ensure_ascii=False,indent=2)
print('Published exact v3: 8 files; full rule set and skill copies equal; project/entrypoints preserved')
