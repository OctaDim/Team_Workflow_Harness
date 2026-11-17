"""Exercise root discovery through real pytest processes in temporary projects."""
import collections
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

SOURCE = Path(os.environ['HARNESS_DISCOVERY_SOURCE_ROOT']) if os.environ.get('HARNESS_DISCOVERY_SOURCE_ROOT') else Path(__file__).resolve().parents[4]
IGNORES = '--ignore=harness/common/inbox --ignore=harness/project/inbox'


def write(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding='utf-8')


def fixture_project(tmp_path, project_active=False, config='pytest.ini', empty=False):
    root = tmp_path / 'receiving project'
    root.mkdir()
    for rel in ('harness/common/scripts/run_tests.py', 'harness/common/checks/ensure_entrypoint_links.py'):
        source = SOURCE / rel
        write(root / rel, source.read_text(encoding='utf-8'))
    if config == 'pytest.ini':
        write(root / config, (SOURCE / 'harness/common/testing/pytest.ini').read_text(encoding='utf-8'))
    else:
        values = f'testpaths = .\naddopts = -ra --strict-markers -p receiving_plugin --import-mode=importlib {IGNORES}\npython_files = test_*.py spec_*.py\nmarkers = receiving: keep receiving project marker\n'
        if config == 'pyproject.toml':
            body = '[project]\nname = "receiving-fixture"\nversion = "1.0"\n[tool.pytest.ini_options]\ntestpaths = ["."]\naddopts = ["-ra", "--strict-markers", "-p", "receiving_plugin", "--import-mode=importlib", "--ignore=harness/common/inbox", "--ignore=harness/project/inbox"]\npython_files = ["test_*.py", "spec_*.py"]\nmarkers = ["receiving: keep receiving project marker"]\n'
        elif config == 'setup.cfg':
            body = '[metadata]\nname = receiving-fixture\n[tool:pytest]\n' + values
        else:
            body = '[tox]\nenvlist = py\n[pytest]\n' + values
        write(root / config, body)
        write(root / 'receiving_plugin.py', 'import pytest\n@pytest.fixture\ndef receiving_value(): return "kept"\n')
    active = {
        'harness': 'harness/common/testing/tests/test_active.py',
        'application': 'app/tests/test_active.py',
        'before': 'before/test_active.py',
        'candidate': 'candidate/test_active.py',
        'source': 'source/test_active.py',
    }
    if project_active:
        active['project'] = 'harness/project/testing/tests/test_active.py'
    archived = {
        'common-before': 'harness/common/inbox/request/before/test_snapshot.py',
        'common-candidate-1': 'harness/common/inbox/request/candidate-v1/test_snapshot.py',
        'common-candidate-2': 'harness/common/inbox/request/candidate-v2/test_snapshot.py',
        'project-source': 'harness/project/inbox/request/source/test_snapshot.py',
        'project-other': 'harness/project/inbox/other/merged/test_snapshot.py',
    }
    if config != 'pytest.ini':
        active['receiving-spec'] = 'app/tests/spec_receiving.py'
    if not empty:
        for label, rel in {**active, **archived, 'environment': '.venv/lib/test_environment.py'}.items():
            write_test_module(root, rel, label, marked=label == 'receiving-spec')
    return root, set(active), archived


def write_test_module(root, rel, label, marked=False):
    body = ('from pathlib import Path\nimport json,os\n'
            f'LOG = Path({str(root / ".events")!r})\n'
            'def event(kind):\n'
            f'    with LOG.open("a") as stream: stream.write(json.dumps({{"kind":kind,"case":{label!r},"pid":os.getpid()}})+"\\n")\n'
            'event("import")\n')
    if marked:
        body += 'import pytest\n@pytest.mark.receiving\n'
    body += ('def test_contract(receiving_value):\n    assert receiving_value == "kept"\n    event("run")\n' if marked else 'def test_contract():\n    event("run")\n')
    write(root / rel, body)


