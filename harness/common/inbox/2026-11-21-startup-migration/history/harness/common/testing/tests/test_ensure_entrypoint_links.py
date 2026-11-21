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
        for folder in ('harness/common/rules', '.claude/rules'):
            rules = self.root / folder
            rules.mkdir(parents=True)
            (rules / 'comm-fixture.md').write_bytes(b'# Rule fixture\n')
        for package in ('common', 'project'):
            directory = self.root / 'harness' / package
            directory.mkdir(parents=True, exist_ok=True)
            (directory / 'INDEX.md').write_text('# Index\n')
            (directory / 'START.md').write_bytes(b'# Start\n')
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
            assert file.read_bytes() == b'# Start\n'

    @pytest.mark.parametrize('newline', ('\n', '\r\n'), ids=['LF', 'CRLF'])
    @pytest.mark.parametrize('common_only', (False, True), ids=['combined', 'common-only'])
    @pytest.mark.parametrize('adjacent', (False, True))
    @pytest.mark.parametrize('missing', ('harness/common/START.md', '.claude/rules/'))
    def test_repairs_each_repeated_block_before_index_without_changing_settings(self, newline, common_only, adjacent, missing):
        if common_only:
            shutil.rmtree(self.root / 'harness/project')
        paths = ['harness/common/START.md', 'harness/project/START.md', '.claude/rules/',
                 'harness/common/INDEX.md', 'harness/project/INDEX.md']
        block = ''.join(f'- [{path}]({path})\n' for path in paths)
        block = block.replace('](.claude/rules/)\n',
            '](.claude/rules/) До выполнения задачи прочитай все Markdown-правила из .claude/rules '
            'и его подпапок, кроме README.human.md; соблюдай применимые требования.\n')
        prefix, separator = '# User settings: keep exact bytes.\n\n', '\nRepeat:\n'
        damaged = ''.join(line for line in block.splitlines(keepends=True) if f']({missing})' not in line)
        if adjacent:
            separator = ''
            damaged = damaged.rstrip('\n')
        agents = self.root / 'AGENTS.md'
        agents.write_bytes((prefix + block + separator + damaged).replace('\n', newline).encode())
        assert self.run_check().returncode == 0
        repaired_block = (block.replace('- [.claude/rules/]', '- [.claude/rules]')
                          if missing == '.claude/rules/' else block)
        expected = (prefix + block + separator + repaired_block).replace('\n', newline).encode()
        assert agents.read_bytes() == expected
        assert self.run_check().returncode == 0
        assert agents.read_bytes() == expected

    def test_only_appends_missing_links_preserving_user_text(self):
        prefix = '# User configuration\n\nKeep this exact text.\n[Existing](./harness/common/INDEX.md)\n'
        (self.root / 'AGENTS.md').write_text(prefix)
        assert self.run_check().returncode == 0
        text = (self.root / 'AGENTS.md').read_text()
        assert text.startswith(prefix)
        assert text.count('harness/common/INDEX.md') == 1
        before = (self.root / 'AGENTS.md').read_bytes()
        assert self.run_check().returncode == 0
        assert (self.root / 'AGENTS.md').read_bytes() == before

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
        assert (self.root / '.claude/rules/comm-fixture.md').read_bytes() == b'# Rule fixture\n'

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
        for branch in ('work', 'harness'):
            assert (project / 'testing/evidence' / branch / 'README.human.md').is_file()
            assert f'testing/evidence/{branch}/' in (project / 'INDEX.md').read_text()
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
        assert (self.root / '.claude/rules/comm-fixture.md').read_bytes() == b'# Rule fixture\n'

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
        assert (self.root / '.claude/rules/comm-fixture.md').read_bytes() == b'# Rule fixture\n'
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

    def test_rules_link_is_restored_with_existing_valid_copies(self):
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
        shutil.rmtree(path)
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


    def test_deleted_project_recreates_neutral_skeleton_without_history(self):
        project = self.root / 'harness/project'
        shutil.rmtree(project)
        assert self.run_check().returncode == 0
        skeleton = {p.relative_to(project): p.read_bytes() for p in project.rglob('*') if p.is_file()}
        (project / 'testing/evidence/work/old-run.log').write_bytes(b'old raw result')
        shutil.rmtree(project)
        assert self.run_check().returncode == 0
        assert skeleton == {p.relative_to(project): p.read_bytes() for p in project.rglob('*') if p.is_file()}

    @pytest.mark.parametrize('name', ('START.md', 'INDEX.md'))
    def test_partial_project_missing_entrypoint_fails_without_replacement(self, name):
        project = self.root / 'harness/project'
        (project / name).unlink()
        before = {p.relative_to(project): p.read_bytes() for p in project.rglob('*') if p.is_file()}
        assert self.run_check().returncode == 2
        assert before == {p.relative_to(project): p.read_bytes() for p in project.rglob('*') if p.is_file()}
        assert not (self.root / 'AGENTS.md').exists()

    @pytest.mark.parametrize('package', ('common', 'project'))
    @pytest.mark.parametrize('name', ('START.md', 'INDEX.md'))
    @pytest.mark.parametrize('content', (b'', b' \r\n', b'\xff'))
    def test_empty_or_invalid_utf8_resources_refuse_before_input_writes(self, package, name, content):
        (self.root / 'harness' / package / name).write_bytes(content)
        result = self.run_check()
        assert result.returncode == 2, result.stderr
        assert str(Path('harness') / package / name) in result.stderr
        assert not (self.root / 'AGENTS.md').exists()
        assert not (self.root / 'CLAUDE.md').exists()

    @pytest.mark.parametrize('damage', ('missing-directory', 'missing-copy', 'different-copy',
                                      'extra-copy', 'empty-source', 'invalid-utf8-source', 'nested-canonical'))
    def test_invalid_rule_copies_are_refused_without_automatic_publication(self, damage):
        native = self.root / '.claude/rules'
        source = self.root / 'harness/common/rules/comm-fixture.md'
        copy = native / source.name
        if damage == 'missing-directory':
            shutil.rmtree(native)
        elif damage == 'missing-copy':
            copy.unlink()
        elif damage == 'different-copy':
            copy.write_bytes(b'different\n')
        elif damage == 'extra-copy':
            (native / 'proj-extra.md').write_bytes(b'extra\n')
        elif damage == 'empty-source':
            source.write_bytes(b' \n')
            copy.write_bytes(source.read_bytes())
        elif damage == 'invalid-utf8-source':
            source.write_bytes(b'\xff')
            copy.write_bytes(source.read_bytes())
        else:
            (native / 'nested').mkdir()
            (native / 'nested/comm-fixture.md').write_bytes(source.read_bytes())
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = self.run_check()
        assert result.returncode == 2, result.stderr
        assert before == {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        assert native.exists() == (damage != 'missing-directory')

    def test_personal_nested_rules_and_human_bodies_are_not_canonical_copies(self):
        native = self.root / '.claude/rules'
        (native / 'personal').mkdir()
        (native / 'personal/local.md').write_bytes(b'# Personal rule\n')
        (native / 'README.human.md').write_bytes(b'\xff')
        (self.root / 'harness/common/rules/README.human.md').write_bytes(b'\xff')
        assert self.run_check().returncode == 0

    def test_complete_block_in_wrong_order_refuses_without_reordering_user_file(self):
        paths = ('harness/common/INDEX.md', 'harness/common/START.md',
                 'harness/project/START.md', '.claude/rules/', 'harness/project/INDEX.md')
        agents = self.root / 'AGENTS.md'
        original = ''.join(f'- [{p}]({p})\n' for p in paths).encode()
        agents.write_bytes(original)
        result = self.run_check()
        assert result.returncode == 2, result.stderr
        assert 'order' in result.stderr.lower()
        assert agents.read_bytes() == original
        assert not (self.root / 'CLAUDE.md').exists()

    def test_repeated_block_with_two_missing_links_is_repaired_locally(self):
        paths = ('harness/common/START.md', 'harness/project/START.md', '.claude/rules/',
                 'harness/common/INDEX.md', 'harness/project/INDEX.md')
        block = ''.join(f'- [{p}]({p})\n' for p in paths)
        damaged = ''.join(line for line in block.splitlines(keepends=True)
                          if 'common/START.md' not in line and '.claude/rules/' not in line)
        agents = self.root / 'AGENTS.md'
        agents.write_text(block + '\nRepeat:\n' + damaged)
        result = self.run_check()
        assert result.returncode == 0, result.stderr
        repaired = agents.read_text().split('\nRepeat:\n')[1]
        for path in paths:
            assert f']({path})' in repaired
        assert repaired.index('common/START') < repaired.index('project/START') < repaired.index('.claude/rules') < repaired.index('common/INDEX')
        before = agents.read_bytes()
        assert self.run_check().returncode == 0
        assert agents.read_bytes() == before

    def test_ambiguous_partial_link_list_refuses_without_adding_to_user_list(self):
        agents = self.root / 'AGENTS.md'
        original = b'- [My note](harness/common/START.md)\n- [Another note](harness/common/INDEX.md)\n'
        agents.write_bytes(original)
        result = self.run_check()
        assert result.returncode == 2, result.stderr
        assert 'ambiguous' in result.stderr.lower()
        assert agents.read_bytes() == original

    def test_three_custom_user_links_are_not_assumed_to_be_a_generated_block(self):
        agents = self.root / 'AGENTS.md'
        original = (b'- [My note](harness/common/START.md)\n'
                    b'- [Project note](harness/project/START.md)\n'
                    b'- [Another note](harness/common/INDEX.md)\n')
        agents.write_bytes(original)
        result = self.run_check()
        assert result.returncode == 2, result.stderr
        assert 'ambiguous' in result.stderr.lower()
        assert agents.read_bytes() == original

    def test_relative_anchored_complete_block_order_is_checked_without_rewriting(self):
        paths = ('harness/common/INDEX.md', 'harness/common/START.md',
                 'harness/project/START.md', '.claude/rules/', 'harness/project/INDEX.md')
        agents = self.root / 'AGENTS.md'
        original = ''.join(f'- [Custom {i}](<./{path}#section>)\n' for i, path in enumerate(paths)).encode()
        agents.write_bytes(original)
        result = self.run_check()
        assert result.returncode == 2, result.stderr
        assert 'order' in result.stderr.lower()
        assert agents.read_bytes() == original

    @pytest.mark.parametrize('prefix,continuation', (('> ', '> '), ('> > ', '> > '), ('- ', '  '), ('> - ', '>   ')))
    def test_container_fenced_examples_do_not_supply_startup_connections(self, prefix, continuation):
        paths = ('harness/common/START.md', 'harness/project/START.md', '.claude/rules/',
                 'harness/common/INDEX.md', 'harness/project/INDEX.md')
        examples = ''.join(continuation + f'[Example]({p})\n' for p in paths)
        text = prefix + '~~~md\n' + examples + continuation + '~~~~\n'
        agents = self.root / 'AGENTS.md'
        agents.write_text(text)
        result = self.run_check()
        assert result.returncode == 0, result.stderr
        assert agents.read_text().startswith(text)
        for path in paths:
            assert f']({path})' in agents.read_text()[len(text):]

    def test_unclosed_quote_fence_refuses_without_autoclosing(self):
        agents = self.root / 'AGENTS.md'
        original = b'> ~~~md\n> [Example](harness/common/START.md)\n'
        agents.write_bytes(original)
        result = self.run_check()
        assert result.returncode == 2, result.stderr
        assert 'Unclosed Markdown code fence' in result.stderr
        assert agents.read_bytes() == original
        assert not (self.root / 'CLAUDE.md').exists()

    @pytest.mark.parametrize('folder', ('harness/common/rules', '.claude/rules'))
    def test_unreadable_nested_rule_directory_refuses_before_repairs(self, folder):
        private = self.root / folder / 'private'
        private.mkdir()
        (private / 'local.md').write_bytes(b'# Private rule\n')
        private.chmod(0)
        try:
            result = self.run_check()
            assert result.returncode == 2, result.stderr
            assert not (self.root / 'AGENTS.md').exists()
            assert not (self.root / 'CLAUDE.md').exists()
        finally:
            private.chmod(0o700)

    @pytest.mark.parametrize('prefix', ('- > ', '- - '))
    def test_unsupported_recursive_container_fence_refuses_without_writes(self, prefix):
        agents = self.root / 'AGENTS.md'
        original = (prefix + '~~~md\n    [Example](harness/common/START.md)\n').encode()
        agents.write_bytes(original)
        result = self.run_check()
        assert result.returncode == 2, result.stderr
        assert 'Unsupported nested Markdown fence' in result.stderr
        assert agents.read_bytes() == original
        assert not (self.root / 'CLAUDE.md').exists()
