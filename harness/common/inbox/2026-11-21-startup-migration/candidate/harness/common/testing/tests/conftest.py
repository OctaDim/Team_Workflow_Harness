"""Small published packages for tests that deliberately damage an installation."""
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


COMMON = Path(__file__).resolve().parents[2]
CHECK = Path('harness/common/checks/ensure_entrypoint_links.py')


@pytest.fixture
def published(tmp_path):
    """A common package without installed files; startup creates a neutral project."""
    common = tmp_path / 'harness/common'
    for name in ('checks/ensure_entrypoint_links.py', 'base/AGENTS.template',
                 'base/CLAUDE.template', 'base/project-skeleton.json', 'INDEX.md'):
        path = common / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(COMMON / name, path)
    rules = common / 'rules'
    rules.mkdir()
    (rules / 'comm-fixture.md').write_bytes(b'# Published rule\r\n')
    (rules / 'README.human.md').write_bytes(b'Human-only guide\n')
    return tmp_path


@pytest.fixture
def startup():
    def execute(root, script=CHECK, *args, no_git=True):
        env = os.environ.copy()
        if no_git:
            env['PATH'] = '/no-git-for-this-test'
        return subprocess.run([sys.executable, '-I', '-B', str(script), *map(str, args)],
                              cwd=root, env=env, capture_output=True, text=True)
    return execute


@pytest.fixture
def installed(published, startup):
    first = startup(published)
    assert first.returncode == 3, first.stdout + first.stderr
    return published


@pytest.fixture
def checker(published):
    spec = importlib.util.spec_from_file_location('startup_checker_fixture', published / CHECK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
