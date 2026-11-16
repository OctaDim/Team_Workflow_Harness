import concurrent.futures,json,subprocess
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v2.json').read_text());out=Path(loc['out'])
jobs=[(m,k) for m in ['common','both'] for k in ['ordinary','selected','triage','history','unrelated'] if not (out/f'current-{m}-{k}.json').exists()]
def run(job):
 m,k=job;r=subprocess.run(['python3','-B',str(w/'native.py'),'candidate',m,k,'current'],capture_output=True,text=True);p=out/f'invocation-{m}-{k}.json'
 with p.open('x') as f:json.dump({'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr},f,ensure_ascii=False,indent=2)
 return {'mode':m,'kind':k,'code':r.returncode,'result_exists':(out/f'current-{m}-{k}.json').exists()}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for r in pool.map(run,jobs):print(json.dumps(r),flush=True)
