"""Observable repair messages, concurrent edits, and metadata on working copies."""
from pathlib import Path
import hashlib
import os
import struct
import subprocess
import sys

import pytest


NATIVE = Path('.claude/rules/comm-fixture.md')
NOTICE = 'Восстановление'
POLICY = 'технически не заблокировано'


def test_conflict_reports_digests_offset_and_route_without_echoing_contents(installed, startup):
    entry = installed / 'AGENTS.md'
    approved = entry.read_bytes()
    unexpected = approved[:2] + b'Private settings'
    entry.write_bytes(unexpected)
    result = startup(installed)
    assert result.returncode == 2 and POLICY in result.stdout
    assert str(entry) in result.stderr and 'offset 2' in result.stderr and 'INBOX' in result.stderr
    for data in (approved, unexpected):
        assert hashlib.sha256(data).hexdigest() in result.stderr
    assert 'Private settings' not in result.stdout + result.stderr
    assert entry.read_bytes() == unexpected


def test_recovery_requests_fresh_context_only_after_changes(installed, startup):
    (installed / NATIVE).unlink()
    result = startup(installed)
    assert result.returncode == 3 and NOTICE in result.stdout and 'новую сессию' in result.stdout
    assert str(installed / NATIVE) in result.stdout
    repeat = startup(installed)
    assert repeat.returncode == 0 and POLICY in repeat.stdout
    assert NOTICE not in repeat.stdout and 'новую сессию' not in repeat.stdout


CHECK_START = '--check-start-entrypoints'


def check_start(root, startup, *args):
    return startup(root, 'harness/common/checks/ensure_entrypoint_links.py', *args)


def digest(data):
    return hashlib.sha256(data).hexdigest()


@pytest.mark.parametrize(('name', 'empty'), [
    ('AGENTS.md', False), ('CLAUDE.md', False), ('AGENTS.md', True),
])
def test_check_start_recovers_only_missing_or_empty_protected_input(installed, startup, name, empty):
    entry = installed / name
    expected = entry.read_bytes()
    rule = installed / NATIVE
    rule.write_bytes(b'Separate conflicting rule')
    if empty:
        entry.write_bytes(b'')
    else:
        entry.unlink()
    result = check_start(installed, startup, CHECK_START)
    assert result.returncode == 3
    assert str(entry) in result.stdout and 'новую сессию' in result.stdout
    assert ('файл пуст' if empty else 'файл отсутствует') in result.stdout
    assert entry.read_bytes() == expected
    assert rule.read_bytes() == b'Separate conflicting rule'
    assert check_start(installed, startup, CHECK_START).returncode == 0
    assert check_start(installed, startup, '--check-rules').returncode == 4


def test_check_start_preserves_nonempty_inputs_and_reports_all_paths(installed, startup):
    unexpected = {'AGENTS.md': b' ', 'CLAUDE.md': b'@AGENTS.md\n'}
    for name, value in unexpected.items():
        (installed / name).write_bytes(value)
    result = check_start(installed, startup, CHECK_START)
    assert result.returncode == 2 and 'INBOX' in result.stderr
    assert 'резервный коммит' in result.stderr and 'восстановление этих входов из канона' in result.stderr
    for name, value in unexpected.items():
        assert str(installed / name) in result.stderr and digest(value) in result.stderr
        assert (installed / name).read_bytes() == value
    assert check_start(installed, startup, '--check-rules').returncode == 0


def test_check_start_recovers_missing_input_even_when_other_needs_approval(installed, startup):
    agents, claude = installed / 'AGENTS.md', installed / 'CLAUDE.md'
    expected = agents.read_bytes()
    agents.unlink()
    claude.write_bytes(b'@AGENTS.md\n')
    result = check_start(installed, startup, CHECK_START)
    assert result.returncode == 2 and str(claude) in result.stderr
    assert str(agents) in result.stdout and 'новую сессию' in result.stdout
    assert agents.read_bytes() == expected and claude.read_bytes() == b'@AGENTS.md\n'


def test_check_start_publication_marker_blocks_repairs(installed, startup):
    (installed / '.harness-publication.json').write_bytes(b'{}')
    entry = installed / 'AGENTS.md'
    entry.unlink()
    result = check_start(installed, startup, CHECK_START)
    assert result.returncode == 2 and 'Unfinished publication' in result.stderr
    assert not entry.exists()


