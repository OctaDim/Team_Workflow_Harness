from pathlib import Path
import importlib.util
import json
import shutil
import subprocess
import tempfile

ROOT = Path('/home/octadim/MyProjects/Multi_User_RAG_Assist_System')
REQUEST = ROOT / 'harness/common/inbox/2026-10-09-confirm-development-workflow'
EVIDENCE = ROOT / 'harness/common/testing/evidence/2026-10-09-confirm-development-workflow'
PROBE = ROOT / 'harness/common/inbox/2026-10-07-lazy-context-routing/native_probe.py'
SPEC = importlib.util.spec_from_file_location('probe', PROBE)
native = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(native)
PROMPT = ('Добавь в существующий main.py функцию add(a, b), возвращающую сумму. '
          'Сначала выполни обязательный старт проекта. Не читай README.human.md. '
          'Не изменяй другие файлы. Если требуется ответ пользователя, задай вопрос и остановись.')
results = []
for phase, agent, mode in [('red', 'codex', 'common'), ('green', 'codex', 'common'),
                           ('red', 'claude', 'common'), ('green', 'claude', 'common')]:
    with tempfile.TemporaryDirectory(prefix='workflow-fixture-') as directory:
        stage = Path(directory)
        common = stage / 'harness/common'
        shutil.copytree(ROOT / 'harness/common', common,
                        ignore=shutil.ignore_patterns('inbox', 'evidence', '__pycache__'))
        if mode == 'both':
            shutil.copytree(ROOT / 'harness/project', stage / 'harness/project')
        for base in ['.agents/skills', '.claude/skills']:
            shutil.copytree(common / 'skills', stage / base)
        shutil.copytree(common / 'rules', stage / '.claude/rules')
        if phase == 'green':
            for folder in [common / 'rules', stage / '.claude/rules']:
                shutil.copyfile(REQUEST / 'comm-confirm-development-workflow.md',
                                folder / 'comm-confirm-development-workflow.md')
        (stage / 'main.py').write_text('# Existing module\n')
        startup = subprocess.run(['python3', '-B', str(common / 'checks/ensure_entrypoint_links.py'),
                                  str(stage)], capture_output=True, text=True)
        assert startup.returncode == 0, startup.stderr
        assert (stage / 'harness/project/START.md').is_file()
        native.CANDIDATE = stage
        native.REQUEST = EVIDENCE
        native.REPO = ROOT
        invocation = f'{phase}-implicit'
        native.PROMPTS = {invocation: PROMPT}
        result = native.probe(agent, 'both', invocation, sandbox='workspace-write',
                              capture_files=True, timeout_seconds=90)
        result.update(fixture_mode=mode, phase=phase)
        results.append(result)
        (EVIDENCE / '2026-10-09-native-summary.json').write_text(
            json.dumps(results, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps(result, ensure_ascii=False), flush=True)
