"""Exercise real Git indexes, temporary projects, and the commit hook."""
import contextlib
import importlib.util
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name('ensure_entrypoint_links.py')
NOTICE = 'Стартовые ссылки повреждены и будут автоматически восстановлены.'


class ProtectionTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for package in ('common', 'project'):
            directory = self.root / 'harness' / package
            directory.mkdir(parents=True)
            (directory / 'INDEX.md').write_text('# Index\n')
            (directory / 'START.md').touch()
        (self.root / 'AGENTS.md').write_text('# Static settings\n\nDo not change this instruction.\n\n' + ''.join(
            f'- [harness/{p}/{n}](harness/{p}/{n})\n'
            for p in ('common', 'project') for n in ('INDEX.md', 'START.md')))
        (self.root / 'CLAUDE.md').write_text('@AGENTS.md\n')
        self.git('init', '-q')
        self.git('config', 'user.name', 'Harness Test')
        self.git('config', 'user.email', 'harness-test@example.invalid')
        self.git('add', 'AGENTS.md', 'CLAUDE.md')
        self.git('-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'Approved initial configuration')

    def git(self, *args):
        result = subprocess.run(['git', *args], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def check(self, *args):
        return subprocess.run([sys.executable, '-B', str(SCRIPT), *args, str(self.root)],
                              capture_output=True, text=True)

    def test_notice_precedes_repair_and_is_not_repeated(self):
        agents = self.root / 'AGENTS.md'
        line = '- [harness/common/START.md](harness/common/START.md)\n'
        agents.write_text(agents.read_text().replace(line, ''))
        spec = importlib.util.spec_from_file_location('entrypoints', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        output = io.StringIO()
        original_write = Path.write_text
        def write(path, text, *args, **kwargs):
            self.assertIn(NOTICE, output.getvalue())
            return original_write(path, text, *args, **kwargs)
        from unittest.mock import patch
        with contextlib.redirect_stdout(output), patch.object(Path, 'write_text', write):
            module.ensure(self.root)
        self.assertEqual(output.getvalue().count(NOTICE), 1)
        self.assertNotIn(NOTICE, self.check().stdout)

    def test_working_copy_instruction_edit_warns_and_preserves_edit(self):
        agents = self.root / 'AGENTS.md'
        edited = agents.read_text().replace('Do not change this instruction.', 'Changed instruction.')
        agents.write_text(edited)
        result = self.check('--check-protected')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('inbox', result.stderr)
        self.assertIn('AGENTS.md', result.stderr)
        self.assertEqual(agents.read_text(), edited)

    def test_staged_edit_is_blocked_even_if_working_file_is_restored(self):
        original = (self.root / 'AGENTS.md').read_text()
        (self.root / 'AGENTS.md').write_text(original + '\nNew requirement.\n')
        self.git('add', 'AGENTS.md')
        (self.root / 'AGENTS.md').write_text(original)
        result = self.check('--check-protected', '--staged')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('inbox', result.stderr)

    def test_exact_bridge_replacement_and_deletion_are_blocked(self):
        bridge = self.root / 'CLAUDE.md'
        bridge.write_text('@./AGENTS.md\n')
        result = self.check('--check-protected')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('CLAUDE.md', result.stderr)
        bridge.unlink()
        self.assertNotEqual(self.check('--check-protected').returncode, 0)

    def test_unchanged_files_and_unrelated_changes_are_allowed(self):
        (self.root / 'feature.txt').write_text('Feature\n')
        self.git('add', 'feature.txt')
        self.assertEqual(self.check('--check-protected').returncode, 0)
        self.assertEqual(self.check('--check-protected', '--staged').returncode, 0)

    def test_repair_is_allowed_but_missing_links_are_not(self):
        agents = self.root / 'AGENTS.md'
        agents.write_text(agents.read_text().replace(
            '- [harness/common/INDEX.md](harness/common/INDEX.md)\n', ''))
        self.assertNotEqual(self.check('--check-protected').returncode, 0)
        self.assertEqual(self.check().returncode, 0)
        self.git('add', 'AGENTS.md')
        self.assertEqual(self.check('--check-protected', '--staged').returncode, 0)

    def test_restoring_links_does_not_hide_an_instruction_edit(self):
        agents = self.root / 'AGENTS.md'
        agents.write_text(agents.read_text().replace('Do not change this instruction.', 'Changed.').replace(
            '- [harness/common/INDEX.md](harness/common/INDEX.md)\n', ''))
        self.assertNotEqual(self.check().returncode, 0)
        result = self.check('--check-protected')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('inbox', result.stderr)

    def test_git_hook_rejects_real_commit_and_allows_unrelated_commit(self):
        hook_source = SCRIPT.with_name('pre-commit')
        installed = self.root / 'harness/common/checks'
        installed.mkdir(parents=True)
        shutil.copy2(SCRIPT, installed / SCRIPT.name)
        hook = self.root / '.git/hooks/pre-commit'
        if hook_source.exists():
            shutil.copy2(hook_source, hook)
        else:
            hook.write_text('#!/bin/sh\nexit 0\n')
        hook.chmod(0o755)
        (self.root / 'feature.txt').write_text('Feature\n')
        self.git('add', 'feature.txt')
        result = subprocess.run(['git', 'commit', '-qm', 'Unrelated change'], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        (self.root / 'AGENTS.md').write_text('Changed instruction.\n')
        self.git('add', 'AGENTS.md')
        before = self.git('rev-parse', 'HEAD').stdout
        result = subprocess.run(['git', 'commit', '-qm', 'Forbidden direct edit'], cwd=self.root, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('inbox', result.stderr)
        self.assertEqual(self.git('rev-parse', 'HEAD').stdout, before)

    def test_missing_baseline_fails_with_actionable_warning(self):
        self.git('rm', 'CLAUDE.md')
        self.git('-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'Fixture without approved bridge')
        result = self.check('--check-protected')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('inbox', result.stderr)


if __name__ == '__main__':
    unittest.main()
