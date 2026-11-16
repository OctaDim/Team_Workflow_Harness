import concurrent.futures,subprocess,json

def run(mode):
 r=subprocess.run(['python3','-B','/tmp/harness_branch_native_v2_20261115.py','/tmp/branch-positive-fixture-v2-20261115.json',mode,'control','baseline-v2'],capture_output=True,text=True)
 print(json.dumps({'mode':mode,'exit':r.returncode,'tail':r.stdout[-1500:]+r.stderr[-1500:]},ensure_ascii=False),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(run,['common','both']))
