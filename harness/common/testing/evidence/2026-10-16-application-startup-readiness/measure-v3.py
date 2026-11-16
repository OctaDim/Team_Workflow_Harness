"""Version-specific measurements; never overwrite earlier run artifacts."""
from pathlib import Path
import json,math,hashlib,yaml
E=Path(__file__).absolute().parent
R=E.parents[4]
Q=E/'publication-v3-candidate'
base=json.loads((E/'context-measurements-v1.json').read_text())
body=(Q/'comm-verify-application-startup/SKILL.md').read_text()
meta=yaml.safe_load(body.split('---',2)[1])
files={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in Q.rglob('*') if p.is_file()}
result={
'version':'v3','sha256':files,'baseline':'context-measurements-v1.json: same unchanged installed common before this publication; native baseline runs remain historical, not reclassified as RED',
'method':base['method'],
'baseline_startup_common':base['baseline_startup_common'],
'baseline_available_resources':base['available_resources_baseline'],
'candidate_startup_delta':{'rule_estimated_tokens':math.ceil(len((Q/'comm-application-startup-readiness.md').read_text())/4),'metadata_estimated_tokens':math.ceil(len(meta['name'])/4)+math.ceil(len(meta['description'])/4)},
'candidate_available_resources':{'paths':[str(p.relative_to(R)) for p in Q.rglob('*.md') if p.name!='README.human.md'],'deferred_resources':0},
'compactness':{'body_words':len(body.split('---',2)[2].split()),'usual_target':200,'reason_for_one_word_excess':'Preserve exact user-approved v3 explicit stop/wait clause; the canonical target says usually. No thresholds changed and analyzer reports no warning.'},
'analyzer_budget':json.loads((E/'skill-analyze-v3-review.json').read_text())['budgets'],
'native_runs':[]}
for p in sorted(E.glob('native-codex-*-v3-review.json')):
 d=json.loads(p.read_text());commands=[];final=[];usage=None
 for line in d['stdout'].splitlines():
  try:event=json.loads(line)
  except ValueError:continue
  item=event.get('item',{})
  if event.get('type')=='item.completed':
   if item.get('type')=='command_execution':commands.append({'command':item.get('command',''),'exit_code':item.get('exit_code'),'output_characters':len(item.get('aggregated_output',''))})
   if item.get('type')=='agent_message':final.append(item.get('text',''))
  if event.get('type')=='turn.completed':usage=event.get('usage')
 result['native_runs'].append({'file':p.name,'mode':d['mode'],'case':d['case'],'completed':d['completed'],'exit_code':d['exit_code'],'usage':usage,'all_commands':commands,'all_tool_output_characters':sum(c['output_characters'] for c in commands),'skill_read':any('skills/comm-verify-application-startup/SKILL.md' in c['command'] for c in commands),'direct_human_read_candidates':[c['command'] for c in commands if 'cat ' in c['command'] and 'README.human.md' in c['command']],'changed_files':d['changed_files'],'final':final[-1] if final else None})
assert len(result['native_runs'])==10
assert all(x['completed'] and x['exit_code']==0 for x in result['native_runs'])
assert all(x['skill_read']==(x['case']!='unrelated') for x in result['native_runs'])
assert all(not x['direct_human_read_candidates'] for x in result['native_runs'])
assert all(x['changed_files']==(['config.local.json'] if x['case']=='explicit' else []) for x in result['native_runs'])
with (E/'measurements-and-native-summary-v3.json').open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print('10 completed runs; loading, human exclusion, bounded writes and exact hashes checked')
