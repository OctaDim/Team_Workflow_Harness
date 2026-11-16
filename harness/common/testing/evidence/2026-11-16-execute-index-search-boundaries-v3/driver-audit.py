import json,re
from pathlib import Path

def items(r):
 result=[]
 for line in r['stdout'].splitlines():
  try:e=json.loads(line)
  except ValueError:continue
  if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution':result.append(e['item'])
 return result

def bootstrap(repo,r):
 commands=items(r);outputs=[i.get('aggregated_output','') for i in commands]
 def pos(text):return [i for i,s in enumerate(outputs) if text.strip() in s]
 rules=[p.read_text() for p in (repo/'.claude/rules').rglob('*.md') if p.name!='README.human.md'];texts={p:(repo/p).read_text() for p in ['harness/common/START.md','harness/project/START.md','harness/project/INDEX.md','harness/common/rules/comm-skill-rule-ownership.md','harness/common/rules/comm-human-folder-guides.md']};procedures=[p.read_text() for p in (repo/'harness/common/skills').rglob('*.md') if p.name!='README.human.md'];first=min((i for t in procedures for i in pos(t)),default=len(commands));valid=[]
 for i,command in enumerate(commands):
  if not all(s in command.get('command','') for s in ['rg --files','--no-ignore','.claude/rules']):continue
  if not all(any(j<i for j in pos(texts[p])) for p in ['harness/common/START.md','harness/project/START.md','harness/common/rules/comm-skill-rule-ownership.md','harness/common/rules/comm-human-folder-guides.md']):continue
  if not all(any(i<j<first for j in pos(t)) for t in rules):continue
  last=max(min(j for j in pos(t) if j>i) for t in rules);ci=[j for j in pos(r['index_text']) if last<=j<=first];pi=[j for j in pos(texts['harness/project/INDEX.md']) if last<=j<=first]
  if ci and pi and ci[0]<=pi[0]:valid.append(i)
 return {'valid':bool(valid),'commands':commands,'outputs':outputs}

def content_reads(commands,path,marker=None):
 found=[];suffix='/'.join(Path(path).parts[-2:]);basename=Path(path).name
 for i,item in enumerate(commands):
  command=item.get('command','');output=item.get('aggregated_output','')
  literal=path in command or suffix in command
  read=bool(re.search(r'\b(?:cat|sed|head|tail|rg)\b|read_text|read_bytes|json\.load|open\(',command)) and '--files' not in command
  returned=bool(re.search(re.escape(suffix)+r':\d+:',output)) or bool(marker and marker in output)
  if item.get('exit_code')==0 and ((literal and read) or returned):found.append(i)
 return found