def test_approved_protected_repair_uses_exact_backup_and_preserves_other_staging(installed, startup):
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=installed)

    def restore(commit, *entries):
        args = ['--restore-start-entrypoints', commit]
        for name, observed, canonical in entries:
            args.extend(('--entrypoint', f'{name}:{digest(observed)}:{digest(canonical)}'))
        return startup(installed, 'harness/common/checks/ensure_entrypoint_links.py', *args, no_git=False)

    git('init', '-q')
    git('config', 'user.name', 'Harness Test')
    git('config', 'user.email', 'harness-test@example.invalid')
    git('add', 'AGENTS.md', 'CLAUDE.md')
    git('commit', '-qm', 'Published inputs')
    agents, claude = installed / 'AGENTS.md', installed / 'CLAUDE.md'
    canonical_agents = agents.read_bytes()
    unexpected_agents, unexpected_claude = b'Observed Agents\n', b'Observed Claude\n'
    agents.write_bytes(unexpected_agents)
    claude.write_bytes(unexpected_claude)
    approval_agents = ('AGENTS.md', unexpected_agents, canonical_agents)
    approval_claude = ('CLAUDE.md', unexpected_claude, b'')
    assert restore(git('rev-parse', 'HEAD').decode().strip(), approval_agents).returncode == 2
    (installed / 'other.txt').write_bytes(b'Staged unrelated data\n')
    git('add', 'other.txt')
    before = git('ls-files', '--stage', '--', 'other.txt')
    git('commit', '--only', '-qm', 'Back up observed inputs', '--', 'AGENTS.md', 'CLAUDE.md')
    backup = git('rev-parse', 'HEAD').decode().strip()

    claude.write_bytes(b'Changed after approval\n')
    result = restore(backup, approval_agents, approval_claude)
    assert result.returncode == 2 and str(claude) in result.stderr
    assert agents.read_bytes() == unexpected_agents and claude.read_bytes() == b'Changed after approval\n'
    claude.write_bytes(unexpected_claude)
    assert restore(backup, ('AGENTS.md', unexpected_agents, b'Wrong template')).returncode == 2
    assert restore(backup, approval_agents).returncode == 3
    assert claude.read_bytes() == unexpected_claude
    assert restore(backup, approval_agents, approval_claude).returncode == 3
    assert (agents.read_bytes(), claude.read_bytes()) == (canonical_agents, b'')
    assert restore(backup, approval_agents, approval_claude).returncode == 0
    assert git('ls-files', '--stage', '--', 'other.txt') == before
    assert git('show', 'HEAD:AGENTS.md') == unexpected_agents
    assert git('show', 'HEAD:CLAUDE.md') == unexpected_claude


def test_checker_does_not_change_git_config_or_install_hooks(installed, startup):
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=installed)
    git('init', '-q')
    git('config', 'user.name', 'Harness Test')
    git('config', 'user.email', 'harness-test@example.invalid')
    config = (installed / '.git/config').read_bytes()
    (installed / 'AGENTS.md').write_bytes(b'Intentional mismatch\n')
    assert startup(installed).returncode == 2
    assert config == (installed / '.git/config').read_bytes()
    assert not (installed / '.git/hooks/pre-commit').exists()
    git('add', 'AGENTS.md')
    git('commit', '-qm', 'Test commit')
    assert git('show', 'HEAD:AGENTS.md') == b'Intentional mismatch\n'


def test_atomic_repair_preserves_permissions_and_published_crlf(installed, checker, monkeypatch, capsys):
    target = installed / NATIVE
    target.write_bytes(b'Incorrect\n')
    target.chmod(0o640)
    replace = os.replace
    calls = []

    def observe(temporary, destination):
        assert NOTICE in capsys.readouterr().out
        assert destination == target and Path(temporary).parent == target.parent
        assert target.read_bytes() == b'Incorrect\n'
        calls.append(destination)
        return replace(temporary, destination)

    monkeypatch.setattr(os, 'replace', observe)
    checker.ensure(installed)
    assert calls == [target]
    assert target.stat().st_mode & 0o777 == 0o640
    assert target.read_bytes() == b'# Published rule\r\n'
    assert not list(target.parent.glob('.comm-fixture.md-*'))


