from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import json,subprocess
w=Path(__file__).parent;out=Path(json.loads((w/'location-v2.json').read_text())['out']);jobs=[(m,k,'unrelated' if k=='unrelated' else 'explicit' if (m=='common')!=(k in ['copy-plan','identity-ambiguous']) else 'implicit') for m in ['common','both'] for k in ['native-transfer','links-only','same-host-plan','copy-plan','identity-ambiguous','receiver-blocked','mirror-risk','redirect-reuse','access-denied','unrelated']];jobs=[j for j in jobs if j!=('common','native-transfer','explicit')]
def run(j):
 m,k,i=j;r=subprocess.run(['python3',str(w/'native.py'),'candidate',m,k,i,'current'],text=True,capture_output=True)
 with (out/f'invocation-current-{m}-{k}-{i}.json').open('x') as f:json.dump({'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr},f,ensure_ascii=False,indent=2)
 print(json.dumps({'mode':m,'kind':k,'invocation':i,'exit_code':r.returncode,'output':r.stdout[-550:],'stderr':r.stderr[-550:]},ensure_ascii=False),flush=True);return r.returncode
with ThreadPoolExecutor(max_workers=3) as pool:results=[f.result() for f in as_completed([pool.submit(run,j) for j in jobs])]
assert all(r==0 for r in results)
