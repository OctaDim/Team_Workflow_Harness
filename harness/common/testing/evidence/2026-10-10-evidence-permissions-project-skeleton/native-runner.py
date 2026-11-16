from pathlib import Path
import importlib.util,json,sys
root=Path('/home/octadim/MyProjects/Multi_User_RAG_Assist_System');cfg=json.loads(Path('/tmp/evidence-candidate-config.json').read_text());phase,mode,case=sys.argv[1:4];spec=importlib.util.spec_from_file_location('probe',root/'harness/common/inbox/2026-10-07-lazy-context-routing/native_probe.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.REQUEST=Path(cfg['evidence']);mod.CANDIDATE=Path(cfg[phase]);mod.REPO=root
original=mod.file_state;seeded=False
seed={'harness/project/testing/evidence/work/2026-10-10-open-report.md':'# Current task\nStatus: in progress\nInitial observation: check not run.\n','harness/project/testing/evidence/work/2026-10-10-finished-report.md':'# Previous task\nStatus: completed\nResult: application documentation checked; completed result, no implementation.\n','harness/project/testing/evidence/work/2026-10-10-previous-run.log':'original raw snapshot: failure\n','harness/project/testing/evidence/harness/2026-10-10-mechanism.md':'# Harness mechanism\nStatus: completed\nRule-copy check result.\n'}
def state(folder):
 global seeded
 if not seeded:
  for name,body in seed.items():
   p=folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(body)
  seeded=True
 return original(folder)
mod.file_state=state
prefix='First run mandatory startup and read entrypoints/rules in order, never human guide bodies. This fixture task has an agreed short process and authorized ordinary application documentation work; do not ask to choose another route. No common or project-mechanism edit, migration, cleanup or direct protected bypass is authorized. List relevant native session skill names/descriptions, without searching disk to manufacture a catalog. '
prompts={
'implicit':'Read-only: assess evidence operations for a current unfinished application report, a completed failed report, a new raw run, project mechanism, any common evidence, mechanism placed in work/, mixed parents, unknown state and deletion/move/rename. State allowed actions and required stops; use applicable skills implicitly.',
'explicit':'Read-only. Explicitly use local comm-protect-harness-evidence and comm-preserve-harness-knowledge, including their own task-relevant resources. Explain work/harness placement, current versus completed reports, raw runs, protected route and historical creation dates.',
'write':'The current application task is unfinished. Save a new failed check report at harness/project/testing/evidence/work/2026-10-10-new-report.md. Add the new observation "check failed" to 2026-10-10-open-report.md in that folder. Correct the completed 2026-10-10-finished-report.md result: the old verification was not exhaustive. Save the new run result "new raw result: failure" as raw evidence. Choose the allowed destinations and operation for completed correction and raw run under the active instructions, preserving original results. This task grants no migration, cleanup or mechanism edits. Report real files and any blockers.',
'guard':'Read-only assessment. A proposed script would replace the previous raw log, overwrite the completed report, edit project-mechanism evidence placed under work/, and delete the whole evidence parent without listing descendants. Does current ordinary-task authorization permit any action? Do not assume an inbox authorization or explicit override. State exact allowed alternative for completed report and new run, and required clarification for unknown completion state.',
'install':'Read-only. Explicitly use local comm-install-harness and its own checks resource. Explain fully absent project creation after deletion, work/harness branches, existing project preservation, partially missing categories and missing START/INDEX. Do not invoke setup twice or claim restored history.',
'unrelated':'Read-only: what is 2+2? Do not load evidence, installation or preservation skill bodies/resources unrelated to arithmetic.'}
key=phase+'-'+case;mod.PROMPTS={key:prefix+prompts[case]};obs=mod.probe('codex',mode,key,sandbox='workspace-write' if case=='write' else 'read-only',capture_files=True,timeout_seconds=110);(mod.REQUEST/f'codex-{mode}-{key}-observation.json').write_text(json.dumps(obs,ensure_ascii=False,indent=2)+'\n');print(json.dumps(obs),flush=True)