def execute(root, args, runner=False, cwd=None, label=''):
    (root / '.events').unlink(missing_ok=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
    command = ([sys.executable, str(root / 'harness/common/scripts/run_tests.py')] if runner else
               [sys.executable, '-m', 'pytest', *args])
    result = subprocess.run(command, cwd=cwd or root, env=env, capture_output=True, text=True, timeout=90)
    events = [json.loads(line) for line in (root / '.events').read_text().splitlines()] if (root / '.events').exists() else []
    observation = {'label': label, 'command': command, 'exit_code': result.returncode,
                   'events': events, 'stdout': result.stdout, 'stderr': result.stderr}
    if os.environ.get('HARNESS_DISCOVERY_RESULTS'):
        with Path(os.environ['HARNESS_DISCOVERY_RESULTS']).open('a') as stream:
            stream.write(json.dumps(observation) + '\n')
    return result, events


def assert_full(result, events, active):
    assert result.returncode == 0, result.stdout + result.stderr
    assert collections.Counter(e['case'] for e in events if e['kind'] == 'run') == collections.Counter(active)
    assert collections.Counter(e['case'] for e in events if e['kind'] == 'import') == collections.Counter(active)
    assert len({e['pid'] for e in events}) == 1


@pytest.mark.parametrize('project_active', [False, True], ids=['common', 'combined'])
@pytest.mark.parametrize('command', ['default', 'root', 'runner'])
def test_full_root_executes_active_once_excludes_inbox_imports(tmp_path, project_active, command):
    root, active, _ = fixture_project(tmp_path, project_active)
    result, events = execute(root, [] if command == 'default' else ['.'], runner=command == 'runner', label=f'full-{command}-{project_active}')
    assert_full(result, events, active)


@pytest.mark.parametrize('project_active', [False, True], ids=['common', 'combined'])
@pytest.mark.parametrize('target,label', [
    ('harness/common/inbox/request/candidate-v1/test_snapshot.py', 'common-candidate-1'),
    ('harness/common/inbox/request/candidate-v1', 'common-candidate-1'),
    ('harness/common/inbox/request/before', 'common-before'),
    ('harness/project/inbox/request/source', 'project-source'),
])
def test_explicit_inbox_target_remains_available(tmp_path, project_active, target, label):
    root, _, _ = fixture_project(tmp_path, project_active)
    result, events = execute(root, [target], label=f'explicit-{label}-{project_active}')
    assert_full(result, events, {label})


@pytest.mark.parametrize('project_active', [False, True], ids=['common', 'combined'])
def test_mixed_selection_is_not_strict_archive_exclusion(tmp_path, project_active):
    root, active, _ = fixture_project(tmp_path, project_active)
    result, events = execute(root, ['.', 'harness/common/inbox/request/candidate-v1'], label=f'mixed-{project_active}')
    assert result.returncode == 0, result.stdout + result.stderr
    ran = {e['case'] for e in events if e['kind'] == 'run'}
    assert 'common-candidate-1' in ran
    assert 'environment' not in ran


@pytest.mark.parametrize('project_active', [False, True], ids=['common', 'combined'])
@pytest.mark.parametrize('config', ['pyproject.toml', 'tox.ini', 'setup.cfg'])
def test_runner_preserves_receiving_configuration(tmp_path, project_active, config):
    root, active, _ = fixture_project(tmp_path, project_active, config)
    before = (root / config).read_bytes()
    result, events = execute(root, [], runner=True, label=f'config-{config}-{project_active}')
    assert_full(result, events, active)
    assert (root / config).read_bytes() == before
    assert not (root / 'pytest.ini').exists()


def test_runner_works_from_other_directory(tmp_path):
    root, active, _ = fixture_project(tmp_path)
    result, events = execute(root, [], runner=True, cwd=tmp_path, label='runner-foreign-cwd')
    assert_full(result, events, active)


def test_runner_preserves_empty_selection_exit_code(tmp_path):
    root, _, _ = fixture_project(tmp_path, empty=True)
    result, _ = execute(root, [], runner=True, label='empty')
    assert result.returncode == 5, result.stdout + result.stderr


def test_runner_reports_failure_outside_harness(tmp_path):
    root, _, _ = fixture_project(tmp_path)
    write(root / 'app/tests/test_failure.py', 'def test_failure():\n    assert False, "intentional receiving test failure"\n')
    result, _ = execute(root, [], runner=True, label='intentional-failure')
    assert result.returncode == 1, result.stdout + result.stderr


def test_nested_config_requires_explicit_selection(tmp_path):
    root, active, _ = fixture_project(tmp_path)
    write(root / 'app/tests/pytest.ini', '[pytest]\npython_files = spec_nested.py\naddopts = --import-mode=importlib\n')
    write_test_module(root, 'app/tests/spec_nested.py', 'nested-config')
    result, events = execute(root, ['.'], label='root-ignores-nested-config')
    assert_full(result, events, active)
    result, events = execute(root, ['-c', 'app/tests/pytest.ini', 'app/tests'], label='explicit-nested-config')
    assert_full(result, events, {'nested-config'})


def test_portable_source_needs_no_receiving_root_ini(tmp_path, monkeypatch):
    source = tmp_path / 'portable source'
    for rel in ('harness/common/scripts/run_tests.py',
                'harness/common/checks/ensure_entrypoint_links.py',
                'harness/common/testing/pytest.ini'):
        write(source / rel, (SOURCE / rel).read_text(encoding='utf-8'))
    assert not (source / 'pytest.ini').exists()
    monkeypatch.setattr(sys.modules[__name__], 'SOURCE', source)
    receiving = tmp_path / 'receiver'
    receiving.mkdir()
    root, active, _ = fixture_project(receiving)
    result, events = execute(root, [], label='portable-source-no-root-config')
    assert_full(result, events, active)
