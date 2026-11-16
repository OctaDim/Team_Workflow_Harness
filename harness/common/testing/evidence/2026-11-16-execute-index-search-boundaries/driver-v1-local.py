import base64,hashlib,importlib.util,json,math,os,re,shutil,tempfile
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);source=Path(loc['source']);sp=importlib.util.spec_from_file_location('g',repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
def save(n,v):
 with (out/n).open('x') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
prior=json.loads((out/'before-source.json').read_text())['harness/common/INDEX.md'];old=base64.b64decode(prior['base64']).decode();new=source.read_text();prefix='Ищи по имени и содержимому категории';tail='Скиллы выбирай через нативные name/description;';assert old.split(prefix)[0]==new.split(prefix)[0];assert old[old.index(tail):]==new[new.index(tail):];assert new.count('README.human.md')==1 and 'на любой глубине' in new
links=[]
for match in re.finditer(r'\[[^\]]+\]\(([^)]+)\)',new):
 p=repo/'harness/common'/match.group(1);assert p.exists(),str(p);g.h.ordinary(p);links.append(str(p.relative_to(repo)))
before=g.protect();save('before.json',{'protected':before,'target_sha256':prior['sha256'],'candidate_sha256':digest(source)})
save('content-and-size.json',{'type':'existing navigation INDEX, not a new always-loaded rule/skill/plugin','rest_unchanged':True,'single_recursive_human_exclusion':True,'links_at_logical_target':links,'before':{'W':len(old.split()),'C':len(old),'utf8_bytes':len(old.encode()),'utf16_units':len(old.encode('utf-16-le'))//2},'candidate':{'W':len(new.split()),'C':len(new),'utf8_bytes':len(new.encode()),'utf16_units':len(new.encode('utf-16-le'))//2},'form':'reuse existing map; no new rule or lazy owner. Existing human/inbox/duplicate/evidence owners retain procedures. Rule-only repeats ownership; new lazy adds no independent result; rule+lazy has no demonstrated selection gap.','budget_classification':'Rule-specific W bands/exception gate N/A to a navigation map; no whole-startup cap exists. Generic stock estimate is recorded, but its deferred label does not change mandatory startup loading. No fake manifest/frontmatter/coverage.'})
for mode in ['common','both']:
 with tempfile.TemporaryDirectory(prefix='index-mode-') as d:
  root=Path(d);startup=g.h.prepare(root,mode,'baseline');project=g.h.snapshot(root/'harness/project');shutil.copyfile(source,root/'harness/common/INDEX.md');shutil.copyfile(repo/'pytest.ini',root/'pytest.ini')
  for rel in ['harness/common/inbox','harness/common/testing/evidence']:
   (root/rel).mkdir(parents=True,exist_ok=True)
   guide=repo/rel/'README.human.md'
   if guide.exists():shutil.copyfile(guide,root/rel/'README.human.md')
  previous=None
  for _ in range(2):
   r=g.h.run(['python3','-B','harness/common/checks/ensure_entrypoint_links.py'],cwd=root);assert r['exit_code']==0,r
   now=g.h.snapshot(root);assert previous is None or previous==now;previous=now
  assert all((root/p).exists() for p in links);r=g.h.run([g.PYTHON,'-m','pytest','-q'],cwd=root,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'),timeout=300);assert r['exit_code']==0,r['stdout'][-1500:]+r['stderr'];assert project==g.h.snapshot(root/'harness/project')
  save(f'prepublication-suite-{mode}.json',{'source_sha256':digest(source),'suite':r,'startup':startup,'project_preserved':True,'repeat_startup_unchanged':True,'logical_links_valid':True,'fixture_transfer':'Historical inbox/evidence bodies excluded; their required category directories/guides retained.'});print(mode,r['stdout'].splitlines()[-1],flush=True)
with tempfile.TemporaryDirectory(prefix='index-project-only-') as d:
 root=Path(d);shutil.copytree(repo/'harness/project',root/'harness/project');state=g.h.snapshot(root);r=g.h.run(['python3','-B',str(repo/'harness/common/checks/ensure_entrypoint_links.py')],cwd=root);assert r['exit_code']!=0 and state==g.h.snapshot(root);save('project-only-negative.json',{'refused_before_writes':True,'result':r})
assert before==g.protect()
