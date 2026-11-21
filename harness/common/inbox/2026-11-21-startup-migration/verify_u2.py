"""Exercise the candidate in two new disposable installations (no model sessions)."""
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys

from prepare_u2_fixtures import CANDIDATE, MODES, REPOSITORY, REQUEST, copy_package, prepare


CHECKER = Path('harness/common/checks/ensure_entrypoint_links.py')
PUBLISHER = Path('harness/common/scripts/publish_startup_set.py')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def command(root, program, args, expected, contains=''):
    result = subprocess.run([sys.executable, '-B', str(program), *args], cwd=root,
                            capture_output=True, text=True)
    output = result.stdout + result.stderr
    if result.returncode != expected or contains not in output:
        raise RuntimeError(f'{program}: expected {expected} / {contains!r}; '
                           f'observed {result.returncode}: {output[-600:]}')


def snapshot(directory):
    return {p.relative_to(directory): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob('*') if p.is_file()}


def check_mirrors(root):
    common = root / 'harness/common'
    for skill in (common / 'skills').iterdir():
        if skill.is_dir():
            reference = snapshot(skill)
            for client in ('.agents', '.claude'):
                assert snapshot(root / client / 'skills' / skill.name) == reference
    expected = {p.relative_to(common / 'rules'): p.read_bytes()
                for p in (common / 'rules').rglob('*.md') if p.name != 'README.human.md'}
    native = root / '.claude/rules'
    assert expected == {p.relative_to(native): p.read_bytes() for p in native.rglob('*.md')}
    for name in ('AGENTS', 'CLAUDE'):
        assert (root / (name + '.md')).read_bytes() == (common / 'base' / (name + '.template')).read_bytes()


def verify_start(root, mode):
    project = root / 'harness/project'
    previous = snapshot(project) if project.exists() else None
    command(root, CHECKER, [], 3)
    command(root, CHECKER, [], 0)
    check_mirrors(root)
    assert not (project / 'START.md').exists()
    assert not (root / 'harness/common/START.md').exists()
    assert (project / 'INDEX.md').read_bytes() == (CANDIDATE / 'harness/project/INDEX.md').read_bytes()
    if previous is not None:
        assert snapshot(project) == previous
    print(mode, 'bootstrap / repeat / maps / installed bytes: OK')

    rule = 'comm-application-config-git.md'
    source = root / 'harness/common/rules' / rule
    native = root / '.claude/rules' / rule
    original = source.read_bytes()
    native.unlink()
    conflict = root / '.claude/rules/team.md'
    conflict.write_bytes(b'test-only personal rule\n')
    command(root, CHECKER, [], 2, 'team.md')
    assert conflict.is_file() and not native.exists()
    conflict.unlink()
    protected = root / 'CLAUDE.md'
    protected.write_bytes(b'@AGENTS.md\n')
    command(root, CHECKER, [], 2, 'CLAUDE.md')
    assert protected.read_bytes() == b'@AGENTS.md\n' and not native.exists()
    protected.unlink()
    command(root, CHECKER, [], 3)
    assert native.read_bytes() == original and protected.read_bytes() == b''
    command(root, CHECKER, [], 0)
    print(mode, 'unknown rule / protected conflict / recovery: OK')
    verify_release(root, source.relative_to(root), native.relative_to(root))


