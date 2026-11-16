import hashlib,importlib.util,json,math,shutil
from pathlib import Path
from audit import bootstrap
w=Path(__file__).parent;loc=json.loads((w/'location-v2.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);source=Path(loc['source']);oldout=Path(loc['previous_out']);sp=importlib.util.spec_from_file_location('g',repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):g.save(out/n,v)
review=json.loads((out/'native-review-final.json').read_text());expected=digest(source);assert review['Codex']=='passed' and len(review['case_results'])==10 and all(r['passed'] for r in review['case_results']);assert review['source_sha256']==expected
before=json.loads((out/'before.json').read_text());assert digest(repo/'harness/common/INDEX.md')==before['target_sha256'];assert g.protect()==before['protected']
for mode in ['common','both']:
 r=json.loads((out/f'prepublication-suite-{mode}.json').read_text());assert r['suite']['exit_code']==0 and r['source_sha256']==expected and r['project_preserved'] and r['repeat_startup_unchanged'] and r['logical_links_valid']
assert json.loads((out/'project-only-negative.json').read_text())['refused_before_writes']
analysis=json.loads(json.loads((out/'candidate-analyze.json').read_text())['stdout']);assert analysis['summary']['grade']=='A' and not any(c['status'] in ['fail','error'] for c in analysis['checks'])
save('stock-assessment-summary.json',{'tool':analysis['tool'],'target':analysis['target'],'summary':analysis['summary'],'budgets':analysis['budgets'],'scope':'Generic bounded directory containing only whole INDEX.md. No skill/plugin profile, invented manifest, coverage or relaxed threshold. Creator/skill structure checks N/A to navigation map. Mandatory startup cost is not deferred regardless of analyzer field label.'})
deps={}
for directory in ['harness/common/skills','harness/common/rules']:
 for p in (repo/directory).rglob('*.md'):
  if p.name!='README.human.md':rel=str(p.relative_to(repo));deps[rel]={'source':rel,'sha256':digest(p),'native':True}
for rel in ['AGENTS.md','harness/common/START.md','harness/project/START.md','harness/project/INDEX.md','harness/common/checks/ensure_entrypoint_links.py']:
 deps[rel]={'source':rel,'sha256':digest(repo/rel),'native':True}
for p in [g.ENTRY,g.CREATOR,repo/'harness/common/scripts/plugin_eval_without_human.mjs']:
 deps[str(p)]={'source':str(p),'sha256':digest(p),'native':False}
actual=[]
for row in review['case_results']:
 r=json.loads((out/row['file']).read_text());b=bootstrap(repo,r);assert b['valid']
 for rel,v in deps.items():
  if v['native'] and not (row['mode']=='common' and rel.startswith('harness/project/')):assert r['before'].get(rel)==v['sha256'],(row['file'],rel)
 actual.append({'file':row['file'],'actual_tool_output_chars':sum(map(len,b['outputs'])),'usage':r['usage']})
save('external-dependencies.json',deps)
guards=[repo/'AGENTS.md',repo/'harness/common/START.md',repo/'harness/project/START.md',*sorted((repo/'.claude/rules').rglob('*.md')),repo/'harness/common/INDEX.md',repo/'harness/project/INDEX.md'];guards=[p for p in guards if p.name!='README.human.md']
def size(p):
 text=(source if p==repo/'harness/common/INDEX.md' else p).read_text();return {'path':str(p.relative_to(repo)),'chars':len(text),'estimated_char_quarter':math.ceil(len(text)/4)}
library=[p for p in (repo/'harness/common/skills').rglob('*.md') if p.name!='README.human.md']
save('context-accounting.json',{'method':'Unicode chars and ceil(chars/4) are static estimates; actual session usage/output recorded separately without exact target attribution. Human bodies excluded.','startup_guards':[size(p) for p in guards],'target_size':json.loads((out/'content-and-size.json').read_text()),'whole_available_lazy_library':[size(p) for p in library],'native_actual':actual,'stock_component':analysis['budgets'],'baseline':'../'+oldout.name+'/baseline-common-ordinary.json','baseline_observation':'Correct UTF8 answer, but broad recursive content search exposed closed request and historical copy. Original v1 repeated boundary failure. V2 triage still read completed body; current v3 tested all fresh cases. No universal future behavior guarantee.'})
save('tool-versions.json',[g.h.run(cmd) for cmd in [['codex','--version'],['git','--version'],['node','--version'],[g.PYTHON,'--version'],[g.PYTHON,'-m','pytest','--version']]])
for filename in ['native.py','fixture.py','review.py','audit.py','local.py','matrix.py','finalize.py','publish.py','close.py','audit_queue_status.py']:
 if (w/filename).exists():shutil.copyfile(w/filename,out/('driver-'+filename))
artifacts={p.name:digest(p) for p in out.glob('*.json')};save('publication-gate.json',{'passed':True,'source_sha256':expected,'target_before_sha256':before['target_sha256'],'raw_sha256':{r['file']:digest(out/r['file']) for r in review['case_results']},'artifact_sha256':artifacts,'Codex/common':'passed current5 native plus full195 suite','Codex/both':'passed current5 native plus full195 suite','Claude':'not run/unverified','Overall':'unverified'})
print('Current INDEX gate complete.')
