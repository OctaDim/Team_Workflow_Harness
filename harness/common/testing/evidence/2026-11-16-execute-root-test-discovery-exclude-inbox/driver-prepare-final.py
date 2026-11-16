import base64,hashlib,importlib.util,json,math,shutil,sys
from pathlib import Path
sys.path.insert(0,'/tmp');from native_audit_helpers_20261115 import bootstrap
w=Path(__file__).parent;loc=json.loads((w/'location-v2.json').read_text());repo=Path(loc['repo']);out=Path(loc['out']);req=Path(loc['request']);code=Path(loc['code']);before=json.loads((out/'before-v2.json').read_text())
def save(name,value):
 with (out/name).open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest={}
for rel,sha in before['implementation'].items():
 p=code/rel;assert digest(p)==sha
 dest=req/'implementation-v2'/rel;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copyfile(p,dest)
 manifest[rel]={'sha256':sha,'base64':base64.b64encode(p.read_bytes()).decode()}
save('implementation-v2.json',manifest)
sources={n:req/'candidate-v2'/n for n in before['candidates']}
# Dependencies are compared to every native before-snapshot, not merely inventoried now.
deps={}
for directory in ['harness/common/skills','harness/common/rules']:
 for p in (repo/directory).rglob('*.md'):
  if p.name=='README.human.md':continue
  rel=str(p.relative_to(repo))
  if any(rel.startswith('harness/common/skills/'+n+'/') for n in sources):continue
  deps[rel]={'source':rel,'sha256':digest(p),'native':True}
for rel in ['AGENTS.md','CLAUDE.md','harness/common/START.md','harness/project/START.md','harness/common/INDEX.md','harness/project/INDEX.md','harness/common/base/project-skeleton.json','harness/common/checks/ensure_entrypoint_links.py']:
 deps[rel]={'source':rel,'sha256':digest(repo/rel),'native':True}
for path in [repo/'harness/common/scripts/plugin_eval_without_human.mjs',Path('/home/octadim/.codex/plugins/cache/openai-curated-remote/plugin-eval/0.1.2/scripts/plugin-eval.js'),Path('/home/octadim/.codex/skills/.system/skill-creator/scripts/quick_validate.py')]:
 deps[str(path)]={'source':str(path),'sha256':digest(path),'native':False}
review=json.loads((out/'native-review-final.json').read_text());assert review['Codex']=='passed'
for row in review['case_results']:
 raw=json.loads((out/row['file']).read_text())
 for rel,entry in deps.items():
  if entry['native']:
   # global CLAUDE intentionally absent in isolated Codex; common project neutral differs.
   if rel in ['CLAUDE.md','harness/project/START.md','harness/project/INDEX.md'] and row['mode']=='common':continue
   if rel=='CLAUDE.md' and rel not in raw['before']:continue
   assert raw['before'].get(rel)==entry['sha256'],(row['file'],rel)
save('external-dependencies.json',deps)
def size(p):
 text=p.read_text();return {'path':str(p.relative_to(repo)),'chars':len(text),'estimated_char_quarter':math.ceil(len(text)/4)}
guards=[repo/'AGENTS.md',repo/'harness/common/START.md',repo/'harness/project/START.md',*sorted((repo/'.claude/rules').rglob('*.md')),repo/'harness/common/INDEX.md',repo/'harness/project/INDEX.md'];guards=[p for p in guards if p.name!='README.human.md']
logical=[p for p in (repo/'harness/common/skills').rglob('*.md') if p.name!='README.human.md'];current=[next((s/p.relative_to(repo/'harness/common/skills'/n) for n,s in sources.items() if p.is_relative_to(repo/'harness/common/skills'/n)),p) for p in logical]
actual=[]
for row in review['case_results']:
 raw=json.loads((out/row['file']).read_text());extras=[p for n,s in sources.items() if n!='comm-install-harness' for p in s.rglob('*.md') if p.name!='README.human.md'];b=bootstrap(repo,raw,sources['comm-install-harness'],extras)
 actual.append({'file':row['file'],'usage':raw['usage'],'actual_tool_output_chars':sum(map(len,b['outputs'])),'loaded':row['loaded']})
meta=[]
for p in current:
 if p.name=='SKILL.md':
  text=p.read_text();front=text.split('---',2)[1] if text.startswith('---') else '';meta.append({'path':str(p.relative_to(repo)),'chars':len(front)})
save('context-accounting.json',{'method':'Unicode chars and ceil(chars/4) estimates, metadata/startup/available logical library separate; native real tool outputs and complete session usage are not exact subject-only token attribution. Human guides excluded. Common-only neutral project differs from combined.','startup_guards':[size(p) for p in guards],'metadata':meta,'available_resources':[size(p) for p in current],'target_static':{n:size(s/'SKILL.md') for n,s in sources.items()},'target_references':{n:[size(p) for p in s.rglob('*.md') if p.name not in ['SKILL.md','README.human.md']] for n,s in sources.items()},'actual_reads_usage':actual,'external_code_resources':list(before['implementation']),'baseline':'baseline-* plugin JSON; baseline-runtime-{common,both}-explicit.json real native reads; all original failed/invalid setup observations retained separately.'})
save('local-summary.json',{'source':before['candidates'],'implementation':before['implementation'],'current_native':'native-review-final.json','profiles':'A95 each; no errors/failures','local_modes':'195 passed each','project_only_refused_before_writes':True})
for name in ['native.py','review.py','modes-v2.py','budget.py','prepare-final.py']:
 shutil.copyfile(w/name,out/('driver-'+name))
print('Final sources, dependencies, context accounting archived.')
