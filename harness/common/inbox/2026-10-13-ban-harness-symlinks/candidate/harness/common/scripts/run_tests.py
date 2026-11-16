"""Run each actual test edition separately, including inbox candidates."""
from pathlib import Path
import runpy
import subprocess
import sys

# Check the bootstrap paths before importing the existing shared guards.
SCRIPT = Path(__file__).absolute()
CHECKER = SCRIPT.parents[1] / 'checks/ensure_entrypoint_links.py'
for source in (SCRIPT, CHECKER):
    for component in (*reversed(source.parents), source):
        if component.is_symlink():
            raise ValueError(f'Symlink forbidden: {component}')
GUARDS = runpy.run_path(str(CHECKER))
ordinary_path, ordinary_tree = GUARDS['ordinary_path'], GUARDS['ordinary_tree']

ROOT = SCRIPT.parents[3]
ordinary_tree(ROOT / 'harness')
SUITES = sorted({path.parent for path in (ROOT / 'harness').rglob('test_*.py')})
assert SUITES, 'No test suites found'
for suite in SUITES:
    print(suite.relative_to(ROOT), flush=True)
    ordinary_tree(ROOT / 'harness')
    subprocess.run([sys.executable, '-m', 'pytest', '--import-mode=importlib',
                    '-q', str(suite)], cwd=ROOT, check=True)
