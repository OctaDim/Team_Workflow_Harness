"""Exercise two supported installations and reject missing common."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGES = Path(__file__).resolve().parents[2]
MODES = [('common',), ('common', 'project')]


class PortabilityTest(unittest.TestCase):
    def install(self, root, mode):
        shutil.copytree(PACKAGES / 'common', root / 'harness/common',
                        ignore=shutil.ignore_patterns('inbox', '__pycache__'))
        if 'project' in mode:
            project = root / 'harness/project'
            if (PACKAGES / 'project').is_dir():
                shutil.copytree(PACKAGES / 'project', project)
            else:
                project.mkdir()
                (project / 'INDEX.md').write_text('# Existing project\n')
                (project / 'START.md').write_text('# Existing startup\n')
            material = project / 'docs/local-task/notes.md'
            material.parent.mkdir(parents=True, exist_ok=True)
            material.write_bytes(b'Existing project material\n')

    def run_check(self, root, script='harness/common/checks/ensure_entrypoint_links.py'):
        return subprocess.run([sys.executable, '-I', '-B', script], cwd=root,
                              env=dict(os.environ, PATH='/no-git-in-this-test'),
                              capture_output=True, text=True)

    def test_startup_command_runs_in_each_clean_mode_without_git(self):
        for mode in MODES:
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.install(root, mode)
                project = root / 'harness/project'
                before = {p.relative_to(project): p.read_bytes() for p in project.rglob('*')
                          if p.is_file() and p.name != 'README.human.md'}
                first = self.run_check(root)
                self.assertEqual(first.returncode, 0, first.stderr)
                if 'project' in mode:
                    self.assertEqual(before, {p.relative_to(project): p.read_bytes()
                                     for p in project.rglob('*') if p.is_file() and p.name != 'README.human.md'})
                else:
                    self.assertTrue((project / 'base/README.human.md').is_file())
                    self.assertFalse((project / 'docs/local-task').exists())
                text = (root / 'AGENTS.md').read_text()
                self.assertIn('](.claude/rules/)', text)
                self.assertIn('harness/project/START.md', text)
                command = re.search(r'(?m)^python3(?: -B)? (harness/[^\s]+\.py)$', text)
                self.assertIsNotNone(command)
                self.assertEqual(command.group(1), 'harness/common/checks/ensure_entrypoint_links.py')
                before_inputs = (root / 'AGENTS.md').read_bytes(), (root / 'CLAUDE.md').read_bytes()
                second = self.run_check(root, command.group(1))
                self.assertEqual(second.returncode, 0, second.stderr)
                self.assertNotIn('будут автоматически восстановлены', second.stdout)
                self.assertEqual(before_inputs, ((root / 'AGENTS.md').read_bytes(), (root / 'CLAUDE.md').read_bytes()))
                self.assertFalse((root / '.git').exists())

    def test_existing_settings_and_startup_command_are_never_rewritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.install(root, ('common', 'project'))
            legacy = root / 'harness/project/checks/ensure_entrypoint_links.py'
            script = legacy.relative_to(root).as_posix() if legacy.exists() else 'harness/common/checks/ensure_entrypoint_links.py'
            prefix = '# Existing settings\n\npython3 ' + script + '\nKeep this setting.\n'
            (root / 'AGENTS.md').write_text(prefix)
            result = self.run_check(root, script)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((root / 'AGENTS.md').read_text().startswith(prefix))

    def test_legacy_checker_rejects_symlinked_common_ancestors(self):
        for relative in ('harness/common', 'harness/common/checks'):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.install(root, ('common', 'project'))
                legacy = root / 'harness/project/checks/ensure_entrypoint_links.py'
                if not legacy.exists():
                    self.skipTest('No legacy shim in a common-only source installation.')
                external = root / 'external'
                checker = external / ('checks/ensure_entrypoint_links.py'
                                      if relative == 'harness/common' else 'ensure_entrypoint_links.py')
                checker.parent.mkdir(parents=True)
                marker = root / 'external-code-executed'
                checker.write_text('from pathlib import Path\nPath(' + repr(str(marker)) + ').touch()\n')
                directory_path = root / relative
                directory_path.rename(directory_path.with_name(directory_path.name + '-original'))
                directory_path.symlink_to(external, target_is_directory=True)
                result = self.run_check(root, str(legacy))
                self.assertFalse(marker.exists(), 'shim must reject symlinked ancestors before execution')
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertFalse((root / 'AGENTS.md').exists())

    def test_required_resource_damage_is_detected(self):
        for mode in MODES:
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.install(root, mode)
                (root / 'harness/common/START.md').unlink()
                result = self.run_check(root)
                self.assertEqual(result.returncode, 2)
                self.assertIn('START.md', result.stderr)
                self.assertFalse((root / 'AGENTS.md').exists())

    def test_project_only_rejected_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / 'harness/project'
            if (PACKAGES / 'project').is_dir():
                shutil.copytree(PACKAGES / 'project', project)
            else:
                project.mkdir(parents=True)
            legacy = project / 'checks/ensure_entrypoint_links.py'
            checker = str(legacy) if legacy.exists() else str(PACKAGES / 'common/checks/ensure_entrypoint_links.py')
            result = self.run_check(root, checker)
            self.assertEqual(result.returncode, 2)
            self.assertIn('common', result.stderr)
            self.assertFalse((root / 'AGENTS.md').exists())
            self.assertFalse((root / 'harness/common').exists())


if __name__ == '__main__':
    unittest.main()
