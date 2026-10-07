"""Check the proposal over the existing installation, without publishing it."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

REQUEST = Path(__file__).resolve().parent
ROOT = REQUEST.parents[3]
with tempfile.TemporaryDirectory(prefix='project-authorization-') as directory:
    staging = Path(directory)
    shutil.copytree(ROOT / 'harness', staging / 'harness',
                    ignore=shutil.ignore_patterns('inbox', 'evidence', '__pycache__'))
    test = staging / 'harness/common/testing/tests/test_ensure_entrypoint_links.py'
    candidate = REQUEST / 'candidate/harness/common/testing/tests/test_ensure_entrypoint_links.py'
    test.write_bytes(candidate.read_bytes())
    red = subprocess.run([sys.executable, '-m', 'pytest', '--import-mode=importlib', '-q',
                          str(test) + '::TestEntryPointLinks::test_missing_project_requires_authorization_before_any_write'],
                         cwd=ROOT, text=True, capture_output=True)
    assert red.returncode == 1 and 'assert 0 == 2' in red.stdout, red.stdout + red.stderr
    for source in (REQUEST / 'candidate/harness').rglob('*'):
        if source.is_file() and '__pycache__' not in source.parts:
            target = staging / 'harness' / source.relative_to(REQUEST / 'candidate/harness')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    tests = staging / 'harness/common/testing/tests'
    green = subprocess.run([sys.executable, '-m', 'pytest', '--import-mode=importlib', '-q',
                            *[str(tests / name) for name in ('test_ensure_entrypoint_links.py',
                             'test_entrypoint_notifications.py', 'test_entrypoint_portability.py')]],
                           cwd=ROOT, text=True, capture_output=True)
    print(json.dumps({'red': {'exit_code': red.returncode, 'stdout': red.stdout, 'stderr': red.stderr},
                      'green': {'exit_code': green.returncode, 'stdout': green.stdout, 'stderr': green.stderr}},
                     ensure_ascii=False, indent=2))
    sys.exit(green.returncode)
