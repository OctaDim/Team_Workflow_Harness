"""Run project tests from the root, excluding the two harness inbox trees."""
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
result = subprocess.run(
    [sys.executable, '-m', 'pytest', '--import-mode=importlib', '-q', '.',
     '--ignore=' + str(ROOT / 'harness/common/inbox'),
     '--ignore=' + str(ROOT / 'harness/project/inbox')],
    cwd=ROOT,
)
raise SystemExit(result.returncode)
