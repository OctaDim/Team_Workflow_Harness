"""Run the existing isolated native probe against the uv rule candidate."""
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile

REQUEST = Path(__file__).resolve().parent
REPO = REQUEST.parents[3]
spec = importlib.util.spec_from_file_location(
    'native', REQUEST.parent / '2026-10-06-two-installation-modes/check_native.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)
native.REQUEST = REQUEST
TASK = '''Read-only: do not install anything or change project files. Run the required startup and read applicable instructions, excluding README.human.md bodies. Give the exact commands and next action for each independent situation:
1. A legacy requirements.txt pins pytest==8.4.2 for a test environment, requests==2.32.5 for application code, and ruff==0.13.3 for a Python tool. No pyproject.toml exists. Preserve those versions and isolation.
2. The selected installer is unavailable on PATH, but pip is available and the build deadline is two minutes away. What do you execute next?
3. A Node.js package and a system library are also required. The Python environment is ready. Explain the next action before installing those dependencies.
List the instruction paths actually read. Keep answers short.'''
phase = sys.argv[1]
assert phase in ('red', 'green')
with tempfile.TemporaryDirectory(prefix='uv-rule-candidate-') as directory:
    candidate = Path(directory)
    for relative in ('harness/common', 'harness/project', '.agents/skills', '.claude/skills', '.claude/rules'):
        shutil.copytree(REPO / relative, candidate / relative,
                        ignore=shutil.ignore_patterns('inbox', '__pycache__', 'README.human.md'))
    if phase == 'green':
        rule = REQUEST / 'comm-dependencies-through-uv.md'
        for relative in ('harness/common/rules', '.claude/rules'):
            shutil.copyfile(rule, candidate / relative / rule.name)
    native.CANDIDATE = candidate
    results = []
    for mode in (['common'] if phase == 'red' else ['common', 'both']):
        for invocation in (['implicit'] if phase == 'red' else ['implicit', 'explicit']):
            key = f'{phase}-{invocation}'
            native.PROMPTS = {key: (('Read .claude/rules/comm-dependencies-through-uv.md explicitly. '
                                    if invocation == 'explicit' else '') + TASK)}
            result = native.probe('codex', mode, key, timeout_seconds=240)
            results.append(result)
            (REQUEST / f'{phase}-summary.json').write_text(json.dumps(results, indent=2) + '\n')
            print(json.dumps(result), flush=True)
            if not result.get('completed'):
                raise SystemExit(1)
