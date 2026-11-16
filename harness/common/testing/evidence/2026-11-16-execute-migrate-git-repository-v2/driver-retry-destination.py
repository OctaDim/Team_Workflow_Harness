import json,subprocess
from pathlib import Path
w=Path(__file__).parent;out=Path(json.loads((w/'location-v2.json').read_text())['out']);assert json.loads((out/'destination-fixture-preflight.json').read_text())['passed']
for kind in ['receiver-blocked','mirror-risk']:
 r=subprocess.run(['python3',str(w/'native.py'),'candidate','common',kind,'explicit','current'],text=True,capture_output=True)
 with (out/f'retry-current-common-{kind}-explicit.json').open('x') as f:json.dump({'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr},f,ensure_ascii=False,indent=2)
 print(kind,r.returncode,r.stdout[-600:],r.stderr[-600:],flush=True);assert r.returncode==0
