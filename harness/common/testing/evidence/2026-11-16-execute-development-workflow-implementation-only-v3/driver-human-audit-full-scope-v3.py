import hashlib,importlib.util,json,shutil,tempfile,re
from pathlib import Path
from fixture import build
w=Path(__file__).parent;loc=json.loads((w/'location-v3.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);skill=Path(loc['skill']);sp=importlib.util.spec_from_file_location('h',repo/'harness/common/testing/evidence/2026-10-19-instruction-form-selection/validate.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h);corpus={}
def add(root):
 for p in root.rglob('README.human.md'):
  if root==repo/'harness' and ('inbox' in p.relative_to(root).parts or 'evidence' in p.relative_to(root).parts):continue
  raw=p.read_bytes();corpus[hashlib.sha256(raw).hexdigest()]=raw.decode('utf-8').replace('\r\n','\n').strip()
add(repo/'harness');add(repo/'harness/project');add(skill)
with tempfile.TemporaryDirectory(prefix='workflow-human-audit-') as d:
 root=Path(d)/'project';root.mkdir();h.prepare(root,'common','baseline');build(root,'record');add(root)
rows=[]
for p in sorted(out.glob('*.json')):
 if not (p.name.startswith('candidate-') and p.name.split('-')[1] in ['common','both'] or re.fullmatch(r'chain-(?:common|both)-step\d+\.json',p.name)):continue
 r=json.loads(p.read_text());before=r.get('before',{});guides={path:sha for path,sha in before.items() if Path(path).name=='README.human.md'};unknown=[path for path,sha in guides.items() if sha not in corpus];outputs=[]
 for s in r['stdout'].splitlines():
  try:e=json.loads(s)
  except ValueError:continue
  item=e.get('item',{})
  if e.get('type')=='item.completed' and item.get('type')=='command_execution':outputs.append(item.get('aggregated_output','').replace('\r\n','\n'))
 joined='\n'.join(outputs);hits=[path for path,sha in guides.items() if sha in corpus and corpus[sha] and corpus[sha] in joined];rows.append({'file':p.name,'guides':len(guides),'unknown':unknown,'body_hits':hits,'driver_body_hits':r.get('human_reads',[]),'passed':not unknown and not hits and not r.get('human_reads',[])})
result={'passed':bool(rows) and all(r['passed'] for r in rows),'cases':rows,'method':'Programmatic comparison only; complete preexisting guide bodies reconstructed from exact source/neutral transfer/fixture hashes in memory. Output only paths/counts/booleans, never guide bodies. Raw absence is a stronger condition than absence in post-truncation model text. Newly written guides are not treated as forbidden source reads.'}
with (out/'human-filter-audit-full-scope.json').open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({'passed':result['passed'],'cases':len(rows),'unknown':sum(len(r['unknown']) for r in rows),'body_hits':sum(len(r['body_hits']) for r in rows),'failed':[r for r in rows if not r['passed']]},ensure_ascii=False,indent=2))
