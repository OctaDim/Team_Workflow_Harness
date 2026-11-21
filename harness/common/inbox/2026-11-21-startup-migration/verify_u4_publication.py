"""Exercise interrupted stages of the real publisher in disposable installations."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from verify_u2 import CHECKER, check_mirrors, command, prepare_initial_switch

# Interrupt after the on-disk operation, including a durable unlink during retirement.
INTERRUPT = """
import os, runpy, sys
publisher, stop_path, *args = sys.argv[1:]
main = runpy.run_path(publisher)['main']
write = main.__globals__['write_checked']
def interrupt(root, path, before, data):
    write(root, path, before, data)
    if path == stop_path:
        os._exit(87)
main.__globals__['write_checked'] = interrupt
sys.argv = [publisher, *args]
sys.exit(main())
"""


def run(workspace):
    pristine, publisher, args, canonical, working, retire = prepare_initial_switch(workspace)
    program = publisher.relative_to(pristine)
    args = [*args, '--initial-cutover']
    boundaries = [str(CHECKER), 'harness/common/base/AGENTS.template',
                  'harness/common/START.md', 'AGENTS.md', 'CLAUDE.md',
                  next(r['path'] for r in working if r['path'].startswith('.agents/skills/')),
                  next(r['path'] for r in working if r['path'].startswith('.claude/rules/')),
                  retire[0]['path']]
    request = Path(args[1])
    for path in [request / 'publication-report.md', request / 'publication.json',
                 request / 'candidate/harness/common/base/AGENTS.template']:
        file = pristine / path
        original = file.read_bytes()
        file.write_bytes(original + b' ')
        command(pristine, program, args, 2)
        assert not (pristine / '.harness-publication.json').exists()
        assert (pristine / 'harness/common/START.md').is_file()
        file.write_bytes(original)
    print('report, manifest, candidate mismatch before publication: OK', flush=True)
    for index, boundary in enumerate(boundaries):
        root = workspace / str(index)
        shutil.copytree(pristine, root)
        result = subprocess.run([sys.executable, '-B', '-c', INTERRUPT,
                                 str(program), boundary, *args], cwd=root,
                                capture_output=True, text=True)
        assert result.returncode == 87, (boundary, result.stderr)
        command(root, CHECKER, [], 2, 'publication')
        command(root, program, args, 0)
        command(root, CHECKER, [], 0)
        check_mirrors(root)
        assert not (root / '.harness-publication.json').exists()
        assert all(not (root / row['path']).exists() for row in canonical if row['after'] is None)
        assert not (root / retire[0]['path']).exists()
        print('resume verified after', boundary, flush=True)


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='harness-u4-publication-') as folder:
        run(Path(folder))