def verify_release(root, source, native):
    # This receipt authorizes a synthetic file version in this temporary root only.
    request = Path('harness/common/inbox/u2-fixture')
    dest = root / request
    source_file, mirror = root / source, root / native
    old = source_file.read_bytes()
    new = old + b'\nU2 isolated publication fixture\n'
    candidate = dest / 'candidate' / source
    candidate.parent.mkdir(parents=True)
    candidate.write_bytes(new)
    mirror.unlink()
    command(root, CHECKER, [], 3)
    assert mirror.read_bytes() == old
    mirror.write_bytes(b'damaged local test copy\n')
    command(root, CHECKER, [], 3)
    assert mirror.read_bytes() == old
    report = b'Synthetic fixture only. No product approval.\n'
    (dest / 'publication-report.md').write_bytes(report)
    manifest = {'schema': 1, 'request': str(request), 'report_sha256': sha(report),
                'canonical': [{'path': str(source), 'before': sha(old), 'after': sha(new)}],
                'working': [{'path': str(native), 'source': str(source),
                             'before': sha(old), 'after': sha(new)}], 'retire': []}
    raw = json.dumps(manifest).encode()
    (dest / 'publication.json').write_bytes(raw)
    args = ['--request', str(request), '--approve-sha256', sha(raw),
            '--approval-id', 'isolated-U2-fixture']
    command(root, PUBLISHER, args, 2)
    assert source_file.read_bytes() == mirror.read_bytes() == old
    approval = {'request': str(request), 'manifest_sha256': sha(raw), 'decision': 'publish',
                'reference': 'isolated-U2-fixture'}
    (dest / 'publication-approval.json').write_text(json.dumps(approval), encoding='utf-8')
    # Stop the actual publisher process after it writes the canonical file.
    # The restart must discover the journal on disk in a different process.
    driver = """
import os, runpy, sys
ns = runpy.run_path(sys.argv[1])
main = ns['main']
real_write = main.__globals__['write_checked']
def interrupted(root, path, before, data):
    real_write(root, path, before, data)
    if path == stop_at:
        os._exit(87)
main.__globals__['write_checked'] = interrupted
stop_at = sys.argv[2]
sys.argv = [sys.argv[1], *sys.argv[3:]]
sys.exit(main())
"""
    result = subprocess.run([sys.executable, '-B', '-c', driver, str(PUBLISHER),
                             str(source), *args], cwd=root, capture_output=True)
    if result.returncode != 87:
        raise RuntimeError(f'Interrupted fixture failed: {result.returncode} {result.stderr[-400:]!r}')
    assert source_file.read_bytes() == new and mirror.read_bytes() == old
    command(root, CHECKER, [], 2, 'publication')
    mirror.write_bytes(b'third version')
    command(root, PUBLISHER, args, 2)
    assert mirror.read_bytes() == b'third version'
    mirror.write_bytes(old)
    command(root, PUBLISHER, args, 0)
    assert source_file.read_bytes() == mirror.read_bytes() == new
    assert not (root / '.harness-publication.json').exists()
    command(root, PUBLISHER, args, 0)
    shutil.rmtree(dest)
    mirror.unlink()
    command(root, CHECKER, [], 3)
    assert mirror.read_bytes() == new
    command(root, CHECKER, [], 0)
    print(root.name, 'v1/v2 / approval / interruption / resume / removed request: OK')


def verify_initial_switch(workspace):
    """Switch a copy of the old installation, including the actual legacy entrypoints."""
    root = workspace / 'first-switch'
    for subtree in ('harness/common', 'harness/project', '.agents/skills', '.claude/skills',
                    '.claude/rules'):
        copy_package(REPOSITORY / subtree, root / subtree, strip_history=True)
    for path in ('AGENTS.md', 'CLAUDE.md', 'harness/README.human.md',
                 'harness/AGENTS.bootstrap.md.in'):
        shutil.copy2(REPOSITORY / path, root / path)

    request = Path('harness/common/inbox/u2-initial-fixture')
    dest = root / request
    copy_package(CANDIDATE, dest / 'candidate', strip_history=False)
    report = b'Isolated initial switch fixture. No product approval.\n'
    (dest / 'publication-report.md').write_bytes(report)
    canonical, working, retire = [], [], []
    publisher = dest / 'candidate' / PUBLISHER
    mirrors = runpy.run_path(str(publisher))['working_paths']

    def before(relative):
        old = root / relative
        return sha(old.read_bytes()) if old.is_file() else None

    for file in sorted((dest / 'candidate/harness').rglob('*')):
        if not file.is_file():
            continue
        relative = file.relative_to(dest / 'candidate').as_posix()
        old, new = before(relative), sha(file.read_bytes())
        if old == new:
            continue
        canonical.append({'path': relative, 'before': old, 'after': new})
        for target in mirrors(relative):
            working.append({'path': target, 'source': relative, 'before': before(target),
                            'after': new})
    for path in json.loads((REQUEST / 'u2-retire.json').read_text(encoding='utf-8')):
        if path == 'harness/AGENTS.bootstrap.md.in':
            retire.append({'path': path, 'before': before(path)})
        else:
            canonical.append({'path': path, 'before': before(path), 'after': None})

    raw = json.dumps({'schema': 1, 'request': request.as_posix(), 'canonical': canonical,
                      'working': working, 'retire': retire, 'report_sha256': sha(report)}).encode()
    (dest / 'publication.json').write_bytes(raw)
    approval = {'request': request.as_posix(), 'decision': 'publish',
                'manifest_sha256': sha(raw), 'reference': 'isolated-first-switch'}
    (dest / 'publication-approval.json').write_text(json.dumps(approval), encoding='utf-8')
    args = ['--request', request.as_posix(), '--approve-sha256', sha(raw),
            '--approval-id', 'isolated-first-switch']
    command(root, publisher, args, 2)
    assert (root / 'CLAUDE.md').read_bytes() == (REPOSITORY / 'CLAUDE.md').read_bytes()
    command(root, publisher, [*args, '--initial-cutover'], 0)
    command(root, CHECKER, [], 0)
    check_mirrors(root)
    assert all(not (root / r['path']).exists() for r in canonical if r['after'] is None)
    assert not (root / retire[0]['path']).exists()
    print('first-switch', len(canonical), 'canonical operations,', len(working),
          'working operations,', len(retire), 'legacy author layout: OK')


if __name__ == '__main__':
    workspace = prepare()
    print(workspace, flush=True)
    for installation in MODES:
        verify_start(workspace / installation, installation)
    verify_initial_switch(workspace)
