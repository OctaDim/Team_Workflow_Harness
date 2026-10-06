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

SCRIPT = Path(__file__).with_name('ensure_entrypoint_links.py')
POLICY = 'технически не заблокировано'
NOTICE = 'Стартовые ссылки повреждены и будут автоматически восстановлены.'
RULES_LINES = ('- [.claude/rules](.claude/rules/)\n'
               'До выполнения задачи прочитай все Markdown-правила из .claude/rules '
               'и его подпапок, кроме README.human.md; соблюдай применимые требования.\n')


class TestNotification:

    @pytest.fixture(autouse=True)
    def _project(self, tmp_path):
        self.root = tmp_path
        for package in ('common', 'project'):
            directory = self.root / 'harness' / package
            directory.mkdir(parents=True)
            (directory / 'INDEX.md').write_text('# Index\n')
            (directory / 'START.md').touch()
        template = self.root / 'harness/common/base/project-skeleton.json'
        template.parent.mkdir()
        shutil.copyfile(SCRIPT.parent.parent / 'base/project-skeleton.json', template)
        (self.root / 'AGENTS.md').write_text('# Static settings\n\nKeep this setting.\n\n' + ''.join((f'- [harness/{p}/{n}](harness/{p}/{n})\n' for p in ('common', 'project') for n in ('INDEX.md', 'START.md'))) + RULES_LINES)
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
        original_write = Path.write_bytes

        def write(path, data, *args, **kwargs):
            assert NOTICE in output.getvalue()
            return original_write(path, data, *args, **kwargs)
        with monkeypatch.context() as scoped:
            scoped.setattr(Path, 'write_bytes', write)
            with contextlib.redirect_stdout(output):
                module.ensure(self.root)
        assert output.getvalue().count(NOTICE) == 1

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
        assert agents.read_bytes().startswith(original)
        assert line in agents.read_bytes()
        second = self.check()
        assert second.returncode == 0, second.stderr
        assert NOTICE not in second.stdout
        assert 'изменение настроек' not in second.stdout
