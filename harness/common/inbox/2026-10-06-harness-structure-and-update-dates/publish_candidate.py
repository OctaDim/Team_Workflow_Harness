"""Apply only the reviewed manifest after explicit publication approval."""
from pathlib import Path
import argparse, hashlib, json, shutil

REQUEST=Path(__file__).resolve().parent
REPO=REQUEST.parents[3]
CANDIDATE=REQUEST/'candidate'
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
parser=argparse.ArgumentParser()
parser.add_argument('--apply',action='store_true')
args=parser.parse_args()
manifest=json.loads((REQUEST/'2026-10-06-publication-manifest.json').read_text())
for relative,expected in manifest['baseline'].items():
 path=REPO/relative
 assert not path.is_symlink() and digest(path)==expected, 'Source changed: '+relative
for row in manifest['files']:
 path=CANDIDATE/row['path']
 assert path.is_file() and not any(p.is_symlink() for p in (path,*path.parents))
 assert digest(path)==row['sha256'], 'Candidate changed: '+row['path']
print('Validated publication:',len(manifest['files']),'files;',len(manifest['removed_paths']),'old paths;',len(manifest['link_updates']),'link-only updates')
if args.apply:
 protected={name:digest(REPO/name) for name in ('AGENTS.md','CLAUDE.md')}
 for row in manifest['files']:
  source=CANDIDATE/row['path'];target=REPO/row['path']
  target.parent.mkdir(parents=True,exist_ok=True)
  shutil.copy2(source,target)
 for relative in manifest['removed_paths']:
  (REPO/relative).unlink()
 for row in manifest['link_updates']:
  (REPO/row['path']).write_text(row['replacement'])
 assert all(digest(REPO/name)==before for name,before in protected.items())
 assert all(digest(REPO/row['path'])==row['sha256'] for row in manifest['files'])
 (REQUEST/'2026-10-06-publication-result.json').write_text(json.dumps({'published':True,'version':manifest['instruction_version'],'files':len(manifest['files']),'removed_paths':len(manifest['removed_paths']),'protected_entrypoints_unchanged':True},indent=2)+'\n')
 print('Publication applied; protected entrypoints unchanged.')
