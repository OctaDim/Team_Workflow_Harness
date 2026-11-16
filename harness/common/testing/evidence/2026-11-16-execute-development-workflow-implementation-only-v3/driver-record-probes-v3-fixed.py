import json,subprocess
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v3.json').read_text());out=Path(loc['out'])
for mode in ['common','both']:
 r=subprocess.run(['python3','-B',str(w/'native-v3.py'),'candidate',mode,'record','1','--tag=-prepared'],capture_output=True,text=True)
 with (out/f'invocation-record-prepared-{mode}-fixed.json').open('x') as f:json.dump({'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr},f,ensure_ascii=False,indent=2)
 print(json.dumps({'mode':mode,'exit_code':r.returncode,'result_exists':(out/f'candidate-{mode}-record-prepared-1.json').exists()}),flush=True)
