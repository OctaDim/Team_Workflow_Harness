import concurrent.futures,json,subprocess
jobs=[('fresh',m,'implicit' if m=='both' else 'explicit') for m in ['common','both']]+[(k,m,'implicit' if m=='both' else 'explicit') for k in ['offline','ambiguous','integration','operation-complete','operation-partial','operation-unknown','operation-permission','general'] for m in ['common','both']]+[('general',m,'unrelated') for m in ['common','both']]
def run(j):
 k,m,c=j;tag='unrelated-v2' if c=='unrelated' else k+'-candidate-v2'
 r=subprocess.run(['python3','-B','/tmp/harness_git_facts_native_20261115.py','/tmp/facts-'+('integration-v2' if k=='integration' else k)+'-candidate-v2-20261115.json',m,c,tag],capture_output=True,text=True)
 print(json.dumps({'job':j,'exit':r.returncode,'tail':r.stdout[-400:] if r.returncode==0 else r.stdout[-1000:]+r.stderr[-1500:]},ensure_ascii=False),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(run,jobs))
