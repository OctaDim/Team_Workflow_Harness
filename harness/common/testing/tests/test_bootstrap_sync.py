"""The checker consumes approved templates. Neither startup nor pytest reverse-syncs."""
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


COMMON = Path(__file__).resolve().parents[2]
RUN = Path('harness/common/scripts/run_tests.py')


def test_working_conflict_never_updates_approved_template(installed, startup):
    base = installed / 'harness/common/base'
    template = base / 'AGENTS.template'
    before = template.read_bytes(), template.stat().st_mtime_ns
    entry = installed / 'AGENTS.md'
    entry.write_bytes(b'User changes\r\n')
    result = startup(installed)
    assert result.returncode == 2 and 'AGENTS.md' in result.stderr
    assert entry.read_bytes() == b'User changes\r\n'
    assert before == (template.read_bytes(), template.stat().st_mtime_ns)
    entry.unlink()
    assert startup(installed).returncode == 3
    assert entry.read_bytes() == before[0]
    assert before == (template.read_bytes(), template.stat().st_mtime_ns)
    assert not (base / 'AGENTS.bootstrap.json').exists()
    assert not (installed / 'harness/AGENTS.bootstrap.md.in').exists()


def test_ordinary_test_runner_never_reverse_syncs(installed):
    runner = installed / RUN
    runner.parent.mkdir(exist_ok=True)
    shutil.copyfile(COMMON / 'scripts/run_tests.py', runner)
    template = installed / 'harness/common/base/AGENTS.template'
    before = template.read_bytes(), template.stat().st_mtime_ns
    entry = installed / 'AGENTS.md'
    entry.write_bytes(b'Independent text in the test checkout\n')
    (installed / 'test_example.py').write_text('def test_example():\n    assert True\n')
    result = subprocess.run([sys.executable, '-B', str(runner)], cwd=installed,
                            capture_output=True, text=True)
    assert result.returncode == 0 and '1 passed' in result.stdout, result.stdout + result.stderr
    assert before == (template.read_bytes(), template.stat().st_mtime_ns)
    assert entry.read_bytes() == b'Independent text in the test checkout\n'
    assert not (installed / 'harness/common/base/AGENTS.bootstrap.json').exists()


@pytest.mark.parametrize('name', ['AGENTS', 'CLAUDE'])
def test_missing_canonical_template_cannot_be_rebuilt_from_working_input(installed, startup, name):
    template = installed / 'harness/common/base' / (name + '.template')
    entry = installed / (name + '.md')
    existing = entry.read_bytes()
    template.unlink()
    result = startup(installed)
    assert result.returncode == 2 and str(template) in result.stderr
    assert not template.exists() and entry.read_bytes() == existing
