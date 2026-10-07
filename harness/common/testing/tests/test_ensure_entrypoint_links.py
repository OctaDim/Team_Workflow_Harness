"""Run with pytest; uses only temporary projects."""
import json
import shutil
import subprocess
import sys
import pytest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / 'checks/ensure_entrypoint_links.py'


class TestEntryPointLinks:

    @pytest.fixture(autouse=True)
    def _project(self, tmp_path):
        self.root = tmp_path
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
        return subprocess.run([sys.executable, '-B', str(SCRIPT), str(self.root)], text=True, capture_output=True)

    def test_creates_four_links_and_import_then_preserves_bytes(self):
        result = self.run_check()
        assert result.returncode == 0, result.stderr
        agents = self.root / 'AGENTS.md'
        claude = self.root / 'CLAUDE.md'
        for package in ('common', 'project'):
            for name in ('INDEX.md', 'START.md'):
                assert f'](harness/{package}/{name})' in agents.read_text()
        assert claude.read_bytes() == b'@AGENTS.md\n'
        before = (agents.read_bytes(), claude.read_bytes())
        assert self.run_check().returncode == 0
        assert before == (agents.read_bytes(), claude.read_bytes())
        for file in self.root.glob('harness/*/START.md'):
            assert file.read_bytes() == b''

    def test_only_appends_missing_links_preserving_user_text(self):
        prefix = '# User configuration\n\nKeep this exact text.\n[Existing](./harness/common/INDEX.md)\n'
        (self.root / 'AGENTS.md').write_text(prefix)
        assert self.run_check().returncode == 0
        text = (self.root / 'AGENTS.md').read_text()
        assert text.startswith(prefix)
        assert text.count('harness/common/INDEX.md') == 1

    def test_link_examples_in_code_do_not_count_as_real_links(self):
        examples = '\n'.join((f'[Example](harness/{p}/{n})' for p in ('common', 'project') for n in ('INDEX.md', 'START.md')))
        (self.root / 'AGENTS.md').write_text(f'```md\n{examples}\n```\n')
        assert self.run_check().returncode == 0
        text = (self.root / 'AGENTS.md').read_text()
        assert text.count('](harness/common/INDEX.md)') == 2

    @pytest.mark.parametrize('newline', (b'\n', b'\r\n'), ids=['LF', 'CRLF'])
    def test_repair_preserves_original_bytes_and_each_files_line_endings(self, newline):
        agents, claude = (self.root / 'AGENTS.md', self.root / 'CLAUDE.md')
        original = newline.join((b'# User settings', b'Keep exact bytes.', b'', b''))
        bridge = b'User bridge text\r\n'
        agents.write_bytes(original)
        claude.write_bytes(bridge)
        result = self.run_check()
        assert result.returncode == 0, result.stderr
        repaired = agents.read_bytes()
        assert repaired.startswith(original)
        assert b'](harness/common/START.md)' + newline in repaired
        if newline == b'\r\n':
            assert b'\n' not in repaired.replace(b'\r\n', b'')
        assert claude.read_bytes() == b'@AGENTS.md\r\n' + bridge
        before = (agents.read_bytes(), claude.read_bytes())
        second = self.run_check()
        assert second.returncode == 0, second.stderr
        assert 'будут автоматически восстановлены' not in second.stdout
        assert (agents.read_bytes(), claude.read_bytes()) == before

    def test_valid_crlf_bridge_is_preserved_without_warning_or_repair(self):
        assert self.run_check().returncode == 0
        agents, claude = (self.root / 'AGENTS.md', self.root / 'CLAUDE.md')
        agents.write_bytes(agents.read_bytes().replace(b'\n', b'\r\n'))
        claude.write_bytes(b'@AGENTS.md\r\n')
        before = (agents.read_bytes(), claude.read_bytes())
        result = self.run_check()
        assert result.returncode == 0, result.stderr
        assert 'будут автоматически восстановлены' not in result.stdout
        assert 'требуется единственная строка' not in result.stdout
        assert (agents.read_bytes(), claude.read_bytes()) == before

    @pytest.mark.parametrize('opener,closer', (('~~~md', '~~~~'), ('```md', '````')), ids=['tilde', 'backtick'])
    def test_longer_fence_closers_do_not_turn_examples_into_installed_links(self, opener, closer):
        examples = '\n'.join((f'[Example](harness/{p}/{n})' for p in ('common', 'project') for n in ('INDEX.md', 'START.md')))
        examples += '\n[Rules](.claude/rules/)\nДо выполнения задачи прочитай все Markdown-правила из .claude/rules и его подпапок, кроме README.human.md; соблюдай применимые требования.'
        agents = self.root / 'AGENTS.md'
        prefix = f'# Keep user settings\n{opener}\n{examples}\n{closer}\n'
        agents.write_text(prefix)
        first = self.run_check()
        assert first.returncode == 0, first.stderr
        text = agents.read_text()
        assert text.startswith(prefix)
        appended = text[len(prefix):]
        for package in ('common', 'project'):
            for name in ('INDEX.md', 'START.md'):
                assert f'](harness/{package}/{name})' in appended
        assert '](.claude/rules/)' in appended
        assert 'прочитай все Markdown-правила' in appended
        before = agents.read_bytes()
        second = self.run_check()
        assert second.returncode == 0, second.stderr
        assert agents.read_bytes() == before

    @pytest.mark.parametrize('name', ('AGENTS.md', 'CLAUDE.md'), ids=['AGENTS.md', 'CLAUDE.md'])
    @pytest.mark.parametrize('opener', ('~~~md', '```md'), ids=['tilde', 'backtick'])
    def test_unclosed_fence_fails_before_writing_either_entrypoint(self, name, opener):
        agents, claude = (self.root / 'AGENTS.md', self.root / 'CLAUDE.md')
        agents.write_text('# Keep user settings\n')
        claude.write_text('Keep bridge text\n')
        (self.root / name).write_text(f'# Keep user settings\n{opener}\nexample\n')
        before = (agents.read_bytes(), claude.read_bytes())
        result = self.run_check()
        assert result.returncode == 2, result.stderr
        assert 'Unclosed Markdown code fence' in result.stderr
        assert (agents.read_bytes(), claude.read_bytes()) == before
        assert not (self.root / '.claude').exists()

    def test_damaged_package_is_reported_without_creating_dangling_links(self):
        (self.root / 'harness/project/START.md').unlink()
        result = self.run_check()
        assert result.returncode != 0
        assert not (self.root / 'AGENTS.md').exists()
        assert not (self.root / 'CLAUDE.md').exists()

    def test_common_only_creates_neutral_project(self):
        shutil.rmtree(self.root / 'harness/project')
        result = self.run_check()
        assert result.returncode == 0, result.stderr
        project = self.root / 'harness/project'
        expected = {'base', 'decisions', 'testing', 'rules', 'skills', 'checks', 'scripts', 'specs', 'inbox', 'docs', 'handoffs'}
        assert project.is_dir(), 'common-only must create project'
        assert {p.name for p in project.iterdir() if p.is_dir()} == expected
        assert {p.name for p in (project / 'testing').iterdir() if p.is_dir()} == {'acceptance', 'tests', 'evidence'}
        assert all((project / 'testing' / name / 'README.human.md').is_file() for name in ('acceptance', 'tests', 'evidence'))
        for directory in [project, *(project / name for name in expected)]:
            assert (directory / 'README.human.md').is_file()
        assert not (project / 'lessons').exists()
        assert (project / 'docs/plans/README.human.md').is_file()
        assert not (project / 'checks/ensure_entrypoint_links.py').exists()
        assert 'EPL' not in (project / 'INDEX.md').read_text()
        assert 'harness/common/checks/ensure_entrypoint_links.py' in (project / 'START.md').read_text()
        assert 'harness/project/START.md' in (self.root / 'AGENTS.md').read_text()
        before = {p.relative_to(project): p.stat().st_mtime_ns for p in project.rglob('*')}
        assert self.run_check().returncode == 0
        assert before == {p.relative_to(project): p.stat().st_mtime_ns for p in project.rglob('*')}

    def test_existing_project_is_not_regenerated_or_exported(self):
        project = self.root / 'harness/project'
        task = project / 'docs/epl-import/notes.md'
        task.parent.mkdir(parents=True)
        task.write_bytes(b'project-specific material\n')
        legacy = project / 'lessons/legacy.md'
        legacy.parent.mkdir()
        legacy.write_bytes(b'existing legacy material: startup must preserve it\n')
        before = {p.relative_to(project): p.read_bytes() for p in project.rglob('*') if p.is_file()}
        assert self.run_check().returncode == 0
        assert before == {p.relative_to(project): p.read_bytes() for p in project.rglob('*') if p.is_file()}
        assert not (project / 'base').exists(), 'existing project is not filled with a new skeleton'

    def test_new_template_categories_apply_only_to_new_project(self):
        template = self.root / 'harness/common/base/project-skeleton.json'
        data = json.loads(template.read_text())
        data['categories']['specs'] = {'purpose': 'Shared specifications', 'example': 'api.md describes an agreed API.'}
        template.write_text(json.dumps(data))
        assert self.run_check().returncode == 0
        assert not (self.root / 'harness/project/specs').exists()
        shutil.rmtree(self.root / 'harness/project')
        result = self.run_check()
        assert result.returncode == 0, result.stderr
        assert (self.root / 'harness/project/specs/README.human.md').is_file()

    def test_project_only_is_rejected_before_writes(self):
        shutil.rmtree(self.root / 'harness/common')
        result = self.run_check()
        assert result.returncode == 2
        assert 'common' in result.stderr
        assert not (self.root / 'AGENTS.md').exists()
        assert not (self.root / '.claude').exists()

    @pytest.mark.parametrize('symlink', (False, True), ids=['regular-file', 'symlink'])
    def test_unsafe_project_path_is_rejected_without_writes(self, symlink):
        project = self.root / 'harness/project'
        shutil.rmtree(project)
        if symlink:
            project.symlink_to(self.root / 'missing-project')
        else:
            project.write_text('keep this file')
        result = self.run_check()
        assert result.returncode == 2
        assert not (self.root / 'AGENTS.md').exists()
        assert not (self.root / '.claude').exists()
        project.unlink()

    @pytest.mark.parametrize('content', ('not json', '{}', '{"categories": {"../outside": {"purpose": "bad", "example": "bad"}}}'), ids=['invalid-json', 'missing-categories', 'path-traversal'])
    def test_invalid_template_does_not_create_project(self, content):
        project = self.root / 'harness/project'
        shutil.rmtree(project)
        template = self.root / 'harness/common/base/project-skeleton.json'
        template.write_text(content)
        result = self.run_check()
        assert result.returncode == 2
        assert not project.exists()
        assert not (self.root / 'AGENTS.md').exists()

    def test_invalid_entrypoint_prevents_project_creation(self):
        shutil.rmtree(self.root / 'harness/project')
        agents = self.root / 'AGENTS.md'
        agents.write_text('# Keep\n```md\nunterminated')
        result = self.run_check()
        assert result.returncode == 2
        assert not (self.root / 'harness/project').exists()
        assert agents.read_text() == '# Keep\n```md\nunterminated'

    def test_adds_import_and_warns_about_extra_claude_content_without_deleting_it(self):
        (self.root / 'CLAUDE.md').write_text('User text\n')
        result = self.run_check()
        assert result.returncode == 0
        assert 'inbox' in result.stdout
        assert 'технически не заблокировано' in result.stdout
        assert (self.root / 'CLAUDE.md').read_text() == '@AGENTS.md\nUser text\n'

    def test_refuses_symlinked_entrypoint_without_changing_target(self):
        target = self.root / 'user.md'
        target.write_text('User text\n')
        (self.root / 'AGENTS.md').symlink_to(target)
        assert self.run_check().returncode != 0
        assert target.read_text() == 'User text\n'

    def test_rules_link_is_restored_and_directory_created(self):
        (self.root / 'AGENTS.md').write_text('# User settings\n\n```md\n[Rules](.claude/rules/)\n```\n')
        first = self.run_check()
        assert first.returncode == 0, first.stderr
        agents = self.root / 'AGENTS.md'
        assert agents.read_text().count('](.claude/rules/)') == 2
        assert 'README.human.md' in agents.read_text()
        assert (self.root / '.claude/rules').is_dir()
        before = agents.read_bytes()
        assert self.run_check().returncode == 0
        assert agents.read_bytes() == before

    @pytest.mark.parametrize('target', ('.claude/rules', '.claude/rules/', './.claude/rules/', '<./.claude/rules/>'))
    def test_existing_relative_rules_links_are_not_duplicated(self, target):
        (self.root / 'AGENTS.md').write_text(f'# User settings\n[Rules]({target})\n')
        assert self.run_check().returncode == 0
        text = (self.root / 'AGENTS.md').read_text()
        assert text.count('[Rules]') == 1
        assert '- [.claude/rules]' not in text
        assert 'прочитай все Markdown-правила' in text

    @pytest.mark.parametrize('relative', ('.claude', '.claude/rules'), ids=['.claude', '.claude-rules'])
    @pytest.mark.parametrize('symlink', (False, True), ids=['regular-file', 'symlink'])
    def test_unsafe_rules_directory_does_not_change_entrypoints(self, relative, symlink):
        (self.root / 'AGENTS.md').write_text('# Keep\n')
        path = self.root / relative
        path.parent.mkdir(exist_ok=True)
        if symlink:
            path.symlink_to(self.root / 'harness', target_is_directory=True)
        else:
            path.write_text('keep\n')
        try:
            result = self.run_check()
            assert result.returncode != 0
            assert (self.root / 'AGENTS.md').read_text() == '# Keep\n'
            assert not (self.root / 'CLAUDE.md').exists()
        finally:
            path.unlink()
