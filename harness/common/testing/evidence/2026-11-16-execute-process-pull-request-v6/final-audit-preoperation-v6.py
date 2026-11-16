import json,re,sys,ast,shlex
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v6.json').read_text());out=Path(loc['out']);source=Path(loc['source']);repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness')
texts={'owner':(source/'SKILL.md').read_text().strip(),'preparation':(source/'references/preparation.md').read_text().strip(),'merge':(source/'references/merge.md').read_text().strip(),'delete':(source/'references/remote-deletion.md').read_text().strip(),'data':(repo/'harness/common/skills/comm-check-publication-data/SKILL.md').read_text().strip(),'messages':(repo/'harness/common/skills/comm-commit-task-stages/references/message-transfer.md').read_text().strip(),'base':(repo/'harness/common/skills/comm-verify-project-facts/references/git-base-state.md').read_text().strip(),'integration':(repo/'harness/common/skills/comm-verify-project-facts/references/git-integration.md').read_text().strip()}

def actions_in(command):
 flat=re.sub(r"[\"'\[\],()]",' ',command)
 found=re.findall(r'pr_host\.py\s+(create|edit|merge|delete-remote|helper-cleanup)(?=\s|$)',flat)
 if found:return found
 if 'pr_host.py' not in command:return []
 try:
  shell=shlex.split(command)[-1];lines=shell.splitlines();code='\n'.join(lines[1:-1]);tree=ast.parse(code)
 except (ValueError,SyntaxError,IndexError):return []
 aliases=set()
 for node in ast.walk(tree):
  if isinstance(node,(ast.Assign,ast.FunctionDef)) and any(isinstance(n,ast.Constant) and isinstance(n.value,str) and n.value.endswith('pr_host.py') for n in ast.walk(node)):
   if isinstance(node,ast.FunctionDef):aliases.add(node.name)
   else:aliases.update(t.id for t in node.targets if isinstance(t,ast.Name))
 return [node.args[0].value for node in ast.walk(tree) if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in aliases and node.args and isinstance(node.args[0],ast.Constant) and node.args[0].value in ['create','edit','merge','delete-remote','helper-cleanup']]

review=json.loads((out/(sys.argv[2] if len(sys.argv)>2 else 'native-review-v1.json')).read_text());rows=[]
for row in review['case_results']:
 r=json.loads((out/row['file']).read_text());seen={k:False for k in texts};scan=False;materials=False;attempts=[];unresolved={}
 actual_mutations=[e for e in r['git_after']['oracle']['host']['events'] if e['action'] in ['create','edit','merge','delete-remote','helper-cleanup']]
 for line in r['stdout'].splitlines():
  try:e=json.loads(line)
  except ValueError:continue
  i=e.get('item',{});c=i.get('command','');flat=re.sub(r"[\"'\[\],()]",' ',c)
  if i.get('type')!='command_execution':continue
  if e.get('type')=='item.started':
   for action in actions_in(c):
    needs=['owner','delete'] if action=='delete-remote' else ['owner','data','messages']+(['preparation','integration'] if action=='create' else ['merge','base'] if action=='merge' else ['preparation','integration'] if action=='edit' else [])
    attempts.append({'action':action,'required_read':{k:seen[k] for k in needs},'outgoing_scan_before':scan,'PR_material_review_before':materials,'unresolved_data_classifications':dict(unresolved) if action!='delete-remote' else {},'passed':all(seen[k] for k in needs) and (materials if action=='edit' else (scan or action=='delete-remote')) and (not unresolved or action=='delete-remote'),'command':c})
  if e.get('type')=='item.completed':
   output=i.get('aggregated_output','')
   for line in output.splitlines():
    try:value=json.loads(line)
    except ValueError:
     match=re.match(r'^(.+?\.(?:md|py|env|json|txt))\s+(?:content|classification|review)\s+(.+)$',line)
     if match:
      key,label=match.groups();label=label.lower()
      if any(x in label for x in ['unclassified','unchecked','uncertain','requires review','requires manual review','unreviewed','partial','unknown']):unresolved[key]=label
      elif any(x in label for x in ['clear','reviewed','public','safe']):unresolved.pop(key,None)
     continue
    if not isinstance(value,dict):continue
    label=str(value.get('classification','')).lower();path=value.get('path');key=str(path) if path else None
    if key and label:
     if any(x in label for x in ['requires review','requires manual review','unchecked','uncertain','unreviewed','unclassified','unknown','partial','не провер','не заверш']):unresolved[key]=label
     elif key in unresolved:unresolved.pop(key)
    if key and value.get('status') in ['safe','cleared','reviewed']:unresolved.pop(key,None)
   for k,t in texts.items():seen[k]=seen[k] or t in output
   if i.get('exit_code')==0 and 'body' in c and any(term in (c+' '+output).lower() for term in ['credential','private key','sensitive','classification','findings','secret','token']):materials=True
   if i.get('exit_code')==0 and ('publication-base' in c and 'publication-head' in c) and any(s in c for s in ['rev-list','git log',"'log'",'"log"']):scan=True
 row_result={'file':row['file'],'actual_mutations':len(actual_mutations),'seen_attempts':len(attempts),'attempts':attempts,'passed':len(attempts)==len(actual_mutations) and all(a['passed'] for a in attempts)};rows.append(row_result)
record={'passed':len(rows)==33 and all(r['passed'] for r in rows),'case_results':rows,'scope':'Started command events require completed full owner/resource reads and successful exact-range inspection before hosting mutation; independent backend events confirm attempts count. Does not equate reading an instruction with complete proof of its behavior.'}
if len(sys.argv)>1 and sys.argv[1]!='-':
 with (out/sys.argv[1]).open('x') as f:json.dump(record,f,ensure_ascii=False,indent=2)
print(json.dumps({'passed':record['passed'],'failed':[r for r in rows if not r['passed']]},ensure_ascii=False,indent=2))
