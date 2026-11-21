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
