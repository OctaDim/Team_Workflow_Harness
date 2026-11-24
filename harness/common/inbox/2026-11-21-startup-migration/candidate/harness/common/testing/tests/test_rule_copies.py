"""Check installed shared rules and exercise copy-drift failures."""
import importlib.util
import tempfile
import pytest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CHECK = Path('harness/common/checks/ensure_entrypoint_links.py')


spec = importlib.util.spec_from_file_location('common_rule_copy_checks', ROOT / CHECK)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
check_rule_copies = checker.check_rule_copies


def test_combined_startup_check_is_short_and_read_only(installed, startup):
    inputs = [installed / name for name in ('AGENTS.md', 'CLAUDE.md', '.claude/rules/comm-fixture.md')]
    original = [(path.read_bytes(), path.stat().st_mtime_ns) for path in inputs]
    result = startup(installed, CHECK, '--check-startup')
    assert (result.returncode, result.stdout, result.stderr) == (0, 'OK\n', '')
    assert [(path.read_bytes(), path.stat().st_mtime_ns) for path in inputs] == original
    assert inputs[1].read_bytes() == b''


@pytest.mark.parametrize('combined', (False, True), ids=('common-only', 'common-project'))
def test_combined_startup_check_reports_all_safe_mismatches(installed, startup, combined):
    native = installed / '.claude/rules'
    native.mkdir(exist_ok=True)
    (native / 'sub').mkdir()
    (native / 'sub/stale.md').write_bytes(b'preserve this copy')
    (native / 'README.human.md').write_bytes(b'human only')
    (native / 'comm-fixture.md').write_bytes(b'changed')
    (installed / 'AGENTS.md').write_bytes(b'')
    (installed / 'CLAUDE.md').unlink()
    expected = {
        '.claude/rules/comm-fixture.md': 'отличается от канона',
        '.claude/rules/sub/stale.md': 'лишний',
        'AGENTS.md': 'отличается от канона',
        'CLAUDE.md': 'отсутствует',
    }
    if combined:
        folder = installed / 'harness/project/rules/sub'
        folder.mkdir(parents=True, exist_ok=True)
        (folder / 'proj-missing.md').write_bytes(b'published')
        expected['.claude/rules/sub/proj-missing.md'] = 'отсутствует'
    result = startup(installed, CHECK, '--check-startup')
    assert result.returncode == 4
    assert dict(line.split('\t', 1) for line in result.stdout.splitlines()) == expected
    assert result.stderr == ''
    assert (native / 'sub/stale.md').read_bytes() == b'preserve this copy'
    assert (native / 'comm-fixture.md').read_bytes() == b'changed'
    assert (installed / 'AGENTS.md').read_bytes() == b''
    assert not (installed / 'CLAUDE.md').exists()


class TestRuleCopies:

    def test_installed_rule_copies(self):
        count = check_rule_copies(ROOT)
        print(f'Checked {count} shared rule copies.')

    def test_project_only_rules_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'harness/project/rules'
            native = root / '.claude/rules'
            source.mkdir(parents=True)
            native.mkdir(parents=True)
            for folder in (source, native):
                (folder / 'proj-example.md').write_bytes(b'canonical\n')
            with pytest.raises(ValueError, match='common'):
                check_rule_copies(root)

    @pytest.mark.parametrize('mode', (('common',), ('common', 'project')), ids=['common', 'common-project'])
    def test_copy_drift_is_detected(self, mode):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            native = root / '.claude/rules'
            native.mkdir(parents=True)
            for package in mode:
                rules = root / 'harness' / package / 'rules'
                rules.mkdir(parents=True)
                prefix = 'comm-' if package == 'common' else 'proj-'
                (rules / (prefix + 'example.md')).write_bytes(b'canonical\n')
                (rules / 'README.human.md').write_bytes(b'')
                (native / (prefix + 'example.md')).write_bytes(b'canonical\n')
            extra_personal = native / 'personal.md'
            extra_personal.write_bytes(b'personal\n')
            with pytest.raises(ValueError, match='personal.md'):
                check_rule_copies(root)
            assert extra_personal.read_bytes() == b'personal\n'
            extra_personal.unlink()
            assert check_rule_copies(root) == len(mode)
            source = next((root / 'harness' / mode[0] / 'rules').glob('*-example.md'))
            copy = native / source.name
            copy.unlink()
            with pytest.raises(ValueError, match='Missing or different rule copy'):
                check_rule_copies(root)
            copy.write_bytes(b'changed\n')
            with pytest.raises(ValueError, match='Missing or different rule copy'):
                check_rule_copies(root)
            copy.unlink()
            copy.symlink_to(source)
            with pytest.raises(ValueError, match='Symlink forbidden'):
                check_rule_copies(root)
            copy.unlink()
            copy.write_bytes(source.read_bytes())
            extra = native / (source.name.split('-')[0] + '-stale.md')
            extra.write_bytes(b'stale\n')
            with pytest.raises(ValueError, match='Unmanaged native rule'):
                check_rule_copies(root)
            extra.unlink()
            assert check_rule_copies(root) == len(mode)
        with tempfile.TemporaryDirectory() as directory:
            with pytest.raises(ValueError, match='common'):
                check_rule_copies(Path(directory))
