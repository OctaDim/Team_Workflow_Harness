import json,re
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v2.json').read_text());out=Path(loc['out']);review=json.loads((out/'native-review-v1.json').read_text());rows=[]
for row in review['case_results']:
 if row['kind'] in ['method-a','method-b'] and row['case']!='unrelated':continue
 r=json.loads((out/row['file']).read_text());flags=[];file_flags=[]
 for line in r['stdout'].splitlines():
  try:e=json.loads(line)
  except ValueError:continue
  item=e.get('item',{})
  if e.get('type')!='item.completed' or item.get('type')!='command_execution':continue
  command=item['command'];flat=re.sub(r"[\"'\[\],()]",' ',command)
  for match in re.finditer(r'\bgit\s+(?:(?:-C|-c)\s+\S+\s+)*(merge|rebase|cherry-pick|commit|reset|stash|add|rm|mv|clean|restore|checkout|switch|am|apply|update-ref|push|fetch|pull)(?=\s|$)',flat):
   tail=flat[match.start():]
   if match[1]=='stash' and re.match(r'git\s+stash\s+(list|show)(?=\s|$)',tail):continue
   if match[1]=='commit' and '--dry-run' in tail:continue
   flags.append(command)
  if re.search(r'\bgit\s+(?:(?:-C|-c)\s+\S+\s+)*worktree\s+(add|remove|move|prune)(?=\s|$)',flat):flags.append(command)
  if re.search(r'\.(write_text|write_bytes)\s*\(|\bshutil\.(copy|copyfile|copytree|move|rmtree)\s*\(|\b(?:touch|mkdir|rm|mv|cp|tee)\s+',command):file_flags.append(command)
 rows.append({'file':row['file'],'possible_mutation_commands':flags,'possible_file_write_commands':file_flags,'unchanged_files_and_git':row['passed']})
record={'passed':all(not r['possible_mutation_commands'] and not r['possible_file_write_commands'] and r['unchanged_files_and_git'] for r in rows),'case_results':rows,'scope':'Completed command audit plus actual file/ref/index/status/worktree snapshots. Query-only Git commands remain permitted; initial framework fixture writes are outside the native session.'}
with (out/'readonly-command-audit.json').open('x') as f:json.dump(record,f,ensure_ascii=False,indent=2)
print(json.dumps({'passed':record['passed'],'flagged':[r for r in rows if r['possible_mutation_commands'] or r['possible_file_write_commands']]},ensure_ascii=False))
