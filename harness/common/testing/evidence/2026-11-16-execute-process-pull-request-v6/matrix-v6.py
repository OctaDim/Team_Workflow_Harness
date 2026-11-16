import subprocess,concurrent.futures,json,threading
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v6.json').read_text());out=Path(loc['out']);stop=threading.Event()
jobs=[('create1',m,c) for m in ['common','both'] for c in ['explicit','implicit']]+[(k,m,'explicit' if m=='common' else 'implicit') for k in ['no-choice','ambiguous-choice','merge2','merge3','gate-table','base-race','queue','loss','cleanup-table','delete-race','local-drift','summary','sensitive'] for m in ['common','both']]+[('create1',m,'unrelated') for m in ['common','both']]
def run(job):
 kind,mode,case=job
 if kind=='base-race' and mode=='common' and case=='explicit':return
 if stop.is_set():print(json.dumps({'job':job,'not_started':'Codex usage limit in preceding job'}),flush=True);return
 tag='unrelated-v6' if case=='unrelated' else kind+'-v6';r=subprocess.run(['python3','-B',str(w/'native.py'),str(w/(kind+'-v6.json')),mode,case,tag],capture_output=True,text=True)
 with (out/f'invocation-{tag}-{mode}-{case}.json').open('x') as f:json.dump({'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr},f,ensure_ascii=False,indent=2)
 path=out/f'{tag}-{mode}-{case}.json';data=json.loads(path.read_text()) if path.exists() else None
 if data and 'usage limit' in data['stdout'].lower():stop.set()
 print(json.dumps({'job':job,'process_exit':r.returncode,'completed':data.get('completed') if data else None,'sensitive_leak':data.get('sensitive_leak') if data else None,'tail':r.stdout[-850:]+r.stderr[-1000:]},ensure_ascii=False),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(run,jobs))
