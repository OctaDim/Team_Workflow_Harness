import concurrent.futures,subprocess,json
jobs=[('positive',m,c) for m in ['common','both'] for c in ['explicit','implicit']]+[(k,m,'explicit' if m=='common' else 'implicit') for k in ['collision','remote-collision','invalid-prefix','missing-prefix','race','host-failure'] for m in ['common','both']]+[('positive',m,'unrelated') for m in ['common','both']]
def run(j):
 k,m,c=j;tag='unrelated-v1' if c=='unrelated' else k+'-v1';r=subprocess.run(['python3','-B','/tmp/harness_branch_native_v2_20261115.py','/tmp/branch-'+k+'-fixture-v2-20261115.json',m,c,tag],capture_output=True,text=True)
 print(json.dumps({'job':j,'exit':r.returncode,'tail':r.stdout[-750:]+r.stderr[-1000:]},ensure_ascii=False),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(run,jobs))
