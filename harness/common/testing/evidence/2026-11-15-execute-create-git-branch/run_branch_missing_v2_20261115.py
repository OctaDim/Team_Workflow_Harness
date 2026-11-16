import concurrent.futures,subprocess,json

def run(mode):
 case='explicit' if mode=='common' else 'implicit';r=subprocess.run(['python3','-B','/tmp/harness_branch_native_v3_20261115.py','/tmp/branch-missing-prefix-fixture-v3-20261115.json',mode,case,'missing-prefix-v2'],capture_output=True,text=True);print(json.dumps({'mode':mode,'exit':r.returncode,'tail':r.stdout[-1000:]+r.stderr[-1000:]},ensure_ascii=False),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(run,['common','both']))
