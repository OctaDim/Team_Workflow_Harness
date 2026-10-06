"""Audit final candidate structure, migration preservation and active links."""
from pathlib import Path
import hashlib, json, re

REQUEST = Path(__file__).resolve().parent
REPO = REQUEST.parents[3]
ROOT = REQUEST / 'candidate'
EVIDENCE = ROOT / 'harness/common/testing/evidence/2026-10-06-structure-migration'
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def audit():
 template = json.loads((ROOT / 'harness/common/base/project-skeleton.json').read_text())['categories']
 assert len(template)==15 and len({name.split('/')[0] for name in template})==12
 for package in ('common','project'):
  for name in template: assert (ROOT/'harness'/package/name/'README.human.md').is_file(), name
 for directory in (ROOT/'harness').rglob('*'):
  if directory.is_dir() and '__pycache__' not in directory.parts:
   assert (directory/'README.human.md').is_file(), str(directory)
 assert not (ROOT/'.claude/rules/README.human.md').exists()
 mapping=json.loads((EVIDENCE/'2026-10-06-migration-map.json').read_text())['paths']
 for row in mapping:
  source=REPO/row['source']; dest=ROOT/row['destination']
  assert dest.is_file(), row['destination']
  assert digest(source)==row['original_sha256'], row['source']
  assert digest(dest)==row['candidate_sha256'], row['destination']
  if source.suffix=='.json' and source.name!='project-skeleton.json': assert digest(dest)==digest(source)
  if row['source']!=row['destination']: assert not (ROOT/row['source']).exists(), row['source']
 for original in json.loads((EVIDENCE/'2026-10-06-originals.json').read_text())['files']:
  assert hashlib.sha256(original['source'].encode()).hexdigest()==original['sha256'], original['path']
 for name in ('AGENTS.md','CLAUDE.md'): assert digest(ROOT/name)==digest(REPO/name)
 for path in ('harness/common/checks/ensure_entrypoint_links.py','harness/project/checks/ensure_entrypoint_links.py'):
  assert digest(ROOT/path)==digest(REPO/path)
 assert digest(ROOT/'harness/common/scripts/plugin_eval_without_human.mjs')==digest(REPO/'harness/common/checks/plugin_eval_without_human.mjs')
 assert digest(ROOT/'pytest.ini')==digest(ROOT/'harness/common/testing/pytest.ini')
 for rule in (ROOT/'harness/common/rules').glob('comm-*.md'): assert digest(rule)==digest(ROOT/'.claude/rules'/rule.name)
 skill='comm-create-lazy-claude-codex-skills'
 source=ROOT/'harness/common/skills'/skill
 for path in source.rglob('*'):
  if path.is_file() and path.name!='README.human.md':
   for native in ('.agents/skills','.claude/skills'): assert digest(path)==digest(ROOT/native/skill/path.relative_to(source))
 checked=0; omitted_inbox=0; broken=[]
 for file in ROOT.rglob('*.md'):
  if file.name=='README.human.md': continue
  for target in re.findall(r'\]\(([^)]+)\)', file.read_text()):
   target=target.strip().strip('<>').split('#')[0]
   if not target or re.match(r'\w+://',target): continue
   checked+=1
   path=(file.parent/target).resolve()
   if path.exists(): continue
   try:relative=path.relative_to(ROOT)
   except ValueError: broken.append((str(file.relative_to(ROOT)),target));continue
   if relative.parts[:3] in (('harness','common','inbox'),('harness','project','inbox')) and (REPO/relative).exists():
    omitted_inbox+=1
   else:broken.append((str(file.relative_to(ROOT)),target))
 assert not broken, broken
 return {'pass':True,'mapped_resources':len(mapping),'links_checked':checked,'historical_inbox_links_resolved_in_source':omitted_inbox,'raw_json_preserved':True,'protected_entrypoints_unchanged':True,'human_guide_bodies_output':False}
if __name__=='__main__':
 result=audit()
 (EVIDENCE/'2026-10-06-candidate-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result,ensure_ascii=False))
