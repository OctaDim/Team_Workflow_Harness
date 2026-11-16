import hashlib,importlib.util,json,os,shutil,tempfile
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v3.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);source=Path(loc['source']);skill=Path(loc['skill']);sp=importlib.util.spec_from_file_location('g',repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
def save(n,v):g.save(out/n,v)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads((out/'before-protected.json').read_text());assert g.protect()==before
result=json.loads((out/'skill-assessment-summary.json').read_text());text=source.read_text()
a=json.loads(json.loads((out/'rule-analyze.json').read_text())['stdout']);component=a['budgets']['deferred_cost_tokens']['components'];assert len(component)==1;T=component[0]['tokens'];assert T<=1000
assert (w/'assessment/rule-v3/comm-confirm-development-workflow.md').read_bytes()==source.read_bytes()
save('rule-budget.json',{'source_sha256':digest(source),'W':len(text.split()),'word_band':'moderate' if len(text.split())>150 else 'good','C':len(text),'UTF16_units':len(text.encode('utf-16-le'))//2,'T':T,'tool':a['tool'],'component':component[0],'stock_summary':a['summary'],'method':'Full unnormalized UTF8 rule, stock per-file estimate. Generic result is not skill/native proof; creator N/A for rule.','limits_preserved':True})
for mode in ['common','both']:
 with tempfile.TemporaryDirectory(prefix='workflow-suite-') as d:
  root=Path(d);startup=g.h.prepare(root,mode,'baseline');project=g.h.snapshot(root/'harness/project')
  for rel in ['harness/common/rules/comm-confirm-development-workflow.md','.claude/rules/comm-confirm-development-workflow.md']:shutil.copyfile(source,root/rel)
  for parent in ['harness/common/skills','.agents/skills','.claude/skills']:shutil.copytree(skill,root/parent/skill.name);assert g.h.snapshot(root/parent/skill.name)==g.h.snapshot(skill)
  shutil.copyfile(repo/'pytest.ini',root/'pytest.ini');previous=None
  for _ in range(2):
   r=g.h.run(['python3','-B','harness/common/checks/ensure_entrypoint_links.py'],cwd=root);assert r['exit_code']==0;now=g.h.snapshot(root);assert previous is None or previous==now;previous=now
  r=g.h.run([g.PYTHON,'-m','pytest','-q'],cwd=root,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'),timeout=300);assert r['exit_code']==0,r['stdout'][-1500:];assert project==g.h.snapshot(root/'harness/project');save(f'prepublication-suite-{mode}.json',{'rule_sha256':digest(source),'skill':g.h.snapshot(skill),'suite':r,'startup':startup,'project_preserved':True,'repeat_startup_unchanged':True,'copies_equal':True});print(mode,r['stdout'].splitlines()[-1],flush=True)
with tempfile.TemporaryDirectory(prefix='workflow-project-only-') as d:
 root=Path(d);shutil.copytree(repo/'harness/project',root/'harness/project');state=g.h.snapshot(root);r=g.h.run(['python3','-B',str(repo/'harness/common/checks/ensure_entrypoint_links.py')],cwd=root);assert r['exit_code']!=0 and state==g.h.snapshot(root);save('project-only-negative.json',{'refused_before_writes':True,'result':r})
assert before==g.protect();print('Rule W/T',len(text.split()),T,'skill',result['grade'],result['score'])
