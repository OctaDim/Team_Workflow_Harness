import ast,hashlib,importlib.util,json,math,shutil
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v3.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);source=Path(loc['source']);skill=Path(loc['skill']);sp=importlib.util.spec_from_file_location('g',repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g);sp=importlib.util.spec_from_file_location('review',w/'review-v3.py');rv=importlib.util.module_from_spec(sp);sp.loader.exec_module(rv)
FINAL_REVIEW='native-review-final-v3.json'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):g.save(out/n,v)
def protected():
 d=g.protect();d['.claude/rules'].pop('comm-confirm-development-workflow.md',None);return d
def others():
 a={}
 for rel in ['harness/common/skills','.agents/skills','.claude/skills']:
  a[rel]={k:v for k,v in g.h.snapshot(repo/rel).items() if not k.startswith(skill.name+'/')}
 return a
review=json.loads((out/FINAL_REVIEW).read_text());rows=review['case_results'];assert review['Codex']=='passed' and len(rows)==65 and all(r['passed'] for r in rows)
case_node=next(n for n in ast.parse((w/'matrix-v3.py').read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='cases' for t in n.targets));cases=ast.literal_eval(case_node.value);expected={f'candidate-{mode}-{kind}-1.json' for mode in ['common','both'] for kind in cases};expected-={'candidate-common-record-1.json','candidate-both-record-1.json'};expected|={'candidate-common-record-prepared-1.json','candidate-both-record-prepared-1.json','candidate-both-audit-fullproject-1.json'}
for mode,kind,reps in [('common','diagnose',[2,3]),('both','diagnose',[2]),('common','implement-code',[2,3]),('both','implement-code',[2])]:expected|={f'candidate-{mode}-{kind}-{rep}.json' for rep in reps}
assert expected=={r['file'] for r in rows},(expected-{r['file'] for r in rows},{r['file'] for r in rows}-expected)
assert review['rule_sha256']==digest(source) and review['skill']==g.h.snapshot(skill)
for n in ['chain-audit.json','semantic-audit-full-scope.json','human-filter-audit-full-scope.json']:assert json.loads((out/n).read_text())['passed'],n
ops=json.loads((out/'operation-audit-full-scope.json').read_text());assert ops['passed_without_flags'] and not ops['manual_candidates']
full=json.loads((out/'candidate-both-audit-fullproject-1.json').read_text());assert full['full_project_source']==full['full_project_after'] and full['full_project_source'] is not None
for mode in ['common','both']:
 r=json.loads((out/f'prepublication-suite-{mode}.json').read_text());assert r['rule_sha256']==digest(source) and r['skill']==g.h.snapshot(skill) and r['suite']['exit_code']==0 and r['project_preserved'] and r['repeat_startup_unchanged'] and r['copies_equal']
assert json.loads((out/'project-only-negative.json').read_text())['refused_before_writes']
budget=json.loads((out/'rule-budget.json').read_text());assert budget['source_sha256']==digest(source) and budget['W']<=300 and budget['T']<=1000
assessment=json.loads((out/'skill-assessment-summary.json').read_text());assert assessment['grade']=='A' and not any(c['status'] in ['fail','error'] for c in assessment['checks'])
prior=json.loads((out/'before-source.json').read_text());assert all(digest(repo/p)==v['sha256'] for p,v in prior.items());assert not any((repo/p/skill.name).exists() for p in ['harness/common/skills','.agents/skills','.claude/skills'])
assert g.protect()==json.loads((out/'before-protected.json').read_text())
save('before-other-installed.json',{'protected':protected(),'other_skills':others()})
deps={}
for folder in ['harness/common/skills','harness/common/rules','harness/common/checks','harness/common/scripts','harness/common/base']:
 for p in (repo/folder).rglob('*'):
  if not p.is_file() or any(part in ['inbox','evidence','__pycache__'] for part in p.relative_to(repo).parts) or p.suffix=='.pyc' or p==repo/'harness/common/rules/comm-confirm-development-workflow.md':continue
  rel=str(p.relative_to(repo));deps[rel]={'path':rel,'sha256':digest(p),'native':True}
