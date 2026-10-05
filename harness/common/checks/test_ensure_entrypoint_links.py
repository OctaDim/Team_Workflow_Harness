"""Run with python3 -B <this-file>; uses only temporary projects."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name('ensure_entrypoint_links.py')


class EntryPointLinksTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for package in ('common', 'project'):
            directory = self.root / 'harness' / package
            directory.mkdir(parents=True)
            (directory / 'INDEX.md').write_text('# Index\n')
            (directory / 'START.md').touch()

    def run_check(self):
        return subprocess.run([sys.executable, '-B', str(SCRIPT), str(self.root)],
                              text=True, capture_output=True)

    def test_creates_four_links_and_import_then_preserves_bytes(self):
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)
        agents = self.root / 'AGENTS.md'
        claude = self.root / 'CLAUDE.md'
        for package in ('common', 'project'):
            for name in ('INDEX.md', 'START.md'):
                self.assertIn(f'](harness/{package}/{name})', agents.read_text())
        self.assertEqual(claude.read_bytes(), b'@AGENTS.md\n')
        before = (agents.read_bytes(), claude.read_bytes())
        self.assertEqual(self.run_check().returncode, 0)
        self.assertEqual(before, (agents.read_bytes(), claude.read_bytes()))
        for file in self.root.glob('harness/*/START.md'):
            self.assertEqual(file.read_bytes(), b'')

    def test_only_appends_missing_links_preserving_user_text(self):
        prefix = '# User configuration\n\nKeep this exact text.\n[Existing](./harness/common/INDEX.md)\n'
        (self.root / 'AGENTS.md').write_text(prefix)
        self.assertEqual(self.run_check().returncode, 0)
        text = (self.root / 'AGENTS.md').read_text()
        self.assertTrue(text.startswith(prefix))
        self.assertEqual(text.count('harness/common/INDEX.md'), 1)

    def test_link_examples_in_code_do_not_count_as_real_links(self):
        examples = '\n'.join(f'[Example](harness/{p}/{n})'
                             for p in ('common', 'project') for n in ('INDEX.md', 'START.md'))
        (self.root / 'AGENTS.md').write_text(f'```md\n{examples}\n```\n')
        self.assertEqual(self.run_check().returncode, 0)
        text = (self.root / 'AGENTS.md').read_text()
        self.assertEqual(text.count('](harness/common/INDEX.md)'), 2)

    def test_damaged_package_is_reported_without_creating_dangling_links(self):
        (self.root / 'harness/project/START.md').unlink()
        result = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / 'AGENTS.md').exists())
        self.assertFalse((self.root / 'CLAUDE.md').exists())

    def test_common_only_does_not_require_project(self):
        import shutil
        shutil.rmtree(self.root / 'harness/project')
        self.assertEqual(self.run_check().returncode, 0)
        self.assertNotIn('harness/project/', (self.root / 'AGENTS.md').read_text())

    def test_adds_import_and_warns_about_extra_claude_content_without_deleting_it(self):
        (self.root / 'CLAUDE.md').write_text('User text\n')
        result = self.run_check()
        self.assertEqual(result.returncode, 0)
        self.assertIn('inbox', result.stdout)
        self.assertIn('технически не заблокировано', result.stdout)
        self.assertEqual((self.root / 'CLAUDE.md').read_text(), '@AGENTS.md\nUser text\n')

    def test_refuses_symlinked_entrypoint_without_changing_target(self):
        target = self.root / 'user.md'
        target.write_text('User text\n')
        (self.root / 'AGENTS.md').symlink_to(target)
        self.assertNotEqual(self.run_check().returncode, 0)
        self.assertEqual(target.read_text(), 'User text\n')


if __name__ == '__main__':
    unittest.main()
