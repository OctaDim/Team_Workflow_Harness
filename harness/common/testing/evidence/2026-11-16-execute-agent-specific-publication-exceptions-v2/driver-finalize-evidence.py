import ast,hashlib,importlib.util,json,math,shutil
from pathlib import Path
import sys
sys.path.insert(0,'/tmp');from native_audit_helpers_20261115 import bootstrap
w=Path(__file__).parent;loc=json.loads((w/'location-v2.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);source=Path(loc['source']);oldout=Path(loc['previous_out']);name=source.name
sp=importlib.util.spec_from_file_location('g',repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
review=json.loads((out/'native-review-final.json').read_text());assert review['Codex']=='passed' and len(review['case_results'])==34 and all(r['passed'] for r in review['case_results']);expected=g.h.snapshot(source);assert review['source']==expected
assert json.loads((out/'status-preservation-audit.json').read_text())['passed']
assert json.loads((out/'fixture-preflight-v3.json').read_text())['passed'];assert json.loads((out/'fixture-preflight-v3.json').read_text())['fixture_sha256']==digest(w/'fixture.py')
prior=json.loads((oldout/'before-source.json').read_text());before=json.loads((out/'before.json').read_text())
for rel,v in prior.items():assert digest(repo/rel)==v['sha256'],rel
g.save(out/'before-source.json',prior)
base_rows=[]
for file in ['baseline-control-both-claude-only-implicit.json','baseline-control-common-retry-unexplained-implicit.json']:
 r=json.loads((oldout/file).read_text());assert r['completed'] and r['exit_code']==0 and not r['actions'] and r['queue']=={'current':'in progress','next':'new'};boot=bootstrap(repo,r,source);base_rows.append({'file':'../'+oldout.name+'/'+file,'actual_tool_output_chars':sum(map(len,boot['outputs'])),'usage':r['usage'],'observed':'canonical baseline stops publication/queue; original incident not freshly reproduced'})
g.save(out/'baseline-and-version-assessment.json',{'baseline':base_rows,'limits':'No causal improvement over passing canonical controls is claimed. Initial control with explanatory gate hints retained separately, not a RED result.','candidate_v1':'Prepared candidate has real over-blocking contradiction: unconditional unresolved-stop versus matching exception; combined scoped-exception refuses specifically authorized fixture release. Separate all-pass stale diagnosis is fixture inconsistency. V1 never published.','repair':'V2 per-slot coverage evaluated first; only uncovered results need repair/new decisions. All mandatory current checks repeated. All-pass fixture diagnosis=N/A.','original':'../'+oldout.name+'/native-review-v1-diagnostic.json','current_source':expected})
g.save(out/'contract-coverage.json',{'actual_subject':'comm-publish-harness-instructions candidate-v2','cases_per_mode':17,'modes':['common-only','common+project'],'actual_agent':'Codex CLI; real fresh-context sessions and real temporary copies/queue actions','synthetic_inputs':'The four Codex/Claude slot rows, A100/19-of20 and waivers are stipulated fixture inputs, NOT actual external review results, stock analyzer output, evaluator coverage, or session-wide user grants. Actual Claude is never invoked.','covered':['wrong publication-base..HEAD substitution blocks publication under general permission','agent and mode exceptions do not cross-cover','fixture scenario/environment causes repaired with original raw preserved and full fresh producer run before copy','instruction-target edit creates v2: fresh matrix and missing v2 Claude coverage stop release','unexplained lucky retry does not resolve failure','exact confirmed covered exception permits only scoped release with original statuses','fully successful required current slots and enough authorization publish without duplicate question','new version/new gap/new placement/ambiguous exception require assessment','data refusal/tool unavailable are not silent exceptions','explicit/implicit owner, gate and placement before copies, unrelated nonloading','no unauthorized copying/closure/advance; full copy equality, types/visibility/startup/common+project checks'], 'scope_limits':'Fixture producer validates a controlled test-world matrix only. It never substitutes for actual subject Codex/native checks. No guarantee against all future model failures or malicious bypass is claimed.'})
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
 raw=json.loads((out/row['file']).read_text());b=bootstrap(repo,raw,source);actual.append({'file':row['file'],'usage':raw['usage'],'actual_tool_output_chars':sum(map(len,b['outputs'])),'loaded':row['loaded'],'gate':row['gate']})
fixture_tree=ast.parse((w/'fixture.py').read_text());toy=next(n.value.value for n in ast.walk(fixture_tree) if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='old' and isinstance(n.value,ast.Constant))
g.save(out/'context-accounting.json',{'method':'Unicode chars and ceil(chars/4), startup/metadata/whole available logical library separate from actual per-session outputs/usage. Human-guide bodies excluded. No exact attribution of session tokens to one subject.','startup_guards':[size(p) for p in guards],'metadata':[{'path':str(p.relative_to(repo)),'chars':len(p.read_text().split('---',2)[1])} for p in library if p.name=='SKILL.md'],'available_resources':[size(p) for p in library],'target_static':size(source/'SKILL.md'),'target_references':[size(p) for p in (source/'references').rglob('*.md') if p.name!='README.human.md'],'actual_reads_usage':actual,'baseline':base_rows,'external_fixture_resources':{'source':'driver-fixture.py','sha256':digest(w/'fixture.py'),'includes':'CASE declaration, legacy helper, test-world producer, versioned slot/waiver data and target example; actual reads included where opened','extra_logical_skill_at_start':{'path':'harness/common/skills/comm-fixture-target/SKILL.md','chars':len(toy),'estimated_char_quarter':math.ceil(len(toy)/4),'role':'synthetic target, separate from subject and real lazy library'}}})
versions=[g.h.run(cmd) for cmd in [['codex','--version'],['git','--version'],['node','--version'],[g.PYTHON,'--version'],[g.PYTHON,'-m','pytest','--version']]];g.save(out/'tool-versions.json',versions)
artifacts={p.name:digest(p) for p in out.glob('*.json')};g.save(out/'publication-gate.json',{'passed':True,'source':expected,'raw_sha256':{r['file']:digest(out/r['file']) for r in review['case_results']},'artifact_sha256':artifacts,'Codex/common':'passed all17 current native cases plus mandatory checks','Codex/both':'passed all17 current native cases plus mandatory checks','Claude':'not run/unverified','Overall':'unverified'})
for filename in ['native.py','fixture.py','review.py','check-modes.py','matrix.py','preflight.py','finalize-evidence.py','audit_queue_status.py']:
 shutil.copyfile(w/filename,out/('driver-'+filename))
shutil.copyfile(w/'location-v2.json',out/'location-v2.json');print('Current source/evidence/context/dependency gate archived.')
