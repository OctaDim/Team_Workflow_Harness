import hashlib,json
from pathlib import Path

def snapshot(root):
 return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}

def items(record):
 found=[]
 for line in record['stdout'].splitlines():
  try:event=json.loads(line)
  except ValueError:continue
  if event.get('type')=='item.completed' and event.get('item',{}).get('type')=='command_execution':found.append(event['item'])
 return found

def bootstrap(repo,record,source,extra_skills=()):
 commands=items(record);outputs=[i.get('aggregated_output','') for i in commands]
 def pos(text):return [i for i,out in enumerate(outputs) if text.strip() in out]
 rules=[p.read_text() for p in (repo/'.claude/rules').rglob('*.md') if p.name!='README.human.md']
 texts={p:(repo/p).read_text() for p in ('harness/common/START.md','harness/project/START.md','harness/common/INDEX.md','harness/project/INDEX.md','harness/common/rules/comm-skill-rule-ownership.md','harness/common/rules/comm-human-folder-guides.md')}
 procedure_texts=[p.read_text() for p in (repo/'harness/common/skills').rglob('SKILL.md')]+[p.read_text() for p in source.rglob('*.md') if p.name!='README.human.md']+[Path(p).read_text() for p in extra_skills]
 first=min((i for t in procedure_texts for i in pos(t)),default=len(commands))
 valid=[]
 for i,cmd in enumerate(commands):
  if not all(s in cmd.get('command','') for s in ('rg --files','--no-ignore','.claude/rules')):continue
  if not all(any(j<i for j in pos(texts[p])) for p in ('harness/common/START.md','harness/project/START.md','harness/common/rules/comm-skill-rule-ownership.md','harness/common/rules/comm-human-folder-guides.md')):continue
  if not all(any(i<j<first for j in pos(t)) for t in rules):continue
  last=max(min(j for j in pos(t) if j>i) for t in rules)
  ci=[j for j in pos(texts['harness/common/INDEX.md']) if last<=j<first];pi=[j for j in pos(texts['harness/project/INDEX.md']) if last<=j<first]
  if ci and pi and ci[0]<=pi[0]:valid.append(i)
 human=[]
 # Programmatic body comparison returns only paths/booleans, never human text.
 for root in (repo/'harness/common',repo/'harness/project',source):
  for p in root.rglob('README.human.md'):
   if 'inbox' in p.relative_to(root).parts or 'evidence' in p.relative_to(root).parts:continue
   body=p.read_text().strip()
   if body and any(body in out for out in outputs):human.append(str(p.relative_to(repo)))
 return {'valid':bool(valid),'human_reads':human,'outputs':outputs,'commands':commands}
