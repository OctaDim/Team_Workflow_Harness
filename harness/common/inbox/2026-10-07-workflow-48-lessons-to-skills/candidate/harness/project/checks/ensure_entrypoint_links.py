"""Compatibility entrypoint; project requires common."""
import runpy
import sys
from pathlib import Path

checker = Path(__file__).absolute().parents[2] / 'common/checks/ensure_entrypoint_links.py'
if not checker.is_file() or any(path.is_symlink() for path in (checker, *checker.parents)):
    print('Entrypoint check failed: Safe ordinary harness/common is required; project-only is unsupported.', file=sys.stderr)
    sys.exit(2)
runpy.run_path(str(checker), run_name='__main__')
