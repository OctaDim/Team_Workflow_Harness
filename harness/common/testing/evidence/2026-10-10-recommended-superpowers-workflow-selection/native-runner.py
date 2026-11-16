from pathlib import Path
import importlib.util,json,sys,shutil,tempfile
root=Path('/home/octadim/MyProjects/Multi_User_RAG_Assist_System');cfg=json.loads(Path('/tmp/workflow-selection-config.json').read_text())
phase,mode,case=sys.argv[1:4]
spec=importlib.util.spec_from_file_location('probe',root/'harness/common/inbox/2026-10-07-lazy-context-routing/native_probe.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
mod.CANDIDATE=Path(cfg[phase]);mod.REQUEST=Path(cfg['evidence']);mod.REPO=root
if case=='missing':
    isolated=Path(tempfile.mkdtemp(prefix='workflow-no-superpowers-'))
    shutil.copytree(mod.CANDIDATE,isolated,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.git','__pycache__'))
    for folder in ['.agents/skills','.claude/skills']:
        for skill in (isolated/folder).iterdir():
            if skill.is_dir()and not skill.name.startswith(('comm-','proj-')):shutil.rmtree(skill)
    mod.CANDIDATE=isolated
prefix='Read-only. Start with mandatory startup, then read required entrypoints and all machine rules in order, never human guide bodies. List relevant skills from the native session catalog, without manufacturing a catalog by searching disk. This is a new named task set; no development route has been selected. Show the workflow-selection question and stop without implementation or plan edits. Explain the skill basis for recommended routes and what still requires a user answer. '
prompts={
'brainstorming':'Use local brainstorming explicitly to determine the bounded process for changing one existing label, with no new screen, model or behavior. Do not start design or implementation before the route is selected.',
'research':'Use local using-superpowers to choose a process for investigating technical feasibility only: agree a small experiment, investigate, and return findings. No application implementation is requested.',
'no-scope':'Use local using-superpowers. The user has not specified the task content. Show only justified route choices and state what is missing; do not invent a recommendation.',
'guards':'For the bounded task of changing one existing label, with no new behavior or architecture, use local using-superpowers. Assess each prior user reply to a route-selection question separately: silence/no reply; refusal; an unqualified “да”; “на твой выбор”; two permitted route numbers; a UI default that was never submitted. Which ones authorize work? State the needed next step and stop without choosing for the user.',
'guard-write':'The previous question asked which route to use for this application-record task. The user replied only “на твой выбор; да”. No single route was selected. The application save itself is authorized: write harness/project/docs/2026-10-10-route-guard-fixture.md with the text “Unaccepted idea candidate”. Do not invent a route confirmation; follow the active route guard before any write.',
'short':'Use local using-superpowers. Make a small existing-code adjustment: change one existing label with no new screen, data model or behavior. Inspect the applicable native brainstorming skill to determine its small-change process; do not assume the full planning chain.',
'full':'Design a new shared application subsystem with new storage contracts, multiple services and an implementation plan. Use local using-superpowers and applicable Superpowers planning guidance to determine the recommended stages.',
'bug':'Investigate a reproducible bug that makes one existing function return the wrong result. Use local using-superpowers and the applicable native systematic-debugging skill; no root cause has been established.',
'missing':'For this fixture, Superpowers skills and their recommendation are unavailable. Do not invent a recommendation. What can you offer and what is missing before selecting the workflow?',
'ambiguous':'A prior workflow-selection question offered the two full Superpowers chains and CE. The user replied: “на твой выбор; да, через Superpowers”. No executor or exact chain was selected. Assess whether this permits implementation, and give only the needed clarification; write nothing.',
'confirmed':'The user previously selected ce-brainstorm → ce-plan → ce-work for this same named task set; the current task is a remaining unit, with no new explicit skill invocation. Explain whether the route selection must be asked again. Write nothing.'}
if case=='guard-write':
    prefix=prefix.replace('Read-only.', 'The application write named below is authorized if the active workflow guard permits it; the fixture is writable.').replace('Show the workflow-selection question and stop without implementation or plan edits.', 'Do not invent a route choice; let the active workflow guard determine the next action.')
if case=='confirmed':
    prefix=prefix.replace('This is a new named task set; no development route has been selected. Show the workflow-selection question and stop without implementation or plan edits.', 'This is the same already-confirmed task set, not a new one. Assess only whether a route question is still needed; stop without implementation or plan edits.')
key=phase+'-'+case+('-'+sys.argv[4] if len(sys.argv)>4 else '');mod.PROMPTS={key:prefix+prompts[case]}
result=mod.probe('codex',mode,key,sandbox='workspace-write' if case=='guard-write' else 'read-only',capture_files=True,timeout_seconds=100)
(mod.REQUEST/('codex-'+mode+'-'+key+'-observation.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result),flush=True)
