"""Exercise the author workflow and consume its package in a fresh project."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

COMMON = Path(__file__).absolute().parents[2]
REPO = COMMON.parents[1]
CHECK = Path('harness/common/checks/ensure_entrypoint_links.py')
RUN = Path('harness/common/scripts/run_tests.py')
RESOURCE = Path('harness/common/base/AGENTS.bootstrap.json')
LAYOUT = Path('harness/AGENTS.bootstrap.md.in')
COMMAND = 'python3 harness/common/checks/ensure_entrypoint_links.py'


def run(root, entry):
    return subprocess.run([sys.executable, '-B', str(entry)], cwd=root, capture_output=True, text=True)


@pytest.fixture
def author(tmp_path):
    for name in (CHECK, RUN, RESOURCE, Path('harness/common/START.md'),
                 Path('harness/common/INDEX.md'), Path('harness/common/base/project-skeleton.json')):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / name, target)
    # Recreate an author checkout even when the suite runs in a package-only install.
    (tmp_path / LAYOUT).write_text(json.loads((tmp_path / RESOURCE).read_bytes())['layout'])
    for folder in ['harness/common/rules', '.claude/rules']:
        directory = tmp_path / folder
        directory.mkdir(parents=True)
        (directory / 'comm-test.md').write_text('# Mandatory rule\n')
    (tmp_path / 'AGENTS.md').write_text('# Project\n\n```sh\n' + COMMAND + '\n```\nPersonal preference.\n')
    (tmp_path / 'test_example.py').write_text('def test_example():\n    assert True\n')
    first = run(tmp_path, CHECK)
    assert first.returncode == 0, first.stderr
    return tmp_path


@pytest.mark.parametrize('entry', [CHECK, RUN], ids=['startup', 'test-runner'])
def test_source_changes_update_only_template_then_generate(author, tmp_path_factory, entry):
    agents = author / 'AGENTS.md'
    agents.write_text(agents.read_text().replace(COMMAND, COMMAND.replace('python3 ', 'python3 -B ')))
    existing = agents.read_bytes()
    start = author / 'harness/common/START.md'
    start.write_text(start.read_text().rstrip() + '\nКонтроль порядка в тестовой установке.\n')
    result = run(author, entry)
    assert result.returncode == 0, result.stderr
    notice, = [line for line in result.stdout.splitlines() if line.startswith('BOOTSTRAP:')]
    assert 'AGENTS.md (команда запуска)' in notice and 'harness/common/START.md (порядок чтения)' in notice
    assert str(RESOURCE) + ' → AGENTS.md' in notice and 'каркас' not in notice
    assert agents.read_bytes() == existing
    template = author / RESOURCE
    snapshot = (template.read_bytes(), template.stat().st_mtime_ns)
    (author / 'test_example.py').write_text('def test_another():\n    assert True\n')
    agents.write_text(agents.read_text().replace('Personal preference.', 'Another personal preference.'))
    again = run(author, entry)
    assert again.returncode == 0 and 'BOOTSTRAP:' not in again.stdout
    assert snapshot == (template.read_bytes(), template.stat().st_mtime_ns)

    consumer = tmp_path_factory.mktemp('consumer')
    shutil.copytree(author / 'harness/common', consumer / 'harness/common')
    shutil.copytree(author / '.claude/rules', consumer / '.claude/rules')
    assert not (consumer / 'AGENTS.md').exists()
    generated = run(consumer, CHECK)
    assert generated.returncode == 0, generated.stderr
    text = (consumer / 'AGENTS.md').read_text()
    assert COMMAND.replace('python3 ', 'python3 -B ') in text
    assert 'Контроль порядка в тестовой установке.' in text and 'preference' not in text


def test_layout_change_and_invalid_input_preserve_last_complete_template(author):
    layout = author / LAYOUT
    layout.write_text(layout.read_text() + '\nPortable notice.\n')
    result = run(author, CHECK)
    assert result.returncode == 0 and str(LAYOUT) + ' (каркас)' in result.stdout
    resource = author / RESOURCE
    snapshot = resource.read_bytes()
    assert 'Portable notice.' in json.loads(snapshot)['layout']
    layout.write_text(layout.read_text().replace('$command', '$unknown'))
    failed = run(author, CHECK)
    assert failed.returncode and 'обновлено 0' in failed.stderr and str(RESOURCE) in failed.stderr
    assert resource.read_bytes() == snapshot
