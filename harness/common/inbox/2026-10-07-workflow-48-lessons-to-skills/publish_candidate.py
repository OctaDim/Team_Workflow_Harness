"""Publish only reviewed manifest paths, refusing unexpected source changes."""
import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def main():
    manifest = json.loads((HERE / 'publication-files.json').read_text())
    protected = {p: digest(ROOT / p) for p in ['AGENTS.md', 'CLAUDE.md']}
    for item in manifest['files']:
        path = Path(item['path'])
        assert not path.is_absolute() and '..' not in path.parts
        assert path.parts[0] in ['harness', '.agents', '.claude']
        assert path.name not in ['AGENTS.md', 'CLAUDE.md']
        target, candidate = ROOT / path, HERE / 'candidate' / path
        assert not target.is_symlink() and not candidate.is_symlink(), str(path)
        assert digest(target) == item['before'], f'Unexpected target: {path}'
        assert digest(candidate) == item['after'], f'Unexpected candidate: {path}'
    for item in manifest['files']:
        target = ROOT / item['path']
        if item['action'] == 'delete':
            target.unlink()
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE / 'candidate' / item['path'], target)
        assert digest(target) == item['after'], item['path']
    for package in ['common', 'project']:
        (ROOT / 'harness' / package / 'lessons').rmdir()
    assert protected == {p: digest(ROOT / p) for p in protected}
    (HERE / 'publication-result.json').write_text(json.dumps({
        'version': manifest['version'], 'files': len(manifest['files']),
        'protected_entrypoints': protected, 'status': 'published',
        'verification_status': 'not-verified',
    }, indent=2) + '\n')
    print(f"Published {len(manifest['files'])} reviewed paths; protected entrypoints unchanged")


if __name__ == '__main__':
    main()
