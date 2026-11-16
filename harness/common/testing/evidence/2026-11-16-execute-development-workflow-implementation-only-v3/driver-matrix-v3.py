import concurrent.futures,json,subprocess
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v3.json').read_text());out=Path(loc['out']);cases=['audit','diagnose','proposal','record','scope-explanation','implement-code','implement-file','implement-config','implement-dependency','implement-external','mixed','preselected','ambiguous','unknown-number','multi-choice','continue-question','continue-status','continue-summary','continue-clarification','continue-direction','new-task','new-selected','explicit-skill','separate-approval','explicit-owner','route-number','executor-number','menu-short','menu-full']
jobs=[('candidate',m,k,1) for m in ['common','both'] for k in cases]+[('candidate','common','diagnose',2),('candidate','common','diagnose',3),('candidate','both','diagnose',2),('candidate','common','implement-code',2),('candidate','common','implement-code',3),('candidate','both','implement-code',2),('baseline','common','diagnose',3),('baseline','both','diagnose',1),('baseline','both','diagnose',2)]
jobs=[j for j in jobs if not (out/('%s-%s-%s-%s.json'%j)).exists()]
def run(j):
 r=subprocess.run(['python3','-B',str(w/'native-v3.py'),*map(str,j)],capture_output=True,text=True);name='%s-%s-%s-%s'%j
 with (out/f'invocation-{name}.json').open('x') as f:json.dump({'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr},f,ensure_ascii=False,indent=2)
 return {'case':name,'exit':r.returncode,'result_exists':(out/(name+'.json')).exists()}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for r in pool.map(run,jobs):print(json.dumps(r),flush=True)
