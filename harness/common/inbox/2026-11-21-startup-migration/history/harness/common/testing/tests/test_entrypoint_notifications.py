"""Notification checks use temporary projects and need no configured hooks."""
import contextlib
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import pytest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / 'checks/ensure_entrypoint_links.py'
POLICY = 'технически не заблокировано'
NOTICE = 'Стартовые ссылки повреждены и будут автоматически восстановлены.'
RULES_LINES = ('- [.claude/rules](.claude/rules/)\n'
               'До выполнения задачи прочитай все Markdown-правила из .claude/rules '
               'и его подпапок, кроме README.human.md; соблюдай применимые требования.\n')


class TestNotification:

    @pytest.fixture(autouse=True)
    def _project(self, tmp_path):
        self.root = tmp_path
        for folder in ('harness/common/rules', '.claude/rules'):
            rules = self.root / folder
            rules.mkdir(parents=True)
            (rules / 'comm-fixture.md').write_bytes(b'# Rule fixture\n')
        for package in ('common', 'project'):
            directory = self.root / 'harness' / package
            directory.mkdir(parents=True, exist_ok=True)
            (directory / 'INDEX.md').write_text('# Index\n')
            (directory / 'START.md').write_bytes(b'# Start\n')
        template = self.root / 'harness/common/base/project-skeleton.json'
        template.parent.mkdir()
        shutil.copyfile(SCRIPT.parent.parent / 'base/project-skeleton.json', template)
        (self.root / 'AGENTS.md').write_text('# Static settings\n\nKeep this setting.\n\n' + ''.join(f'- [harness/{p}/START.md](harness/{p}/START.md)\n' for p in ('common', 'project')) + RULES_LINES + ''.join(f'- [harness/{p}/INDEX.md](harness/{p}/INDEX.md)\n' for p in ('common', 'project')))
        (self.root / 'CLAUDE.md').write_text('@AGENTS.md\n')

    def check(self, git_available=True):
        environment = dict(os.environ)
        if not git_available:
            environment['PATH'] = '/nonexistent-for-this-test'
        return subprocess.run([sys.executable, '-B', str(SCRIPT), str(self.root)], capture_output=True, text=True, env=environment)

    def git(self, *args):
        result = subprocess.run(['git', *args], cwd=self.root, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        return result

    def register_fixture(self):
        self.git('init', '-q')
        self.git('config', 'user.name', 'Harness Test')
        self.git('config', 'user.email', 'harness-test@example.invalid')
        self.git('add', 'AGENTS.md', 'CLAUDE.md')
        self.git('commit', '-qm', 'Initial test fixture')

    def test_no_git_binary_or_repository_or_baseline_is_required(self):
        before = ((self.root / 'AGENTS.md').read_bytes(), (self.root / 'CLAUDE.md').read_bytes())
        result = self.check(git_available=False)
        assert result.returncode == 0, result.stderr
        assert POLICY in result.stdout
        assert before == ((self.root / 'AGENTS.md').read_bytes(), (self.root / 'CLAUDE.md').read_bytes())

    def test_instruction_change_is_reported_and_preserved_without_blocking(self):
        self.register_fixture()
        agents = self.root / 'AGENTS.md'
        changed = agents.read_text().replace('Keep this setting.', 'Changed setting.')
        agents.write_text(changed)
        result = self.check()
        assert result.returncode == 0, result.stderr
        assert POLICY in result.stdout
        assert 'AGENTS.md' in result.stdout
        assert 'inbox' in result.stdout
        assert 'изменение настроек' in result.stdout
        assert agents.read_text() == changed

    def test_rules_instruction_added_inside_fence_is_reported_as_a_settings_change(self):
        agents = self.root / 'AGENTS.md'
        original = agents.read_text() + '\n~~~md\n~~~example\n~~~\n'
        agents.write_text(original)
        self.register_fixture()
        instruction = RULES_LINES.splitlines(keepends=True)[1]
        changed = original.replace('~~~example\n', '~~~example\n' + instruction)
        agents.write_text(changed)
        result = self.check()
        assert result.returncode == 0, result.stderr
        assert 'изменение настроек' in result.stdout
        assert NOTICE not in result.stdout
        assert agents.read_text() == changed

    def test_unclosed_historical_fence_does_not_block_repair_of_valid_current_file(self):
        agents = self.root / 'AGENTS.md'
        original = '# Keep user settings\n~~~md\nexample\n'
        agents.write_text(original)
        self.register_fixture()
        current = original + '~~~\n'
        agents.write_text(current)
        result = self.check()
        assert result.returncode == 0, result.stderr
        assert 'изменение настроек' in result.stdout
        assert NOTICE in result.stdout
        repaired = agents.read_text()
        assert repaired.startswith(current)
        assert '](harness/common/START.md)' in repaired[len(current):]
        before = agents.read_bytes()
        assert self.check().returncode == 0
        assert agents.read_bytes() == before

    def test_extra_bridge_text_warns_without_rewriting_or_blocking(self):
        self.register_fixture()
        bridge = self.root / 'CLAUDE.md'
        extra = '@AGENTS.md\nUser text\n'
        bridge.write_text(extra)
        result = self.check()
        assert result.returncode == 0, result.stderr
        assert 'CLAUDE.md' in result.stdout
        assert 'inbox' in result.stdout
        assert POLICY in result.stdout
        assert bridge.read_text() == extra

    def test_repair_is_announced_and_next_run_has_no_damage_message(self):
        agents = self.root / 'AGENTS.md'
        line = '- [harness/common/START.md](harness/common/START.md)\n'
        agents.write_text(agents.read_text().replace(line, ''))
        first = self.check(git_available=False)
        assert first.returncode == 0, first.stderr
        assert NOTICE in first.stdout
        assert line in agents.read_text()
        assert NOTICE not in self.check(git_available=False).stdout

    def test_repair_message_is_visible_before_the_first_write(self, monkeypatch):
        agents = self.root / 'AGENTS.md'
        line = '- [harness/common/START.md](harness/common/START.md)\n'
        agents.write_text(agents.read_text().replace(line, ''))
        spec = importlib.util.spec_from_file_location('entrypoint_notifications', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        output = io.StringIO()
        original_replace = os.replace
        replacements = []

        def replace(source, destination):
            assert NOTICE in output.getvalue()
            replacements.append(destination)
            return original_replace(source, destination)
        with monkeypatch.context() as scoped:
            scoped.setattr(os, 'replace', replace)
            with contextlib.redirect_stdout(output):
                module.ensure(self.root)
        assert output.getvalue().count(NOTICE) == 1
        assert replacements == [agents]

    def test_rules_repair_is_not_reported_as_a_settings_change(self):
        agents = self.root / 'AGENTS.md'
        agents.write_text(agents.read_text().replace(RULES_LINES, ''))
        self.register_fixture()
        first = self.check()
        assert first.returncode == 0, first.stderr
        assert NOTICE in first.stdout
        second = self.check()
        assert NOTICE not in second.stdout
        assert 'изменение настроек' not in second.stdout

    def test_check_installs_no_hooks_or_configuration_and_does_not_block_commit(self):
        self.register_fixture()
        config = (self.root / '.git/config').read_bytes()
        agents = self.root / 'AGENTS.md'
        agents.write_text(agents.read_text() + '\nDirect edit.\n')
        assert self.check().returncode == 0
        assert (self.root / '.git/config').read_bytes() == config
        assert not (self.root / '.git/hooks/pre-commit').exists()
        self.git('add', 'AGENTS.md')
        before = self.git('rev-parse', 'HEAD').stdout
        self.git('commit', '-qm', 'Commit is not mechanically blocked')
        assert self.git('rev-parse', 'HEAD').stdout != before

    def test_crlf_link_repair_is_not_reported_as_a_settings_change(self):
        agents = self.root / 'AGENTS.md'
        original = agents.read_bytes().replace(b'\n', b'\r\n')
        line = b'- [harness/common/START.md](harness/common/START.md)\r\n'
        original = original.replace(line, b'')
        agents.write_bytes(original)
        self.register_fixture()
        first = self.check()
        assert first.returncode == 0, first.stderr
        assert NOTICE in first.stdout
        repaired = agents.read_bytes()
        assert repaired.startswith(b'# Static settings\r\n\r\nKeep this setting.\r\n\r\n')
        assert b'\n' not in repaired.replace(b'\r\n', b'')
        assert line in agents.read_bytes()
        second = self.check()
        assert second.returncode == 0, second.stderr
        assert NOTICE not in second.stdout
        assert 'изменение настроек' not in second.stdout

    def load_checker(self):
        spec = importlib.util.spec_from_file_location('entrypoint_atomic_checks', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def damage_agents(self):
        agents = self.root / 'AGENTS.md'
        agents.write_bytes(agents.read_bytes().replace(
            b'- [harness/common/START.md](harness/common/START.md)\n', b''))
        return agents

    def test_atomic_repair_preserves_permissions_and_crlf(self, monkeypatch):
        agents = self.damage_agents()
        original = agents.read_bytes().replace(b'\n', b'\r\n')
        agents.write_bytes(original)
        agents.chmod(0o640)
        module = self.load_checker()
        replacements = []
        original_replace = os.replace

        def replace(source, destination):
            assert Path(destination).read_bytes() == original
            assert Path(source).parent == agents.parent
            replacements.append(destination)
            return original_replace(source, destination)
        monkeypatch.setattr(os, 'replace', replace)
        module.ensure(self.root)
        assert replacements == [agents]
        assert agents.stat().st_mode & 0o777 == 0o640
        assert b'\n' not in agents.read_bytes().replace(b'\r\n', b'')
        assert not list(self.root.glob('.AGENTS.md-*'))

    def test_parallel_edit_during_planning_is_preserved(self, monkeypatch):
        agents = self.damage_agents()
        module = self.load_checker()
        repair = module.repair_startup_blocks

        def changed(*args):
            result = repair(*args)
            agents.write_bytes(b'# Concurrent edit\n')
            return result
        monkeypatch.setattr(module, 'repair_startup_blocks', changed)
        with pytest.raises(ValueError, match='changed'):
            module.ensure(self.root)
        assert agents.read_bytes() == b'# Concurrent edit\n'

    def test_concurrent_bridge_edit_after_first_replace_reports_partial_result(self, monkeypatch):
        agents = self.damage_agents()
        bridge = self.root / 'CLAUDE.md'
        bridge.write_bytes(b'User bridge\n')
        module = self.load_checker()
        replace = os.replace

        def changed(source, destination):
            result = replace(source, destination)
            if Path(destination) == agents:
                bridge.write_bytes(b'Concurrent bridge\n')
            return result
        monkeypatch.setattr(os, 'replace', changed)
        with pytest.raises(ValueError, match='AGENTS.md') as error:
            module.ensure(self.root)
        assert 'CLAUDE.md' in str(error.value)
        assert bridge.read_bytes() == b'Concurrent bridge\n'
        assert b'](harness/common/START.md)' in agents.read_bytes()
        assert not list(self.root.glob('.CLAUDE.md-*'))

    @pytest.mark.parametrize('failure', ('create', 'replace', 'write'))
    def test_atomic_io_failure_preserves_original_and_removes_temporary_file(self, monkeypatch, failure):
        agents = self.damage_agents()
        original = agents.read_bytes()
        module = self.load_checker()

        def fail(*args, **kwargs):
            raise OSError('injected I/O failure')
        if failure == 'replace':
            monkeypatch.setattr(os, 'replace', fail)
        elif failure == 'create':
            monkeypatch.setattr(module.tempfile, 'NamedTemporaryFile', fail)
        else:
            create = module.tempfile.NamedTemporaryFile

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
            monkeypatch.setattr(module.tempfile, 'NamedTemporaryFile', BrokenWriter)
        with pytest.raises((OSError, ValueError), match='injected I/O failure'):
            module.ensure(self.root)
        assert agents.read_bytes() == original
        assert not list(self.root.glob('.AGENTS.md-*'))

    @pytest.mark.skipif(sys.platform != 'linux' or not hasattr(os, 'setxattr'), reason='Linux extended-attribute/ACL check requires Linux APIs')
    def test_atomic_repair_preserves_extended_attributes_and_acl(self):
        import struct
        agents = self.damage_agents()
        os.setxattr(agents, 'user.harness-test', b'preserve metadata')
        # Use the mapped UID so this ACL is valid inside a single-user namespace.
        acl = struct.pack('<I', 2) + b''.join(struct.pack('<HHI', tag, permission, uid)
            for tag, permission, uid in ((1, 6, 0xffffffff), (2, 4, os.getuid()),
                                         (4, 0, 0xffffffff), (16, 4, 0xffffffff), (32, 0, 0xffffffff)))
        os.setxattr(agents, 'system.posix_acl_access', acl)
        before = {name: os.getxattr(agents, name) for name in os.listxattr(agents)}
        original = agents.stat()
        self.load_checker().ensure(self.root)
        after = agents.stat()
        assert (after.st_uid, after.st_gid, after.st_mode) == (original.st_uid, original.st_gid, original.st_mode)
        assert before == {name: os.getxattr(agents, name) for name in os.listxattr(agents)}
