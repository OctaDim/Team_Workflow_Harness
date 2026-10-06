"""Notification checks use temporary projects and need no configured hooks."""
import contextlib
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name('ensure_entrypoint_links.py')
POLICY = 'технически не заблокировано'
NOTICE = 'Стартовые ссылки повреждены и будут автоматически восстановлены.'
RULES_LINES = ('- [.claude/rules](.claude/rules/)\n'
               'До выполнения задачи прочитай все Markdown-правила из .claude/rules '
               'и его подпапок, кроме README.human.md; соблюдай применимые требования.\n')


class NotificationTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for package in ('common', 'project'):
            directory = self.root / 'harness' / package
            directory.mkdir(parents=True)
            (directory / 'INDEX.md').write_text('# Index\n')
            (directory / 'START.md').touch()
        (self.root / 'AGENTS.md').write_text('# Static settings\n\nKeep this setting.\n\n' + ''.join(
            f'- [harness/{p}/{n}](harness/{p}/{n})\n'
            for p in ('common', 'project') for n in ('INDEX.md', 'START.md')) + RULES_LINES)
        (self.root / 'CLAUDE.md').write_text('@AGENTS.md\n')

    def check(self, git_available=True):
        environment = dict(os.environ)
        if not git_available:
            environment['PATH'] = '/nonexistent-for-this-test'
        return subprocess.run([sys.executable, '-B', str(SCRIPT), str(self.root)],
                              capture_output=True, text=True, env=environment)

    def git(self, *args):
        result = subprocess.run(['git', *args], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def register_fixture(self):
        self.git('init', '-q')
        self.git('config', 'user.name', 'Harness Test')
        self.git('config', 'user.email', 'harness-test@example.invalid')
        self.git('add', 'AGENTS.md', 'CLAUDE.md')
        self.git('commit', '-qm', 'Initial test fixture')

    def test_no_git_binary_or_repository_or_baseline_is_required(self):
        before = (self.root/'AGENTS.md').read_bytes(), (self.root/'CLAUDE.md').read_bytes()
        result = self.check(git_available=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(POLICY, result.stdout)
        self.assertEqual(before, ((self.root/'AGENTS.md').read_bytes(), (self.root/'CLAUDE.md').read_bytes()))

    def test_instruction_change_is_reported_and_preserved_without_blocking(self):
        self.register_fixture()
        agents = self.root/'AGENTS.md'
        changed = agents.read_text().replace('Keep this setting.', 'Changed setting.')
        agents.write_text(changed)
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(POLICY, result.stdout)
        self.assertIn('AGENTS.md', result.stdout)
        self.assertIn('inbox', result.stdout)
        self.assertIn('изменение настроек', result.stdout)
        self.assertEqual(agents.read_text(), changed)

    def test_rules_instruction_added_inside_fence_is_reported_as_a_settings_change(self):
        agents = self.root / 'AGENTS.md'
        original = agents.read_text() + '\n~~~md\n~~~example\n~~~\n'
        agents.write_text(original)
        self.register_fixture()
        instruction = RULES_LINES.splitlines(keepends=True)[1]
        changed = original.replace('~~~example\n', '~~~example\n' + instruction)
        agents.write_text(changed)
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('изменение настроек', result.stdout)
        self.assertNotIn(NOTICE, result.stdout)
        self.assertEqual(agents.read_text(), changed)

    def test_unclosed_historical_fence_does_not_block_repair_of_valid_current_file(self):
        agents = self.root / 'AGENTS.md'
        original = '# Keep user settings\n~~~md\nexample\n'
        agents.write_text(original)
        self.register_fixture()
        current = original + '~~~\n'
        agents.write_text(current)
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('изменение настроек', result.stdout)
        self.assertIn(NOTICE, result.stdout)
        repaired = agents.read_text()
        self.assertTrue(repaired.startswith(current))
        self.assertIn('](harness/common/START.md)', repaired[len(current):])
        before = agents.read_bytes()
        self.assertEqual(self.check().returncode, 0)
        self.assertEqual(agents.read_bytes(), before)

    def test_extra_bridge_text_warns_without_rewriting_or_blocking(self):
        self.register_fixture()
        bridge=self.root/'CLAUDE.md'
        extra='@AGENTS.md\nUser text\n'
        bridge.write_text(extra)
        result=self.check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('CLAUDE.md', result.stdout)
        self.assertIn('inbox', result.stdout)
        self.assertIn(POLICY, result.stdout)
        self.assertEqual(bridge.read_text(), extra)

    def test_repair_is_announced_and_next_run_has_no_damage_message(self):
        agents=self.root/'AGENTS.md'
        line='- [harness/common/START.md](harness/common/START.md)\n'
        agents.write_text(agents.read_text().replace(line,''))
        first=self.check(git_available=False)
        self.assertEqual(first.returncode,0,first.stderr)
        self.assertIn(NOTICE,first.stdout)
        self.assertIn(line,agents.read_text())
        self.assertNotIn(NOTICE,self.check(git_available=False).stdout)

    def test_repair_message_is_visible_before_the_first_write(self):
        agents = self.root/'AGENTS.md'
        line = '- [harness/common/START.md](harness/common/START.md)\n'
        agents.write_text(agents.read_text().replace(line, ''))
        spec = importlib.util.spec_from_file_location('entrypoint_notifications', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        output = io.StringIO()
        original_write = Path.write_bytes
        def write(path, data, *args, **kwargs):
            self.assertIn(NOTICE, output.getvalue())
            return original_write(path, data, *args, **kwargs)
        from unittest.mock import patch
        with contextlib.redirect_stdout(output), patch.object(Path, 'write_bytes', write):
            module.ensure(self.root)
        self.assertEqual(output.getvalue().count(NOTICE), 1)

    def test_rules_repair_is_not_reported_as_a_settings_change(self):
        agents = self.root / 'AGENTS.md'
        agents.write_text(agents.read_text().replace(RULES_LINES, ''))
        self.register_fixture()
        first = self.check()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn(NOTICE, first.stdout)
        second = self.check()
        self.assertNotIn(NOTICE, second.stdout)
        self.assertNotIn('изменение настроек', second.stdout)

    def test_check_installs_no_hooks_or_configuration_and_does_not_block_commit(self):
        self.register_fixture()
        config=(self.root/'.git/config').read_bytes()
        agents=self.root/'AGENTS.md'
        agents.write_text(agents.read_text()+'\nDirect edit.\n')
        self.assertEqual(self.check().returncode,0)
        self.assertEqual((self.root/'.git/config').read_bytes(),config)
        self.assertFalse((self.root/'.git/hooks/pre-commit').exists())
        self.git('add','AGENTS.md')
        before=self.git('rev-parse','HEAD').stdout
        self.git('commit','-qm','Commit is not mechanically blocked')
        self.assertNotEqual(self.git('rev-parse','HEAD').stdout,before)

    def test_crlf_link_repair_is_not_reported_as_a_settings_change(self):
        agents = self.root / 'AGENTS.md'
        original = agents.read_bytes().replace(b'\n', b'\r\n')
        line = b'- [harness/common/START.md](harness/common/START.md)\r\n'
        original = original.replace(line, b'')
        agents.write_bytes(original)
        self.register_fixture()
        first = self.check()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn(NOTICE, first.stdout)
        self.assertTrue(agents.read_bytes().startswith(original))
        self.assertIn(line, agents.read_bytes())
        second = self.check()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertNotIn(NOTICE, second.stdout)
        self.assertNotIn('изменение настроек', second.stdout)


if __name__=='__main__':
    unittest.main()
