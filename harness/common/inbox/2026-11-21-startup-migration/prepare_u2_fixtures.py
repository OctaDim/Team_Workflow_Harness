"""Build fresh installations for this INBOX request; print their temporary parent."""
import json
import os
from pathlib import Path
import shutil
import tempfile


REQUEST = Path(__file__).absolute().parent
REPOSITORY = REQUEST.parents[3]
CANDIDATE = REQUEST / 'candidate'
MODES = ('common-only', 'common-project')


def ordinary(path):
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError(f'Symlink in fixture input: {part}')
    return path


def copy_package(source, destination, strip_history):
    ordinary(source)
    if not source.is_dir():
        raise ValueError(f'Missing fixture package: {source}')
    for parent, directories, files in os.walk(source, onerror=raise_error):
        parent = ordinary(Path(parent))
        relative = parent.relative_to(source)
        target = ordinary(destination / relative)
        target.mkdir(exist_ok=True, parents=True)
        if strip_history and (relative in (Path('inbox'), Path('handoffs'))
                              or relative.is_relative_to('testing/evidence')):
            # Keep the two project map targets, excluding their historical records.
            directories[:] = [name for name in directories
                              if relative == Path('testing/evidence')
                              and name in ('work', 'harness')]
            files = [name for name in files if name == 'README.human.md']
        for name in directories:
            ordinary(parent / name)
        for name in files:
            file = ordinary(parent / name)
            if not file.is_file():
                raise ValueError(f'Invalid fixture input: {file}')
            shutil.copy2(file, ordinary(target / name))


def raise_error(error):
    raise error


def prepare():
    ordinary(CANDIDATE)
    retire = json.loads(ordinary(REQUEST / 'u2-retire.json').read_text(encoding='utf-8'))
    workspace = Path(tempfile.mkdtemp(prefix='harness-startup-u2-'))
    if workspace.is_relative_to(REPOSITORY):
        workspace.rmdir()
        raise ValueError('Use a temporary directory outside the working repository.')
    for mode in MODES:
        root = workspace / mode
        packages = ('common',) if mode == 'common-only' else ('common', 'project')
        for package in packages:
            relative = Path('harness') / package
            copy_package(REPOSITORY / relative, root / relative, strip_history=True)
            copy_package(CANDIDATE / relative, root / relative, strip_history=False)
        for name in retire:
            path = Path(name)
            if path.is_absolute() or '..' in path.parts:
                raise ValueError(f'Invalid fixture retirement: {name}')
            ordinary(root / path).unlink(missing_ok=True)
        if mode == 'common-project':
            # Include actual project data in the preservation check.
            (root / 'harness/project/base/fixture.txt').write_bytes(b'U2 project fixture\n')
    return workspace


if __name__ == '__main__':
    print(prepare())
