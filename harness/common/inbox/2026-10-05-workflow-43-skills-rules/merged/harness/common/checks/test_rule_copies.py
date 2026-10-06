"""Check installed shared rules and exercise copy-drift failures."""
import tempfile
import pytest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def check_rule_copies(root):
    native = root / '.claude/rules'
    sources = {}
    installed_prefixes = []
    for package, prefix in (('common', 'comm-'), ('project', 'proj-')):
        rules = root / 'harness' / package / 'rules'
        if rules.is_dir():
            installed_prefixes.append(prefix)
            sources.update((file.name, file) for file in rules.glob(prefix + '*.md'))
    if not sources:
        raise ValueError('No canonical shared rules found; nothing checked.')
    expected = set(sources)
    actual = {file.name for prefix in installed_prefixes
              for file in native.glob(prefix + '*.md')}
    if expected != actual:
        raise ValueError(f'Missing copies: {sorted(expected - actual)}; '
                         f'extra copies: {sorted(actual - expected)}')
    for name, source in sorted(sources.items()):
        copy = native / name
        for file in (source, copy):
            if not file.is_file() or any(path.is_symlink() for path in (file, *file.parents)):
                raise ValueError(f'Not an ordinary file: {file}')
        if source.read_bytes() != copy.read_bytes():
            raise ValueError(f'Different rule bytes: {name}')
    return len(sources)


class TestRuleCopies:

    def test_installed_rule_copies(self):
        count = check_rule_copies(ROOT)
        print(f'Checked {count} shared rule copies.')

    @pytest.mark.parametrize('mode', (('common',), ('project',), ('common', 'project')), ids=['common', 'project', 'common-project'])
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
            with pytest.raises(ValueError, match='nothing checked'):
                check_rule_copies(Path(directory))