for rel in ['AGENTS.md','CLAUDE.md','harness/common/START.md','harness/common/INDEX.md','harness/project/START.md','harness/project/INDEX.md','pytest.ini']:
 deps[rel]={'path':rel,'sha256':digest(repo/rel),'native':rel!='pytest.ini'}
for p in [g.ENTRY,g.CREATOR,repo/'harness/common/scripts/plugin_eval_without_human.mjs',repo/'harness/common/testing/evidence/2026-10-19-instruction-form-selection/validate.py',repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py']:
 deps[str(p)]={'path':str(p),'sha256':digest(p),'native':False}
rawfiles=[r['file'] for r in rows]+[r['file'] for r in json.loads((out/'semantic-audit-full-scope.json').read_text())['cases']]+[r['file'] for r in json.loads((out/'chain-audit.json').read_text())['cases']
assert {r['file'] for r in ops['cases']}==set(rawfiles)
assert set(rawfiles)<={r['file'] for r in json.loads((out/'human-filter-audit-full-scope.json').read_text())['cases']}
listed={mode:[] for mode in ['common','both']};actual=[];vendor_manifest={}
for name in rawfiles:
 raw=json.loads((out/name).read_text())
 for rel,v in deps.items():
  if v['native'] and not (raw['mode']=='common' and rel.startswith('harness/project/')):assert raw['before'].get(rel)==v['sha256'],(name,rel)
 if raw.get('native_catalogue',{}).get('listed'):listed[raw['mode']].append(name)
 msgs=raw.get('new_model_tool_messages',raw['model_tool_messages']);actual.append({'file':name,'mode':raw['mode'],'usage':raw['usage'],'actual_new_tool_output_chars':sum(v['visible_text_chars'] for v in rv.visible({**raw,'model_tool_messages':msgs})),'initial_context':raw.get('initial_context',[]),'body_read_source':'Post-truncation model tool messages; chain deltas only, cumulative messages retained for history proof.'})
 if raw.get('extra_skills'):
  vendor=Path('/home/octadim/.codex/plugins/cache/openai-curated-remote/superpowers/7.0.1/skills')
  for sk,files in raw['extra_skills'].items():
   assert g.h.snapshot(vendor/sk)==files
   for rel,sha in files.items():assert raw['before'].get('.agents/skills/'+sk+'/'+rel)==sha
  vendor_manifest[name]={'package':'superpowers/7.0.1','complete_skills':raw['extra_skills']}
assert all(listed.values());save('native-catalogue-audit.json',{'passed':True,'listed_cases':listed,'method':'Exact target name and description observed in actual initial system/developer metadata, separate from full file-copy checks.'});save('external-dependencies.json',deps);save('vendor-fixture-dependencies.json',vendor_manifest)
# Every full-chain warning in the real resumed dialogs is also exact.
menu=(skill/'references/menu.md').read_text();warning=menu[menu.index('> **Самостоятельная реализация'):menu.index('\n\nЯвный вызов')]
for mode in ['common','both']:
 raw=json.loads((out/f'chain-{mode}-step5.json').read_text());assert rv.norm(warning) in rv.norm(raw['final'])
static=lambda p:{'path':str(p.relative_to(repo)) if p.is_relative_to(repo) else str(p),'C':len(p.read_text()),'estimated_char_quarter':math.ceil(len(p.read_text())/4)}
guards=[repo/'AGENTS.md',repo/'harness/common/START.md',repo/'harness/project/START.md',*sorted((repo/'.claude/rules').rglob('*.md')),repo/'harness/common/INDEX.md',repo/'harness/project/INDEX.md'];startup=[]
for p in guards:
 if p.name=='README.human.md':continue
 d=static(p)
 if p.name=='comm-confirm-development-workflow.md':d={**d,'C':len(source.read_text()),'estimated_char_quarter':budget['T'],'candidate_sha256':digest(source)}
 startup.append(d)
library=[p for p in (repo/'harness/common/skills').rglob('*.md') if p.name!='README.human.md']+[p for p in skill.rglob('*.md') if p.name!='README.human.md']
save('context-accounting.json',{'method':'Static Unicode chars/ceil(C/4), stock UTF16 per-file estimates and actual model turn usage are separate. No attribution of total tokens/billing to one instruction. Human bodies omitted. Chain new messages measured without double-counting retained history.','startup_guards':startup,'metadata':[{'path':str(p),'C':len(p.read_text().split('---',2)[1])} for p in library if p.name=='SKILL.md'],'whole_available_harness_resources':[static(p) for p in library],'current_rule':budget,'current_skill_budgets':assessment['budgets'],'route_component_startup_before':1531,'route_component_startup_after':budget['T']+assessment['budgets']['trigger_cost_tokens']['value'],'complete_pair_static_with_all_resources':budget['T']+assessment['budgets']['total_tokens']['value'],'actual_reads_usage':actual,'external_actual_SP':'vendor-fixture-dependencies.json; full actual installed 7.0.1 copies for recommendation scenarios only, not synthetic recommendation metadata. Initial platform metadata size/hash recorded in each raw; opaque platform-provided resources not claimed fully inventoried.'})
baseline_files=[Path(loc['previous_out'])/'baseline-common-diagnose-1.json',Path(loc['v2_out'])/'baseline-common-diagnose-2.json',out/'baseline-common-diagnose-3.json',out/'baseline-both-diagnose-1.json',out/'baseline-both-diagnose-2.json'];controls=[]
for p in baseline_files:
 raw=json.loads(p.read_text());assert raw['completed'] and raw['exit_code']==0;controls.append({'file':str(p.relative_to(out.parent)),'menu_observed':'Compound Engineering' in raw['final'],'source_sha256':raw['source_sha256'],'usage':raw['usage']})
save('baseline-and-form-assessment.json',{'diagnostic_micro_controls':controls,'positive_passing_baselines':'Original basic audits and preparatory record already passed; no causal improvement claimed for those. Original diagnosis/proposal stopped for route and source explanation confirmed overbroad literal scope.','form_choice':'User selected short existing rule plus new contextual menu skill. Rule-only v1 W572/T1190 not adopted; no exception assumed. Lazy-only would remove the agreed early boundary; not implemented as a production alternative. Pair keeps classification/continuation with existing owner and defers menu/response algorithm. No metadata repair without observed miss.','critical_duplicate':'SKILL entry guard against new menu for analytics/already-clear route is needed for direct explicit invocation; full eligibility algorithm not duplicated.','source_fixes':'v2 real shortened warning fixed in v3 by complete literal template. All current mandatory checks repeated. Fixture/driver/oracle errors diagnosed separately with originals preserved; no lucky retry or old-version pass used.','current_sources':{'rule':digest(source),'skill':g.h.snapshot(skill)}})
save('tool-versions.json',[g.h.run(cmd) for cmd in [['codex','--version'],['git','--version'],['node','--version'],[g.PYTHON,'--version'],[g.PYTHON,'-m','pytest','--version']]])
for name in ['native-v3.py','native-full-project-v3.py','fixture.py','matrix-v3.py','probes-v3.py','chain-v3.py','chain-review-v3.py','review-v3.py','human-audit-full-scope-v3.py','extra-audits-v3.py','local-v3.py','local-v3-resume.py','local-v3-resume2.py','record-probes-v3-fixed.py','finalize-v3.py','publish-v3.py','close-v3.py']:
 if (w/name).exists():shutil.copyfile(w/name,out/('driver-'+name))
artifacts={p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!='README.human.md'};save('publication-gate.json',{'passed':True,'rule_sha256':digest(source),'skill':g.h.snapshot(skill),'review_file':FINAL_REVIEW,'selected_raw_sha256':{name:digest(out/name) for name in rawfiles},'artifact_sha256':artifacts,'Codex/common':'passed documented current scope','Codex/both':'passed documented current scope','Claude/common':'not run/unverified','Claude/both':'not run/unverified','Overall':'unverified','core_cases':len(rows),'real_chain_turns':12,'semantic_reviews':2,'full_project_byte_preservation':True})
print('Current full scope gate archived; source/native publication authorized by existing task scope.')
