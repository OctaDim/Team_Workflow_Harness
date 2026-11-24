"""Exercise two supported installations and reject missing common."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import pytest
from pathlib import Path
from uuid import uuid4

PACKAGES = Path(__file__).resolve().parents[3]
MODES = [('common',), ('common', 'project')]
CHECK = 'harness/common/checks/ensure_entrypoint_links.py'
CONFIGS = ('.codex/hooks.json', '.claude/settings.json')


def test_hook_installation_preserves_existing_settings(published, startup):
    original = {
        'hooks': {'UserPromptSubmit': [{'hooks': [{'type': 'command', 'command': 'echo existing'}]}]},
        'customSetting': {'key': 'value'},
    }
    for relative in CONFIGS:
        path = published / relative
        path.parent.mkdir()
        path.write_text(json.dumps(original))
    assert startup(published).returncode == 3
    installed = {}
    for relative in CONFIGS:
        installed[relative] = (published / relative).read_bytes()
        parsed = json.loads(installed[relative])
        assert parsed['customSetting'] == original['customSetting']
        assert parsed['hooks']['UserPromptSubmit'][0] == original['hooks']['UserPromptSubmit'][0]
        assert len(parsed['hooks']['UserPromptSubmit']) == 2
        assert len(parsed['hooks']['SessionStart']) == 1
    assert startup(published).returncode == 0
    assert all((published / path).read_bytes() == data for path, data in installed.items())


@pytest.mark.parametrize('invalid', ('{', '{"hooks": {}, "hooks": {}}', '{"hooks": {"SessionStart": {}}}'))
def test_invalid_settings_leave_both_configs_unchanged(published, startup, invalid):
    for relative, data in zip(CONFIGS, ('{}', invalid)):
        path = published / relative
        path.parent.mkdir()
        path.write_text(data)
    result = startup(published)
    assert result.returncode == 2
    assert CONFIGS[1] in result.stderr
    assert (published / CONFIGS[0]).read_text() == '{}'
    assert (published / CONFIGS[1]).read_text() == invalid
    assert not (published / 'AGENTS.md').exists()


def test_resume_rejects_changed_published_startup_context(installed, monkeypatch):
    monkeypatch.setenv('XDG_STATE_HOME', str(installed.parent / 'state'))
    nested = installed / 'nested task folder'
    nested.mkdir()

    def hook(session, event, source='startup'):
        payload = {'hook_event_name': event, 'cwd': str(nested),
                   'session_id': str(session), 'source': source}
        result = subprocess.run([sys.executable, '-I', '-B', str(installed / CHECK),
                                 '--startup-hook', str(installed)], cwd=nested,
                                input=json.dumps(payload), capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        return json.loads(result.stdout) if result.stdout else None

    first, fresh = uuid4(), uuid4()
    hook(first, 'SessionStart')
    assert hook(first, 'UserPromptSubmit') == {'continue': True}
    for name in ('harness/common/rules/comm-fixture.md', '.claude/rules/comm-fixture.md'):
        (installed / name).write_bytes(b'new publication')
    hook(first, 'SessionStart', 'resume')
    blocked = hook(first, 'UserPromptSubmit')
    assert blocked['decision'] == 'block'
    assert 'Актуальность стартовых текстов' in blocked['reason']
    assert hook(first, 'UserPromptSubmit') == blocked
    hook(fresh, 'SessionStart')
    assert hook(fresh, 'UserPromptSubmit') == {'continue': True}


class TestPortability:

    def install(self, root, mode):
        shutil.copytree(PACKAGES / 'common', root / 'harness/common', ignore=shutil.ignore_patterns('inbox', 'evidence', 'handoffs', '__pycache__', '.pytest_cache'))
        native = root / '.claude/rules'
        shutil.copytree(PACKAGES / 'common/rules', native, ignore=shutil.ignore_patterns('README.human.md'))
        if 'project' in mode:
            project = root / 'harness/project'
            if (PACKAGES / 'project').is_dir():
                shutil.copytree(PACKAGES / 'project', project, ignore=shutil.ignore_patterns('inbox', 'evidence', 'handoffs', '__pycache__', '.pytest_cache'))
            else:
                project.mkdir()
                (project / 'INDEX.md').write_text('# Existing project\n')

            material = project / 'docs/local-task/notes.md'
            material.parent.mkdir(parents=True, exist_ok=True)
            material.write_bytes(b'Existing project material\n')
            for rule in (project / 'rules').glob('proj-*.md'):
                shutil.copyfile(rule, native / rule.name)

    def run_check(self, root, script='harness/common/checks/ensure_entrypoint_links.py', *args):
        return subprocess.run([sys.executable, '-I', '-B', script, *args], cwd=root, env=dict(os.environ, PATH='/no-git-in-this-test'), capture_output=True, text=True)

    @pytest.mark.parametrize('mode', MODES, ids=['common-only', 'common-and-project'])
    def test_startup_command_runs_in_each_clean_mode_without_git(self, mode):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.install(root, mode)
            project = root / 'harness/project'
            before = {p.relative_to(project): p.read_bytes() for p in project.rglob('*') if p.is_file()}
            first = self.run_check(root)
            assert first.returncode == 3, first.stderr
            if 'project' in mode:
                assert before == {p.relative_to(project): p.read_bytes() for p in project.rglob('*') if p.is_file()}
            else:
                assert (project / 'base/README.human.md').is_file()
                assert not (project / 'docs/local-task').exists()
            text = (root / 'AGENTS.md').read_text()
            assert (root / 'AGENTS.md').read_bytes() == (root / 'harness/common/base/AGENTS.template').read_bytes()
            assert '`.claude/rules`' in text and '`README.human.md`' in text
            assert 'включая поиск её файлов' in text and 'проверил полноту каждого файла' in text
            assert 'применяй полученные always loaded правила' in text
            assert 'START.md' not in text
            assert not (root / 'CLAUDE.md').read_bytes()
            script = 'harness/common/checks/ensure_entrypoint_links.py'
            for relative in ('.codex/hooks.json', '.claude/settings.json'):
                hooks = json.loads((root / relative).read_bytes())['hooks']
                for event in ('SessionStart', 'UserPromptSubmit'):
                    assert '--startup-hook' in hooks[event][0]['hooks'][0]['command']
            before_inputs = ((root / 'AGENTS.md').read_bytes(), (root / 'CLAUDE.md').read_bytes())
            second = self.run_check(root, script, '--check-startup')
            assert second.returncode == 0, second.stderr
            assert second.stdout == 'OK\n'
            assert before_inputs == ((root / 'AGENTS.md').read_bytes(), (root / 'CLAUDE.md').read_bytes())
            assert not (root / '.git').exists()
            target = root / '.claude/rules/comm-entrypoint-links-rule.md'
            approved = target.read_bytes()
            divergent = approved + b'\nLocal change.\n'
            target.write_bytes(divergent)
            rejected = self.run_check(root, script, '--check-startup')
            assert rejected.returncode == 4 and target.name in rejected.stdout
            assert target.read_bytes() == divergent
            restored = self.run_check(root, script, '--restore-rules')
            assert restored.returncode == 3, restored.stderr
            assert target.read_bytes() == approved
            assert self.run_check(root, script, '--check-startup').returncode == 0
            assert before_inputs == ((root / 'AGENTS.md').read_bytes(), (root / 'CLAUDE.md').read_bytes())


    def test_existing_settings_and_startup_command_are_never_rewritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.install(root, ('common', 'project'))
            script = 'harness/common/checks/ensure_entrypoint_links.py'
            prefix = '# Existing settings\n\npython3 ' + script + '\nKeep this setting.\n'
            (root / 'AGENTS.md').write_text(prefix)
            result = self.run_check(root, script)
            assert result.returncode == 2, result.stderr
            assert (root / 'AGENTS.md').read_text() == prefix
            assert 'AGENTS.md' in result.stderr and 'INBOX' in result.stderr

    @pytest.mark.parametrize('mode', MODES, ids=['common-only', 'common-and-project'])
    @pytest.mark.parametrize('relative', ('harness/common', 'harness/common/checks', 'harness/common/checks/ensure_entrypoint_links.py'))
    def test_common_checker_rejects_symlinked_paths_without_writes(self, relative, mode):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.install(root, mode)
            external = root / 'external'
            checker = external / ('checks/ensure_entrypoint_links.py' if relative == 'harness/common' else 'ensure_entrypoint_links.py')
            checker.parent.mkdir(parents=True)
            marker = root / 'external-code-executed'
            checker.write_text('from pathlib import Path\nPath(' + repr(str(marker)) + ').touch()\n')
            directory_path = root / relative
            directory_path.rename(directory_path.with_name(directory_path.name + '-original'))
            directory_path.symlink_to(checker if directory_path.suffix == '.py' else external,
                                      target_is_directory=directory_path.suffix != '.py')
            # The trusted checker inspects the tree; never execute the substituted file.
            script = str(PACKAGES / 'common/checks/ensure_entrypoint_links.py')
            result = subprocess.run([sys.executable, '-I', '-B', script, str(root)],
                                    capture_output=True, text=True)
            assert not marker.exists(), 'unsafe resources must not be executed'
            assert result.returncode == 2, result.stderr
            assert not (root / 'AGENTS.md').exists()

    @pytest.mark.parametrize('mode', MODES, ids=['common-only', 'common-and-project'])
    def test_required_resource_damage_is_detected(self, mode):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.install(root, mode)
            (root / 'harness/common/base/AGENTS.template').unlink()
            result = self.run_check(root)
            assert result.returncode == 2
            assert 'AGENTS.template' in result.stderr
            assert not (root / 'AGENTS.md').exists()

    def test_project_only_rejected_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / 'harness/project'
            if (PACKAGES / 'project').is_dir():
                shutil.copytree(PACKAGES / 'project', project, ignore=shutil.ignore_patterns('inbox', 'evidence', 'handoffs', '__pycache__', '.pytest_cache'))
            else:
                project.mkdir(parents=True)
            checker = str(PACKAGES / 'common/checks/ensure_entrypoint_links.py')
            result = self.run_check(root, checker)
            assert result.returncode == 2
            assert 'common' in result.stderr
            assert not (root / 'AGENTS.md').exists()
            assert not (root / 'harness/common').exists()

    @pytest.mark.parametrize('relative', ('harness/common', 'harness/common/checks', 'harness/common/checks/ensure_entrypoint_links.py'))
    def test_direct_checker_rejects_its_own_symlinked_path(self, relative):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.install(root, ('common',))
            path = root / relative
            original = path.with_name(path.name + '-original')
            path.rename(original)
            path.symlink_to(original, target_is_directory=original.is_dir())
            result = self.run_check(root)
            assert result.returncode == 2, result.stderr
            assert not (root / 'AGENTS.md').exists()
            assert not (root / 'harness/project').exists()

    def test_symlinked_target_root_is_rejected_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            root.mkdir()
            self.install(root, ('common',))
            alias = root.with_name('alias')
            alias.symlink_to(root, target_is_directory=True)
            result = subprocess.run([sys.executable, '-I', '-B',
                                    str(PACKAGES / 'common/checks/ensure_entrypoint_links.py'), str(alias)],
                                    capture_output=True, text=True)
            assert result.returncode == 2, result.stderr
            assert not (root / 'AGENTS.md').exists()
            assert not (root / 'harness/project').exists()
