import importlib.util, json, subprocess, tempfile, hashlib
from pathlib import Path
source=Path('harness/common/testing/evidence/2026-10-16-application-startup-readiness/native-validation-v3.py').absolute()
spec=importlib.util.spec_from_file_location('readiness_fixture',source); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
e=source.parent
results=[]
for mode in ('common','both'):
 with tempfile.TemporaryDirectory(prefix='startup-structural-') as directory:
  root=Path(directory)
  startup=m.prepare(root,mode,False)
  common=root/'harness/common'
  rule=common/'rules'/m.RULE
  assert rule.read_bytes()==(root/'.claude/rules'/m.RULE).read_bytes()
  for native in ('.agents/skills','.claude/skills'):
   assert m.state(common/'skills'/m.NAME)==m.state(root/native/m.NAME)
  assert (common/'skills'/m.NAME/'SKILL.md').is_file()
  if mode=='common':
   assert not (root/'harness/project/sentinel.txt').exists()
   assert (root/'harness/project/testing/evidence/work').is_dir()
   assert (root/'harness/project/testing/evidence/harness').is_dir()
  tests=['test_rule_copies.py','test_skills_first_knowledge.py','test_human_guide_reader.py']
  cmd=[str(m.REPO/'.venv/bin/python'),'-m','pytest','--import-mode=importlib','-q','-p','no:cacheprovider',*[str(common/'testing/tests'/t) for t in tests]]
  p=subprocess.run(cmd,cwd=root,capture_output=True,text=True,env=dict(__import__('os').environ,PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'))
  results.append({'mode':mode,'startup':startup,'copy_equality':True,'rule_pointer':True,'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
  print(mode,p.returncode,p.stdout[-1200:])
 with tempfile.TemporaryDirectory(prefix='startup-negative-') as directory:
  root=Path(directory);m.prepare(root,mode,False)
  victim=root/'.claude/rules'/m.RULE;victim.unlink()
  before=m.state(root)
  p=subprocess.run(['python3','-B','harness/common/checks/ensure_entrypoint_links.py'],cwd=root,capture_output=True,text=True)
  assert p.returncode!=0 and before==m.state(root)
  results.append({'mode':mode,'missing_native_rule_refused_before_writes':True,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
with tempfile.TemporaryDirectory(prefix='startup-project-only-') as directory:
 root=Path(directory);(root/'harness/project').mkdir(parents=True);(root/'harness/project/START.md').write_text('# Project only\n')
 before=m.state(root)
 p=subprocess.run(['python3','-B','harness/common/checks/ensure_entrypoint_links.py'],cwd=root,capture_output=True,text=True)
 assert p.returncode!=0 and before==m.state(root)
 results.append({'mode':'project-only','refused':True,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
with (e/'installation-v3.json').open('x') as f:json.dump(results,f,ensure_ascii=False,indent=2)
