import ast,collections,configparser,hashlib,json,re,shlex,sys,tomllib
from pathlib import Path
sys.path.insert(0,'/tmp');from native_audit_helpers_20261115 import bootstrap,snapshot
w=Path(__file__).parent;loc=json.loads((w/'location-v2.json').read_text());repo=Path(loc['repo']);out=Path(loc['out']);req=Path(loc['request']);code=Path(loc['code']);sources={n:req/'candidate-v2'/n for n in ['comm-install-harness','comm-process-harness-inbox']};expected={n:snapshot(p) for n,p in sources.items()};impl=json.loads((out/'before-v2.json').read_text())['implementation']
jobs=[('current2-install-pyproject','common','install','explicit'),('current2-install-tox','common','install','implicit'),('current2-install-ini','both','install','explicit'),('current2-install-setup','both','install','implicit'),('current2-execution','common','execution','explicit'),('current2-execution','both','execution','implicit'),('current2-creation','common','creation','implicit'),('current2-creation','both','creation','explicit'),('current2-target','common','target','explicit'),('current2-target','both','target','explicit'),('current2-unrelated','common','unrelated','unrelated'),('current2-unrelated','both','unrelated','unrelated')]
def config_data(text,name):
 if name=='pyproject.toml':return tomllib.loads(text)['tool']['pytest']['ini_options']
 c=configparser.ConfigParser();c.read_string(text);return dict(c['tool:pytest' if name=='setup.cfg' else 'pytest'])
def tokens(value):return value if isinstance(value,list) else shlex.split(value)
def preserved_config(r):
 before=config_data(r['config_before'],r['config']);after=config_data(r['config_after'],r['config']);oldopts=tokens(before.get('addopts',''));opts=tokens(after.get('addopts',''));paths=tokens(after.get('testpaths',''))
 others=all(k in after and after[k]==v for k,v in before.items() if k not in ['testpaths','addopts']);no_other_keys=set(after)-set(before)<=set(['testpaths','addopts']);kept=all(opt in opts for opt in oldopts);ignore=[];bad=[]
 for i,opt in enumerate(opts):
  if opt.startswith('--ignore='):ignore.append(opt.split('=',1)[1])
  elif opt=='--ignore' and i+1<len(opts):ignore.append(opts[i+1])
  if opt in ['-k','-m','--collect-only','--deselect'] or opt.startswith(('--ignore-glob','--deselect=')):bad.append(opt)
 expected_ignores={'harness/common/inbox','harness/project/inbox'}
 normalized=set()
 for item in ignore:
  p=Path(item)
  if p.is_absolute():
   # Absolute equivalents end at the exact two named inbox roots.
   for expected_path in expected_ignores:
    if str(p).endswith('/'+expected_path):normalized.add(expected_path);break
   else:normalized.add(str(p))
  else:normalized.add(str(p).rstrip('/'))
 return {'other_settings':others and no_other_keys,'existing_options':kept,'root_scope':not paths or paths==['.'],'no_positional_root_addopts':'.' not in opts,'only_two_ignores':normalized==expected_ignores,'no_filters':not bad,'receiving_comment':'# preserve receiving note' in r['config_after'],'no_shadow':r['config']=='pytest.ini' or not r['pytest_ini_after']}

def executes_test(command):
 try:
  shell=shlex.split(command)[-1];lines=shell.splitlines();head=shlex.split(lines[0])
 except (ValueError,IndexError):return False
 while head and ('=' in head[0] or head[0]=='env'):head.pop(0)
 if not head:return False
 executable=Path(head[0]).name
 if executable.startswith('pytest'):return True
 if not executable.startswith('python'):return False
 if '-m' in head and head.index('-m')+1<len(head) and head[head.index('-m')+1] in ['pytest','py_compile','compileall']:return True
 if any(arg.endswith('run_tests.py') for arg in head[1:]):return True
 try:
  code=head[head.index('-c')+1] if '-c' in head else '\n'.join(lines[1:-1])
  tree=ast.parse(code)
 except (ValueError,IndexError,SyntaxError):return False
 for node in ast.walk(tree):
  if not isinstance(node,ast.Call):continue
  if isinstance(node.func,ast.Attribute) and isinstance(node.func.value,ast.Name):
   if node.func.value.id=='pytest' and node.func.attr=='main':return True
   if node.func.value.id=='subprocess' and node.func.attr in ['run','call','check_call','check_output','Popen'] and node.args and isinstance(node.args[0],(ast.List,ast.Tuple)):
    values=[n.value for n in node.args[0].elts if isinstance(n,ast.Constant) and isinstance(n.value,str)]
    if 'pytest' in values or any(v.endswith('run_tests.py') for v in values):return True
 return False