def test_concurrent_edit_before_replace_survives(installed, checker, monkeypatch):
    target = installed / NATIVE
    target.write_bytes(b'Damaged')
    write = checker.replace_input

    def concurrent(path, *args):
        path.write_bytes(b'Concurrent')
        return write(path, *args)

    monkeypatch.setattr(checker, 'replace_input', concurrent)
    with pytest.raises(ValueError, match='changed'):
        checker.ensure(installed)
    assert target.read_bytes() == b'Concurrent'


def test_concurrent_creation_after_first_update_reports_partial_operation(installed, checker, monkeypatch):
    rule = installed / NATIVE
    rule.write_bytes(b'Damaged')
    entry = installed / 'CLAUDE.md'
    entry.unlink()
    write = checker.replace_input

    def concurrent(path, *args):
        result = write(path, *args)
        if path == rule:
            entry.write_bytes(b'Concurrent bridge\n')
        return result

    monkeypatch.setattr(checker, 'replace_input', concurrent)
    with pytest.raises(ValueError) as error:
        checker.ensure(installed)
    completed, pending = str(error.value).split('already updated: ', 1)[1].split('; pending: ', 1)
    assert str(rule) in completed and str(entry) in pending
    assert rule.read_bytes() == b'# Published rule\r\n'
    assert entry.read_bytes() == b'Concurrent bridge\n'


@pytest.mark.parametrize('failure', ['create', 'replace', 'write'])
def test_io_failure_preserves_file_and_cleans_temp(installed, checker, monkeypatch, failure):
    target = installed / NATIVE
    target.write_bytes(b'Original')
    def fail(*args, **kwargs):
        raise OSError('injected I/O failure')
    if failure == 'replace':
        monkeypatch.setattr(os, 'replace', fail)
    elif failure == 'create':
        monkeypatch.setattr(checker.tempfile, 'NamedTemporaryFile', fail)
    else:
        create = checker.tempfile.NamedTemporaryFile
        class BrokenWriter:
            def __init__(self, *args, **kwargs):
                self.file = create(*args, **kwargs)
                self.name = self.file.name
            def __enter__(self):
                return self
            def __exit__(self, *args):
                self.file.close()
            def write(self, data):
                self.file.write(data[:2])
                raise OSError('injected I/O failure')
        monkeypatch.setattr(checker.tempfile, 'NamedTemporaryFile', BrokenWriter)
    with pytest.raises((OSError, ValueError), match='injected I/O failure'):
        checker.ensure(installed)
    assert target.read_bytes() == b'Original'
    assert not list(target.parent.glob('.comm-fixture.md-*'))


@pytest.mark.skipif(sys.platform != 'linux' or not hasattr(os, 'setxattr'), reason='Linux ACL check')
def test_repair_preserves_owner_and_extended_attributes(installed, checker):
    target = installed / NATIVE
    target.write_bytes(b'Damaged')
    os.setxattr(target, 'user.harness-test', b'preserve')
    acl = [(1, 6, 0xffffffff), (2, 4, os.getuid()), (4, 0, 0xffffffff),
           (16, 4, 0xffffffff), (32, 0, 0xffffffff)]
    os.setxattr(target, 'system.posix_acl_access', struct.pack('<I', 2) + b''.join(
        struct.pack('<HHI', *row) for row in acl))
    before = {name: os.getxattr(target, name) for name in os.listxattr(target)}
    original = target.stat()
    checker.ensure(installed)
    after = target.stat()
    assert (after.st_uid, after.st_gid, after.st_mode) == (original.st_uid, original.st_gid, original.st_mode)
    assert before == {name: os.getxattr(target, name) for name in os.listxattr(target)}


def test_skeleton_creation_is_announced_before_writes(published, checker, monkeypatch, capsys):
    create = checker.create_project_skeleton
    def inspect(project, categories):
        assert NOTICE in capsys.readouterr().out
        assert not project.exists()
        return create(project, categories)
    monkeypatch.setattr(checker, 'create_project_skeleton', inspect)
    assert published / 'harness/project' in checker.ensure(published)
