"""Copy complete packages and execute only their own installed checker."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGES = Path(__file__).resolve().parents[2]
INSTALLED = tuple(name for name in ('common', 'project') if (PACKAGES/name).is_dir())
MODES = [(name,) for name in INSTALLED] + ([INSTALLED] if len(INSTALLED) == 2 else [])


class PortabilityTest(unittest.TestCase):
    def test_startup_command_runs_in_each_clean_mode_without_git(self):
        for mode in MODES:
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for name in mode:
                    shutil.copytree(PACKAGES/name, root/'harness'/name)
                script = root/'harness'/mode[0]/'checks/ensure_entrypoint_links.py'
                self.assertTrue(script.is_file(), f'Missing standalone checker: {script}')
                environment = dict(os.environ, PATH='/no-git-in-this-test')
                first = subprocess.run([sys.executable, '-I', '-B', str(script)], cwd=root,
                                       env=environment, capture_output=True, text=True)
                self.assertEqual(first.returncode, 0, first.stderr)
                text = (root/'AGENTS.md').read_text()
                command = re.search(r'(?m)^python3(?: -B)? (harness/[^\s]+\.py)$', text)
                self.assertIsNotNone(command, 'Static startup instruction missing.')
                self.assertTrue((root/command.group(1)).is_file(), 'Generated startup points to absent sibling.')
                before = (root/'AGENTS.md').read_bytes(), (root/'CLAUDE.md').read_bytes()
                startup = subprocess.run([sys.executable, '-I', '-B', command.group(1)], cwd=root,
                                         env=environment, capture_output=True, text=True)
                self.assertEqual(startup.returncode, 0, startup.stderr)
                self.assertNotIn('будут автоматически восстановлены', startup.stdout)
                self.assertEqual(before, ((root/'AGENTS.md').read_bytes(), (root/'CLAUDE.md').read_bytes()))
                self.assertEqual(before[1], b'@AGENTS.md\n')
                for name in set(('common', 'project'))-set(mode):
                    self.assertNotIn(f'harness/{name}/', text)
                self.assertFalse((root/'.git').exists())

    def test_existing_settings_and_startup_command_are_never_rewritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            name = INSTALLED[0]
            shutil.copytree(PACKAGES/name, root/'harness'/name)
            prefix = '# Existing settings\n\nKeep this exact startup command and setting.\n'
            (root/'AGENTS.md').write_text(prefix)
            (root/'CLAUDE.md').write_text('@AGENTS.md\n')
            result = subprocess.run([sys.executable, '-I', '-B', f'harness/{name}/checks/ensure_entrypoint_links.py'],
                                    cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((root/'AGENTS.md').read_text().startswith(prefix))

    def test_required_resource_damage_is_detected_by_each_own_checker(self):
        for name in INSTALLED:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                shutil.copytree(PACKAGES/name, root/'harness'/name)
                script = root/'harness'/name/'checks/ensure_entrypoint_links.py'
                self.assertTrue(script.is_file(), f'Missing checker: {name}')
                (root/'harness'/name/'START.md').unlink()
                result = subprocess.run([sys.executable, '-I', '-B', str(script)], cwd=root,
                                        capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('START.md', result.stderr)
                self.assertFalse((root/'AGENTS.md').exists())

    def test_installed_runtime_files_are_regular_and_match_when_both_installed(self):
        self.assertTrue(INSTALLED, 'No installed package to check.')
        copies = []
        for name in INSTALLED:
            file = PACKAGES/name/'checks/ensure_entrypoint_links.py'
            self.assertTrue(file.is_file(), f'Runtime copy must ship with {name}.')
            self.assertFalse(file.is_symlink())
            copies.append(file.read_bytes())
        if len(copies) == 2:
            self.assertEqual(copies[0], copies[1])
        else:
            print('Peer byte comparison: not checked (only one package installed).')


if __name__ == '__main__':
    if len(INSTALLED) < 2:
        print('Uninstalled package modes: not checked; active modes:', MODES)
    unittest.main()
