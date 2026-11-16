import concurrent.futures,subprocess,json
jobs=[('integration','common','explicit'),('integration','both','implicit'),('operation-partial','common','explicit')]
def run(j):
 k,m,c=j;cfg='/tmp/facts-'+('integration-v2' if k=='integration' else k)+'-candidate-v3-20261115.json';r=subprocess.run(['python3','-B','/tmp/harness_git_facts_native_20261115.py',cfg,m,c,k+'-candidate-v3'],capture_output=True,text=True);print(json.dumps({'job':j,'exit':r.returncode,'result':r.stdout[-800:]+r.stderr[-800:]},ensure_ascii=False),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(run,jobs))
