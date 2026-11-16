import subprocess,concurrent.futures,json
from pathlib import Path
w=Path(__file__).parent
jobs=[('method-b',m,c) for m in ['common','both'] for c in ['explicit','implicit']]+[('method-a',m,'explicit' if m=='common' else 'implicit') for m in ['common','both']]+[(k,m,'explicit') for k in ['choice','pr-readonly','dirty','unknown-intent','sql','protected-harness'] for m in ['common','both']]+[('method-b',m,'unrelated') for m in ['common','both']]
def run(job):
 kind,mode,case=job;tag='unrelated-v2' if case=='unrelated' else kind+'-v2';r=subprocess.run(['python3','-B',str(w/'native.py'),str(w/(kind+'-v2.json')),mode,case,tag],capture_output=True,text=True);print(json.dumps({'job':job,'exit':r.returncode,'tail':r.stdout[-1000:]+r.stderr[-1200:]},ensure_ascii=False),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(run,jobs))
