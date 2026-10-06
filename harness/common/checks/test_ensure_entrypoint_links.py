"""Run with python3 -B <this-file>; uses only temporary projects."""
import json
import shutil
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
        template = SCRIPT.parent.parent / 'base/project-skeleton.json'
        if template.exists():
            destination = self.root / 'harness/common/base/project-skeleton.json'
            destination.parent.mkdir()
            shutil.copyfile(template, destination)

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

    def test_repair_preserves_original_bytes_and_each_files_line_endings(self):
        agents, claude = self.root / 'AGENTS.md', self.root / 'CLAUDE.md'
        for newline in (b'\n', b'\r\n'):
            with self.subTest(newline=newline):
                original = newline.join((b'# User settings', b'Keep exact bytes.', b'', b''))
                bridge = b'User bridge text\r\n'
                agents.write_bytes(original)
                claude.write_bytes(bridge)
                result = self.run_check()
                self.assertEqual(result.returncode, 0, result.stderr)
                repaired = agents.read_bytes()
                self.assertTrue(repaired.startswith(original))
                self.assertIn(b'](harness/common/START.md)' + newline, repaired)
                if newline == b'\r\n':
                    self.assertNotIn(b'\n', repaired.replace(b'\r\n', b''))
                self.assertEqual(claude.read_bytes(), b'@AGENTS.md\r\n' + bridge)
                before = agents.read_bytes(), claude.read_bytes()
                second = self.run_check()
                self.assertEqual(second.returncode, 0, second.stderr)
                self.assertNotIn('будут автоматически восстановлены', second.stdout)
                self.assertEqual((agents.read_bytes(), claude.read_bytes()), before)

    def test_valid_crlf_bridge_is_preserved_without_warning_or_repair(self):
        self.assertEqual(self.run_check().returncode, 0)
        agents, claude = self.root / 'AGENTS.md', self.root / 'CLAUDE.md'
        agents.write_bytes(agents.read_bytes().replace(b'\n', b'\r\n'))
        claude.write_bytes(b'@AGENTS.md\r\n')
        before = agents.read_bytes(), claude.read_bytes()
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('будут автоматически восстановлены', result.stdout)
        self.assertNotIn('требуется единственная строка', result.stdout)
        self.assertEqual((agents.read_bytes(), claude.read_bytes()), before)

    def test_longer_fence_closers_do_not_turn_examples_into_installed_links(self):
        examples = '\n'.join(f'[Example](harness/{p}/{n})'
                             for p in ('common', 'project') for n in ('INDEX.md', 'START.md'))
        examples += ('\n[Rules](.claude/rules/)\n'
                     'До выполнения задачи прочитай все Markdown-правила из .claude/rules '
                     'и его подпапок, кроме README.human.md; соблюдай применимые требования.')
        agents = self.root / 'AGENTS.md'
        for opener, closer in (('~~~md', '~~~~'), ('```md', '````')):
            with self.subTest(opener=opener):
                prefix = f'# Keep user settings\n{opener}\n{examples}\n{closer}\n'
                agents.write_text(prefix)
                first = self.run_check()
                self.assertEqual(first.returncode, 0, first.stderr)
                text = agents.read_text()
                self.assertTrue(text.startswith(prefix))
                appended = text[len(prefix):]
                for package in ('common', 'project'):
                    for name in ('INDEX.md', 'START.md'):
                        self.assertIn(f'](harness/{package}/{name})', appended)
                self.assertIn('](.claude/rules/)', appended)
                self.assertIn('прочитай все Markdown-правила', appended)
                before = agents.read_bytes()
                second = self.run_check()
                self.assertEqual(second.returncode, 0, second.stderr)
                self.assertEqual(agents.read_bytes(), before)

    def test_unclosed_fence_fails_before_writing_either_entrypoint(self):
        agents, claude = self.root / 'AGENTS.md', self.root / 'CLAUDE.md'
        for name in ('AGENTS.md', 'CLAUDE.md'):
            for opener in ('~~~md', '```md'):
                with self.subTest(name=name, opener=opener):
                    agents.write_text('# Keep user settings\n')
                    claude.write_text('Keep bridge text\n')
                    (self.root / name).write_text(f'# Keep user settings\n{opener}\nexample\n')
                    before = agents.read_bytes(), claude.read_bytes()
                    result = self.run_check()
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertIn('Unclosed Markdown code fence', result.stderr)
                    self.assertEqual((agents.read_bytes(), claude.read_bytes()), before)
                    self.assertFalse((self.root / '.claude').exists())

    def test_damaged_package_is_reported_without_creating_dangling_links(self):
        (self.root / 'harness/project/START.md').unlink()
        result = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / 'AGENTS.md').exists())
        self.assertFalse((self.root / 'CLAUDE.md').exists())

    def test_common_only_creates_neutral_project(self):
        shutil.rmtree(self.root / 'harness/project')
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)
        project = self.root / 'harness/project'
        expected = {'base', 'decisions', 'lessons', 'testing', 'rules', 'skills',
                    'checks', 'inbox', 'docs', 'handoffs'}
        self.assertTrue(project.is_dir(), 'common-only must create project')
        self.assertEqual({p.name for p in project.iterdir() if p.is_dir()}, expected)
        for directory in [project, *(project / name for name in expected)]:
            self.assertTrue((directory / 'README.human.md').is_file())
        self.assertFalse((project / 'checks/ensure_entrypoint_links.py').exists())
        self.assertNotIn('EPL', (project / 'INDEX.md').read_text())
        self.assertIn('harness/common/checks/ensure_entrypoint_links.py',
                      (project / 'START.md').read_text())
        self.assertIn('harness/project/START.md', (self.root / 'AGENTS.md').read_text())
        before = {p.relative_to(project): p.stat().st_mtime_ns for p in project.rglob('*')}
        self.assertEqual(self.run_check().returncode, 0)
        self.assertEqual(before, {p.relative_to(project): p.stat().st_mtime_ns for p in project.rglob('*')})

    def test_existing_project_is_not_regenerated_or_exported(self):
        project = self.root / 'harness/project'
        task = project / 'docs/epl-import/notes.md'
        task.parent.mkdir(parents=True)
        task.write_bytes(b'project-specific material\n')
        before = {p.relative_to(project): p.read_bytes() for p in project.rglob('*') if p.is_file()}
        self.assertEqual(self.run_check().returncode, 0)
        self.assertEqual(before, {p.relative_to(project): p.read_bytes() for p in project.rglob('*') if p.is_file()})
        self.assertFalse((project / 'base').exists(), 'existing project is not filled with a new skeleton')

    def test_new_template_categories_apply_only_to_new_project(self):
        template = self.root / 'harness/common/base/project-skeleton.json'
        data = json.loads(template.read_text())
        data['categories']['specs'] = {'purpose': 'Shared specifications', 'example': 'api.md describes an agreed API.'}
        template.write_text(json.dumps(data))
        self.assertEqual(self.run_check().returncode, 0)
        self.assertFalse((self.root / 'harness/project/specs').exists())
        shutil.rmtree(self.root / 'harness/project')
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / 'harness/project/specs/README.human.md').is_file())

    def test_project_only_is_rejected_before_writes(self):
        shutil.rmtree(self.root / 'harness/common')
        result = self.run_check()
        self.assertEqual(result.returncode, 2)
        self.assertIn('common', result.stderr)
        self.assertFalse((self.root / 'AGENTS.md').exists())
        self.assertFalse((self.root / '.claude').exists())

    def test_unsafe_project_path_is_rejected_without_writes(self):
        project = self.root / 'harness/project'
        shutil.rmtree(project)
        for symlink in (False, True):
            with self.subTest(symlink=symlink):
                if symlink:
                    project.symlink_to(self.root / 'missing-project')
                else:
                    project.write_text('keep this file')
                result = self.run_check()
                self.assertEqual(result.returncode, 2)
                self.assertFalse((self.root / 'AGENTS.md').exists())
                self.assertFalse((self.root / '.claude').exists())
                project.unlink()

    def test_invalid_template_does_not_create_project(self):
        project = self.root / 'harness/project'
        shutil.rmtree(project)
        template = self.root / 'harness/common/base/project-skeleton.json'
        for content in ('not json', '{}', '{"categories": {"../outside": {"purpose": "bad", "example": "bad"}}}'):
            with self.subTest(content=content):
                template.write_text(content)
                result = self.run_check()
                self.assertEqual(result.returncode, 2)
                self.assertFalse(project.exists())
                self.assertFalse((self.root / 'AGENTS.md').exists())

    def test_invalid_entrypoint_prevents_project_creation(self):
        shutil.rmtree(self.root / 'harness/project')
        agents = self.root / 'AGENTS.md'
        agents.write_text('# Keep\n```md\nunterminated')
        result = self.run_check()
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / 'harness/project').exists())
        self.assertEqual(agents.read_text(), '# Keep\n```md\nunterminated')

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

    def test_rules_link_is_restored_and_directory_created(self):
        (self.root / 'AGENTS.md').write_text('# User settings\n\n```md\n[Rules](.claude/rules/)\n```\n')
        first = self.run_check()
        self.assertEqual(first.returncode, 0, first.stderr)
        agents = self.root / 'AGENTS.md'
        self.assertEqual(agents.read_text().count('](.claude/rules/)'), 2)
        self.assertIn('README.human.md', agents.read_text())
        self.assertTrue((self.root / '.claude/rules').is_dir())
        before = agents.read_bytes()
        self.assertEqual(self.run_check().returncode, 0)
        self.assertEqual(agents.read_bytes(), before)

    def test_existing_relative_rules_links_are_not_duplicated(self):
        for target in ('.claude/rules', '.claude/rules/', './.claude/rules/', '<./.claude/rules/>'):
            with self.subTest(target=target):
                (self.root / 'AGENTS.md').write_text(f'# User settings\n[Rules]({target})\n')
                self.assertEqual(self.run_check().returncode, 0)
                text = (self.root / 'AGENTS.md').read_text()
                self.assertEqual(text.count('[Rules]'), 1)
                self.assertNotIn('- [.claude/rules]', text)
                self.assertIn('прочитай все Markdown-правила', text)

    def test_unsafe_rules_directory_does_not_change_entrypoints(self):
        (self.root / 'AGENTS.md').write_text('# Keep\n')
        for relative in ('.claude', '.claude/rules'):
            for symlink in (False, True):
                with self.subTest(relative=relative, symlink=symlink):
                    path = self.root / relative
                    path.parent.mkdir(exist_ok=True)
                    if symlink:
                        path.symlink_to(self.root / 'harness', target_is_directory=True)
                    else:
                        path.write_text('keep\n')
                    try:
                        result = self.run_check()
                        self.assertNotEqual(result.returncode, 0)
                        self.assertEqual((self.root / 'AGENTS.md').read_text(), '# Keep\n')
                        self.assertFalse((self.root / 'CLAUDE.md').exists())
                    finally:
                        path.unlink()


if __name__ == '__main__':
    unittest.main()
