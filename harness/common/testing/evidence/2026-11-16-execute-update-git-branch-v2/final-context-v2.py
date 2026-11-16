from pathlib import Path
import json,hashlib
repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=repo/'harness/common/testing/evidence/2026-11-16-execute-update-git-branch-v2';source=repo/'harness/common/inbox/2026-11-14-05-update-git-branch/candidate-v2/comm-update-git-branch'
guards=[repo/'AGENTS.md',repo/'harness/common/START.md',repo/'harness/project/START.md',*sorted((repo/'.claude/rules').rglob('*.md')),repo/'harness/common/INDEX.md',repo/'harness/project/INDEX.md'];guards=[p for p in guards if p.name!='README.human.md']
skills=[p for p in (repo/'harness/common/skills').glob('*/SKILL.md') if p.parent.name!=source.name]+[source/'SKILL.md'];resources=[p for p in (repo/'harness/common/skills').rglob('*.md') if p.name not in ['SKILL.md','README.human.md'] and source.name not in p.parts]+[p for p in source.rglob('*.md') if p.name not in ['SKILL.md','README.human.md']]
def record(p):
 t=p.read_text();return {'path':str(p.relative_to(repo)),'chars':len(t),'estimated_char_quarter':(len(t)+3)//4}
metadata=[]
for p in skills:
 front=p.read_text().split('---',2)[1];metadata.append({'path':str(p.relative_to(repo)),'chars':len(front)})
static={}
static['baseline']={'trigger':0,'invoke':0,'deferred':0,'total':0,'reason':'new owner absent'}
for stage,prefix in [('candidate','local')]:
 d=json.loads(json.loads((out/f'{prefix}-comm-update-git-branch-analyze.json').read_text())['stdout']);static[stage]={k:d['budgets'][k+'_cost_tokens']['value'] for k in ['trigger','invoke','deferred']};static[stage]['total']=d['budgets']['total_tokens']['value']
context={'method':'Unicode characters, char/4 estimates; metadata, startup guards and all available logical machine resources separate from actual per-run reads/usage. No exact skill-only token attribution. No human-guide bodies read.','startup_guards':[record(p) for p in guards],'metadata':metadata,'available_resources':[record(p) for p in skills+resources],'target_static':static,'target_references':{str(p.relative_to(source)):(len(p.read_text())+3)//4 for p in source.rglob('*.md') if p.name not in ['SKILL.md','README.human.md']},'actual_reads_usage':'Raw native traces and native-review-v1.json retain actual complete returned bodies, command-output sizes and unmodified session usage; includes startup and any repeated/dependency reads.'}
with (out/'context-accounting.json').open('x') as f:json.dump(context,f,ensure_ascii=False,indent=2)
print(static)
