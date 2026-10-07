"""Run each actual test edition separately, including inbox candidates."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
SUITES = sorted({path.parent for path in (ROOT / 'harness').rglob('test_*.py')})
assert SUITES, 'No test suites found'
for suite in SUITES:
    print(suite.relative_to(ROOT), flush=True)
    subprocess.run([sys.executable, '-m', 'pytest', '--import-mode=importlib',
                    '-q', str(suite)], cwd=ROOT, check=True)
