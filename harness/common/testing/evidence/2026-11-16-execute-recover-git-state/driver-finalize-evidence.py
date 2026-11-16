import hashlib,importlib.util,json,math,shutil,sys
from pathlib import Path
sys.path.insert(0,'/tmp');from native_audit_helpers_20261115 import bootstrap
w=Path(__file__).parent;loc=json.loads((w/'location.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);source=Path(loc['source']);name=source.name
sp=importlib.util.spec_from_file_location('g',repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((out/'operation-audit-final-v2.json').read_text())['passed']
review=json.loads((out/'native-review-final.json').read_text());assert review['Codex']=='passed' and len(review['case_results'])==20;expected=g.h.snapshot(source);assert review['source']==expected
base=[]
for file in ['baseline-common-published-implicit.json','baseline-both-abort-risk-implicit.json']:
 r=json.loads((out/file).read_text());assert r['completed'] and r['exit_code']==0 and r['git_before']==r['git_after'] and r['before']==r['after'];base.append({'file':file,'result':'passed scoped preservation/technical decision baseline; no behavior violation observed','final_verbatim':r['final']})
g.save(out/'baseline-assessment.json',{'results':base,'limits':'Prepared candidate predates this execution. No new guidance authored or changes justified by these passing controls; no RED or causal improvement invented. Current candidate evaluated as prepared under explicit execution/publication authorization.','setup_diagnosis':'Initial queue.py helper shadowed Python standard queue before CLI start; renamed audit_queue_status.py; that attempt is not a native result.'})
deps={}
for directory in ['harness/common/skills','harness/common/rules']:
 for p in (repo/directory).rglob('*.md'):
  if p.name=='README.human.md' or p.is_relative_to(repo/'harness/common/skills'/name):continue
  rel=str(p.relative_to(repo));deps[rel]={'source':rel,'sha256':digest(p),'native':True}
for rel in ['AGENTS.md','harness/common/START.md','harness/project/START.md','harness/common/INDEX.md','harness/project/INDEX.md','harness/common/checks/ensure_entrypoint_links.py']:
 deps[rel]={'source':rel,'sha256':digest(repo/rel),'native':True}
for p in [g.ENTRY,g.CREATOR,repo/'harness/common/scripts/plugin_eval_without_human.mjs']:
 deps[str(p)]={'source':str(p),'sha256':digest(p),'native':False}
for row in review['case_results']:
 raw=json.loads((out/row['file']).read_text())
 for rel,v in deps.items():
  if v['native'] and not (row['mode']=='common' and rel.startswith('harness/project/')):assert raw['before'].get(rel)==v['sha256'],(row['file'],rel)
g.save(out/'external-dependencies.json',deps)
def size(p):
 text=p.read_text();return {'path':str(p.relative_to(repo)),'chars':len(text),'estimated_char_quarter':math.ceil(len(text)/4)}
guards=[repo/'AGENTS.md',repo/'harness/common/START.md',repo/'harness/project/START.md',*sorted((repo/'.claude/rules').rglob('*.md')),repo/'harness/common/INDEX.md',repo/'harness/project/INDEX.md'];guards=[p for p in guards if p.name!='README.human.md'];library=[p for p in (repo/'harness/common/skills').rglob('*.md') if p.name!='README.human.md' and not p.is_relative_to(repo/'harness/common/skills'/name)]+[p for p in source.rglob('*.md') if p.name!='README.human.md'];actual=[]
for row in review['case_results']:
 raw=json.loads((out/row['file']).read_text());b=bootstrap(repo,raw,source);actual.append({'file':row['file'],'usage':raw['usage'],'actual_tool_output_chars':sum(map(len,b['outputs'])),'loaded':row['loaded'],'dependencies_read':row['dependencies']})
g.save(out/'context-accounting.json',{'method':'Unicode chars, ceil(chars/4) estimates; startup, metadata, full logical available library and actual per-session tool reads/usage separate. Human-guide bodies excluded. No exact subject-only token attribution.','startup_guards':[size(p) for p in guards],'metadata':[{'path':str(p.relative_to(repo)),'chars':len(p.read_text().split('---',2)[1])} for p in library if p.name=='SKILL.md'],'available_resources':[size(p) for p in library],'target_static':size(source/'SKILL.md'),'target_references':[size(p) for p in (source/'references').rglob('*.md') if p.name!='README.human.md'],'actual_reads_usage':actual,'baseline_sessions':[{'file':r['file'],'actual_tool_output_chars':sum(map(len,bootstrap(repo,json.loads((out/r['file']).read_text()),source)['outputs'])),'usage':json.loads((out/r['file']).read_text())['usage'],'subject_available':False} for r in base]})
artifacts={p.name:digest(p) for p in out.glob('*.json') if p.name not in ['publication-gate.json']}
g.save(out/'publication-gate.json',{'passed':True,'source':expected,'raw_sha256':{r['file']:digest(out/r['file']) for r in review['case_results']},'artifact_sha256':artifacts,'Codex/common':'passed documented current scope','Codex/both':'passed documented current scope','Claude':'not run/unverified','Overall':'unverified','baseline':'passing controls; no candidate edit or claimed improvement'})
for filename in ['native.py','fixture.py','review.py','check-modes.py','matrix.py','finalize-evidence.py','audit_queue_status.py','audit-operations.py']:
 shutil.copyfile(w/filename,out/('driver-'+filename))
print('evidence and gate prepared')