rows=[]
for tag,mode,case,invocation in jobs:
 file=out/f'{tag}-{mode}-{invocation}.json'
 if not file.exists():continue
 r=json.loads(file.read_text());extras=[p for name,s in sources.items() if name!='comm-install-harness' for p in s.rglob('*.md') if p.name!='README.human.md'];boot=bootstrap(repo,r,sources['comm-install-harness'],extras);outputs='\n'.join(boot['outputs']);commands='\n'.join(i['command'] for i in boot['commands']);loaded={name:{str(p.relative_to(source)):p.read_text().strip() in outputs for p in source.rglob('*.md') if p.name!='README.human.md'} for name,source in sources.items()};observed=r['observed'];groups={pid:[e for e in observed if e['pid']==pid] for pid in {e['pid'] for e in observed}};active=set(r['active']);arch=set(r['archived']);full=[pid for pid,es in groups.items() if collections.Counter(e['case'] for e in es if e['kind']=='run')==collections.Counter(active) and collections.Counter(e['case'] for e in es if e['kind']=='import')==collections.Counter(active)]
 checks={'completed':r['completed'] and r['exit_code']==0,'source':r['source']==expected,'implementation':r.get('implementation')==impl,'implementation_version':r.get('implementation_version')=='implementation-v2','bootstrap':boot['valid'],'human_exclusion':not boot['human_reads'],'project_preserved':r['project_before']==r['project_after']}
 changed={p for p,v in r['before'].items() if r['after'].get(p)!=v};created=set(r['after'])-set(r['before']);allowed={r['config']} if case in ['install','execution'] else set()
 if case=='execution':allowed.add('harness/common/inbox/2026-11-16-validation/request.md')
 checks['only_authorized_changes']=changed<=allowed
 if case=='creation':checks['creation_scope']=all(p.startswith('harness/common/inbox/2026-11-16-run-durations/') for p in created)
 elif case=='execution':checks['report_scope']=all(p.startswith('harness/common/testing/evidence/2026-11-16-validation/') for p in created)
 else:checks['no_extra_files']=not created
 if case in ['install','execution']:
  checks.update(preserved_config(r));checks['actual_full_execution']=bool(full);checks['no_inbox_imports']=not any(e['case'] in arch for e in observed);checks['testing_resource']=loaded['comm-install-harness']['references/testing.md'];oracle=r.get('parent_collection_oracle',{});checks['independent_full_discovery']=oracle.get('exit_code')==0 and 'late_active/test_future.py::test_contract' in oracle.get('stdout','') and not any('/inbox/' in line.split('::',1)[0] for line in oracle.get('stdout','').splitlines() if '::' in line)
  if case=='install':checks['install_owner']=loaded['comm-install-harness']['SKILL.md'];checks['both_commands']=bool(re.search(r'(?:python|python3)\s+[^\n]*scripts/run_tests\.py',commands)) and '-m pytest' in commands
  else:
   checks['inbox_owner']=loaded['comm-process-harness-inbox']['SKILL.md'] and loaded['comm-process-harness-inbox']['references/workflow.md'];checks['targeted_and_full']=bool(full) and any({e['case'] for e in es if e['kind']=='run'}=={'application','receiving-spec'} for es in groups.values())
 elif case=='creation':
  checks.update(inbox_owner=loaded['comm-process-harness-inbox']['SKILL.md'],workflow=loaded['comm-process-harness-inbox']['references/workflow.md'],no_execution=not observed and not any(executes_test(i.get('command','')) for i in boot['commands']))
  bodies={p:__import__('base64').b64decode(data).decode('utf-8') for p,data in r['created_files'].items() if not p.endswith('README.human.md')};requests=[v for p,v in bodies.items() if p.endswith('/request.md')];candidates=[v for p,v in bodies.items() if p.endswith('run_tests.py')];checks['full_created_request']=len(requests)==1 and bool(re.search(r'Status\s*:\s*new',requests[0],re.I)) and any(x in requests[0].lower() for x in ['not executed','не выполн','не исполн','не запуск']);checks['complete_candidate']=bool(candidates) and any('--durations' in b and '10' in b and 'subprocess' in b for b in candidates)
 elif case=='target':
  checks['only_explicit_target']=collections.Counter(e['case'] for e in observed if e['kind']=='run')=={'historical-candidate':1} and collections.Counter(e['case'] for e in observed if e['kind']=='import')=={'historical-candidate':1};checks['testing_resource']=loaded['comm-install-harness']['references/testing.md'];checks['honest_failure']=any(x in r['final'].lower() for x in ['failed','упал','падает','не прой','провал','ошиб']) and ('1' in r['final']);checks['config_unchanged']=r['config_before']==r['config_after']
 else:checks.update(unrelated_nonloading=not any(any(v.values()) for v in loaded.values()),no_execution=not observed,correct_answer='184' in r['final'],files_unchanged=r['before']==r['after'])
 rows.append({'file':file.name,'case':case,'mode':mode,'invocation':invocation,'passed':all(checks.values()),'checks':checks,'loaded':loaded,'full_pytest_processes':full,'tool_output_chars':sum(map(len,boot['outputs'])),'usage':r['usage']})
result={'source':expected,'implementation':impl,'Codex':'passed' if len(rows)==12 and all(r['passed'] for r in rows) else 'incomplete/failed','case_results':rows}
if len(sys.argv)>1:
 with (out/sys.argv[1]).open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({'Codex':result['Codex'],'cases':len(rows),'failed':[{'file':r['file'],'checks':[k for k,v in r['checks'].items() if not v]} for r in rows if not r['passed']]},ensure_ascii=False,indent=2))
