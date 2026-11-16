import concurrent.futures,subprocess,json
jobs=[('general','both','implicit','general-candidate-v3-retry1'),('general','common','unrelated','unrelated-v3-retry1'),('general','both','unrelated','unrelated-v3-retry1'),('operation-permission','both','explicit','operation-permission-candidate-v3-explicit-retry1')]
def run(j):
 k,m,c,tag=j;r=subprocess.run(['python3','-B','/tmp/harness_git_facts_native_20261115.py','/tmp/facts-'+k+'-candidate-v3-20261115.json',m,c,tag],capture_output=True,text=True);print(json.dumps({'job':j,'exit':r.returncode,'tail':r.stdout[-750:]+r.stderr[-750:]},ensure_ascii=False),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(run,jobs))
