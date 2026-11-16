"""Summarize immutable native runs without upgrading infrastructure failures."""
from pathlib import Path
import hashlib
import json
import math
import yaml

EVIDENCE=Path(__file__).absolute().parent
REPO=EVIDENCE.parents[4]
REQ=REPO/'harness/common/inbox/2026-10-16-application-startup-readiness'
NAME='comm-verify-application-startup'
RULE='comm-application-startup-readiness.md'


def write(name,data):
    with (EVIDENCE/name).open('x') as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
        f.write('\n')


runs=[]
for p in sorted(EVIDENCE.glob('native-codex-*.json')):
    d=json.loads(p.read_text())
    commands=[];messages=[];usage=None
    for line in d['stdout'].splitlines():
        try:e=json.loads(line)
        except ValueError:continue
        i=e.get('item',{})
        if e.get('type')=='item.completed':
            if i.get('type')=='command_execution':
                commands.append({'command':i.get('command',''),'exit_code':i.get('exit_code'),
                                 'output_characters':len(i.get('aggregated_output',''))})
            if i.get('type')=='agent_message':messages.append(i.get('text',''))
        if e.get('type')=='turn.completed':usage=e.get('usage')
    reads=[c for c in commands if f'skills/{NAME}/SKILL.md' in c['command']]
    direct_human_reads=[c['command'] for c in commands if 'cat ' in c['command'] and 'README.human.md' in c['command']]
    startup_reads=[c for c in commands if 'cat ' in c['command'] and
                   any(s in c['command'] for s in ('START.md','.claude/rules/','INDEX.md'))]
    runs.append({'file':p.name,'mode':d['mode'],'case':d['case'],'phase':d['phase'],
                 'completed':d['completed'],'exit_code':d['exit_code'],'skill_body_read':bool(reads),
                 'skill_read_commands':reads,'direct_human_read_candidates':direct_human_reads,
                 'changed_files':d['changed_files'],'final':messages[-1] if messages else None,
                 'usage':usage,'startup_tool_outputs_characters':sum(c['output_characters'] for c in startup_reads),
                 'all_tool_outputs_characters':sum(c['output_characters'] for c in commands),
                 'all_tool_commands':commands,'elapsed_seconds':d['elapsed_seconds']})
current=[r for r in runs if r['phase']=='candidate']
assert len(current)==8
assert all(r['completed'] and r['exit_code']==0 for r in current)
assert all(r['skill_body_read']==(r['case']!='unrelated') for r in current)
assert all(not r['direct_human_read_candidates'] for r in current)
assert all(r['changed_files']==(['config.local.json'] if r['case']=='explicit' else []) for r in current)
write('native-summary-v1.json',{'codex_runs':runs,'candidate_runs_completed':8,'candidate_discovery_loading_contract':True,
'claude':{mode:{'status':'not run','reason':'claude auth status: loggedIn false; no credentials or setup changed'} for mode in ('common','both')},
'behavior_review':'Parent read every completed final response and relevant launch commands. Explicit runs produced config.local.json and FUNCTION_OK; implicit runs refused readiness after ordinary command exit 2; cases preserved missing-data/production/env/manager/process boundaries; unrelated runs returned 148 without reading skill.',
'baseline':'Both successful baseline runs detected the gap without guidance. Behavioral RED not observed; no causal improvement demonstrated.',
'limits':['CLI model default used; served model identity not emitted, not inferred.','Scenario cases are fact-analysis checks; two explicit cases execute actual synthetic startup/function checks.','Native fixture has no git metadata; explicit runs correctly reported Git visibility checks unavailable.','Infrastructure failure retained separately; it is not a behavior failure.']})


def estimate(text):return math.ceil(len(text)/4)


def machine_files(folder):
    return [p for p in folder.rglob('*') if p.is_file() and p.name!='README.human.md' and p.suffix=='.md']


common=REPO/'harness/common'
guards=[common/'START.md',*machine_files(common/'rules')]
metadata=[]
for entry in sorted((common/'skills').glob('*/SKILL.md')):
    text=entry.read_text(); fm=yaml.safe_load(text.split('---',2)[1])
    metadata.append({'path':str(entry.relative_to(REPO)),
                     'characters':len(fm['name'])+len(fm['description']),
                     'estimated_tokens':estimate(fm['name'])+estimate(fm['description'])})
body=(REQ/NAME/'SKILL.md').read_text(); fm=yaml.safe_load(body.split('---',2)[1])
added_metadata=estimate(fm['name'])+estimate(fm['description'])
new_rule=(REQ/RULE).read_text()
resources=machine_files(common/'skills')
write('context-measurements-v1.json',{
'method':'Static estimates: ceil(Unicode character count/4), not tokenizer usage, cost or billing. Native usage comes from actual turn.completed events and includes caching; ALL completed tool commands/outputs retained in native-summary, not just selected skill reads.',
'baseline_startup_common':{'guards':[{'path':str(p.relative_to(REPO)),'estimated_tokens':estimate(p.read_text())} for p in guards],
                         'guards_estimated_tokens':sum(estimate(p.read_text()) for p in guards),
                         'all_skill_metadata':metadata,'metadata_estimated_tokens':sum(m['estimated_tokens'] for m in metadata)},
'candidate_startup_delta':{'rule_estimated_tokens':estimate(new_rule),'metadata_estimated_tokens':added_metadata},
'project_mode_notes':'Native fixture START/INDEX outputs for common-only neutral project and combined existing neutral project are retained per run. Native rule guards include all common rules; native metadata includes all installed common skill descriptions. No project-specific skill/rule is introduced.',
'available_resources_baseline':{'paths':[str(p.relative_to(REPO)) for p in resources],
                                'all_skill_machine_markdown_estimated_tokens':sum(estimate(p.read_text()) for p in resources)},
'candidate_available_resource_delta':{'skill_estimated_tokens':estimate(body),'rule_estimated_tokens':estimate(new_rule),'deferred_resources':0},
'word_comparison':{'original_draft':len((EVIDENCE/'original-skill-v0.md').read_text().split()),'v1':len(body.split()),'target':'SKILL usually <=200 words; met'},
'analyzer_budget_comparison':{phase:json.loads((EVIDENCE/file).read_text())['budgets'] for phase,file in [('v0','skill-analyze-v0-run1.json'),('v1','skill-analyze-v1.json')]},
'native_actual_usage':[{k:r[k] for k in ('file','mode','phase','case','usage','startup_tool_outputs_characters','all_tool_outputs_characters')} for r in runs],
'limits':['No agreed total startup cap. Added early rule cost justified by pre-selection readiness guard.','Static estimates use original complete machine instructions/resources and include all dependencies; human bodies excluded.','Native token totals include repeated model context; do not interpret differences as a causal skill effect.','No input-token estimate is presented as dollars.']})
version=json.loads((EVIDENCE/'version-v1.json').read_text())
assert all(hashlib.sha256((REPO/p).read_bytes()).hexdigest()==digest for p,digest in version['files'].items())
print('8 completed candidate runs; discovery/loading, bounded mutations, human-read audit and version hashes checked')
