"""Exercise two supported installations and reject missing common."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import pytest
from pathlib import Path

PACKAGES = Path(__file__).resolve().parents[3]
MODES = [('common',), ('common', 'project')]


class TestPortability:

    def install(self, root, mode):
        shutil.copytree(PACKAGES / 'common', root / 'harness/common', ignore=shutil.ignore_patterns('inbox', '__pycache__'))
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

    def run_check(self, root, script='harness/common/checks/ensure_entrypoint_links.py', *args):
        return subprocess.run([sys.executable, '-I', '-B', script, *args], cwd=root, env=dict(os.environ, PATH='/no-git-in-this-test'), capture_output=True, text=True)

    @pytest.mark.parametrize('mode', MODES, ids=['common-only', 'common-and-project'])
    def test_startup_command_runs_in_each_clean_mode_without_git(self, mode):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.install(root, mode)
            project = root / 'harness/project'
            before = {p.relative_to(project): p.read_bytes() for p in project.rglob('*') if p.is_file() and p.name != 'README.human.md'}
            first = self.run_check(root, 'harness/common/checks/ensure_entrypoint_links.py', '--create-project')
            assert first.returncode == 0, first.stderr
            if 'project' in mode:
                assert before == {p.relative_to(project): p.read_bytes() for p in project.rglob('*') if p.is_file() and p.name != 'README.human.md'}
            else:
                assert (project / 'base/README.human.md').is_file()
                assert not (project / 'docs/local-task').exists()
            text = (root / 'AGENTS.md').read_text()
            assert '](.claude/rules/)' in text
            assert 'harness/project/START.md' in text
            command = re.search('(?m)^python3(?: -B)? (harness/[^\\s]+\\.py)$', text)
            assert command is not None
            assert command.group(1) == 'harness/common/checks/ensure_entrypoint_links.py'
            before_inputs = ((root / 'AGENTS.md').read_bytes(), (root / 'CLAUDE.md').read_bytes())
            second = self.run_check(root, command.group(1))
            assert second.returncode == 0, second.stderr
            assert 'будут автоматически восстановлены' not in second.stdout
            assert before_inputs == ((root / 'AGENTS.md').read_bytes(), (root / 'CLAUDE.md').read_bytes())
            assert not (root / '.git').exists()

    def test_existing_settings_and_startup_command_are_never_rewritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.install(root, ('common', 'project'))
            legacy = root / 'harness/project/checks/ensure_entrypoint_links.py'
            script = legacy.relative_to(root).as_posix() if legacy.exists() else 'harness/common/checks/ensure_entrypoint_links.py'
            prefix = '# Existing settings\n\npython3 ' + script + '\nKeep this setting.\n'
            (root / 'AGENTS.md').write_text(prefix)
            result = self.run_check(root, script)
            assert result.returncode == 0, result.stderr
            assert (root / 'AGENTS.md').read_text().startswith(prefix)

    @pytest.mark.parametrize('relative', ('harness/common', 'harness/common/checks'), ids=['harness-common', 'harness-common-checks'])
    def test_legacy_checker_rejects_symlinked_common_ancestors(self, relative):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.install(root, ('common', 'project'))
            legacy = root / 'harness/project/checks/ensure_entrypoint_links.py'
            if not legacy.exists():
                pytest.skip('No legacy shim in a common-only source installation.')
            external = root / 'external'
            checker = external / ('checks/ensure_entrypoint_links.py' if relative == 'harness/common' else 'ensure_entrypoint_links.py')
            checker.parent.mkdir(parents=True)
            marker = root / 'external-code-executed'
            checker.write_text('from pathlib import Path\nPath(' + repr(str(marker)) + ').touch()\n')
            directory_path = root / relative
            directory_path.rename(directory_path.with_name(directory_path.name + '-original'))
            directory_path.symlink_to(external, target_is_directory=True)
            result = self.run_check(root, str(legacy))
            assert not marker.exists(), 'shim must reject symlinked ancestors before execution'
            assert result.returncode == 2, result.stderr
            assert not (root / 'AGENTS.md').exists()

    @pytest.mark.parametrize('mode', MODES, ids=['common-only', 'common-and-project'])
    def test_required_resource_damage_is_detected(self, mode):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.install(root, mode)
            (root / 'harness/common/START.md').unlink()
            result = self.run_check(root, 'harness/common/checks/ensure_entrypoint_links.py', '--create-project')
            assert result.returncode == 2
            assert 'START.md' in result.stderr
            assert not (root / 'AGENTS.md').exists()

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
            assert result.returncode == 2
            assert 'common' in result.stderr
            assert not (root / 'AGENTS.md').exists()
            assert not (root / 'harness/common').exists()
