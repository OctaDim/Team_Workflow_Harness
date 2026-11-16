import concurrent.futures,json,subprocess
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location.json').read_text());out=Path(loc['out']);jobs=[('common','diagnose'),('both','proposal'),('common','record'),('both','scope-explanation'),('common','scope-explanation')]
def run(job):
 m,k=job;r=subprocess.run(['python3','-B',str(w/'native.py'),'baseline',m,k,'1'],capture_output=True,text=True)
 with (out/f'invocation-baseline-{m}-{k}.json').open('x') as f:json.dump({'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr},f,ensure_ascii=False,indent=2)
 return {'mode':m,'kind':k,'code':r.returncode,'result_exists':(out/f'baseline-{m}-{k}-1.json').exists()}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for r in pool.map(run,jobs):print(json.dumps(r),flush=True)
