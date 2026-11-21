"""Check installed shared rules and exercise copy-drift failures."""
import importlib.util
import tempfile
import pytest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


spec = importlib.util.spec_from_file_location('common_rule_copy_checks', ROOT / 'harness/common/checks/ensure_entrypoint_links.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
check_rule_copies = checker.check_rule_copies


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
            (native / 'personal.md').write_bytes(b'personal\n')
            assert check_rule_copies(root) == len(mode)
            source = next((root / 'harness' / mode[0] / 'rules').glob('*-example.md'))
            copy = native / source.name
            copy.unlink()
            with pytest.raises(ValueError, match='Missing copies'):
                check_rule_copies(root)
            copy.write_bytes(b'changed\n')
            with pytest.raises(ValueError, match='Different rule bytes'):
                check_rule_copies(root)
            copy.unlink()
            copy.symlink_to(source)
            with pytest.raises(ValueError, match='Not an ordinary file'):
                check_rule_copies(root)
            copy.unlink()
            copy.write_bytes(source.read_bytes())
            extra = native / (source.name.split('-')[0] + '-stale.md')
            extra.write_bytes(b'stale\n')
            with pytest.raises(ValueError, match='extra copies'):
                check_rule_copies(root)
            extra.unlink()
            assert check_rule_copies(root) == len(mode)
        with tempfile.TemporaryDirectory() as directory:
            with pytest.raises(ValueError, match='common'):
                check_rule_copies(Path(directory))
