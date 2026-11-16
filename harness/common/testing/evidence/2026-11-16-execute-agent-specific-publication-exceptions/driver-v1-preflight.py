import hashlib,json,subprocess,tempfile
from pathlib import Path
from fixture import build
w=Path(__file__).parent;out=Path(json.loads((w/'location.json').read_text())['out']);rows=[]
for kind in ['known-failure','claude-only','reverse-exception','mode-exception','scenario-repair','environment-repair','candidate-repair','retry-unexplained','scoped-exception','all-pass','new-version','new-failure','new-placement','ambiguous-exception','data-denied','tool-unavailable','unrelated']:
 with tempfile.TemporaryDirectory(prefix='gate-fixture-preflight-') as d:
  root=Path(d)/'project';root.mkdir();truth,task,audit=build(root,kind);settings=json.loads((root/'packet/settings.json').read_text());original=(root/'packet/original-raw.json').read_bytes();status=json.loads(original)
  assert status['skill_sha256']==hashlib.sha256((root/truth['candidate']/'SKILL.md').read_bytes()).hexdigest()
  if kind in ['scenario-repair','environment-repair','candidate-repair']:
   settings.update(diagnosis='confirmed fixture cause repaired')
   if kind=='scenario-repair':settings['checked_range']='publication-base..HEAD'
   if kind=='environment-repair':settings['transport']='ready'
   if kind=='candidate-repair':
    p=root/truth['candidate']/'SKILL.md';p.write_text(p.read_text().replace('Result: unsafe-fallback','Result: safe-stop'));settings['version']='v2'
   (root/'packet/settings.json').write_text(json.dumps(settings));r=subprocess.run(['python3','-B','tools/check_fixture.py','run','--out','packet/preflight-new.json'],cwd=root,text=True,capture_output=True);assert r.returncode==0,(kind,r.stderr);new=json.loads(r.stdout);assert new['passed_cases']==20 and all(v['result']=='pass' and v['complete'] for k,v in new['slots'].items() if k.startswith('Codex/'));assert all(v['result']=='not run' for k,v in new['slots'].items() if k.startswith('Claude/'));assert (root/'packet/original-raw.json').read_bytes()==original
  if kind=='all-pass':assert status['passed_cases']==20 and all(v['result']=='pass' and v['complete'] for k,v in status['slots'].items() if k.startswith('Codex/'))
  rows.append({'kind':kind,'build_valid':True,'repair_producer_valid':kind in ['scenario-repair','environment-repair','candidate-repair']})
with (out/'fixture-preflight-v2.json').open('x') as f:json.dump({'passed':True,'fixture_sha256':hashlib.sha256((w/'fixture.py').read_bytes()).hexdigest(),'cases':rows,'limits':'Synthetic packet/producer consistency only; not actual agent verification or stock analyzer output.'},f,indent=2)
print('17 fixture cases and all3 repair producers valid')
