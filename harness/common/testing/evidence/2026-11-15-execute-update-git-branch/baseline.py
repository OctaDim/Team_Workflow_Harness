import subprocess,concurrent.futures,json
from pathlib import Path
w=Path(__file__).parent

def run(mode):
 r=subprocess.run(['python3','-B',str(w/'native.py'),str(w/'method-b.json'),mode,'control','baseline-v1'],capture_output=True,text=True);print(json.dumps({'mode':mode,'exit':r.returncode,'tail':r.stdout[-1800:]+r.stderr[-1200:]},ensure_ascii=False),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(run,['common','both']))
