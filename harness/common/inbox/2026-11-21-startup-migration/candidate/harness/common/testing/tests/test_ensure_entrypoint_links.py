"""Check protected inputs, published rule/skill packages and project creation."""
import json
import os
from pathlib import Path
import shutil

import pytest


def snapshot(directory):
    return {p.relative_to(directory): p.read_bytes() for p in directory.rglob('*') if p.is_file()}


def test_neutral_project_uses_template_and_repeat_preserves_every_file(published, startup):
    result = startup(published)
    assert result.returncode == 3, result.stderr
    project = published / 'harness/project'
    common = published / 'harness/common'
    template = json.loads((common / 'base/project-skeleton.json').read_bytes())['categories']
    index = (project / 'INDEX.md').read_text()
    for name in template:
        folder = project / name
        assert (folder / 'README.human.md').is_file()
        assert f'[{folder.name}]({name})' in index
    for parent in (project, *(p for p in project.rglob('*') if p.is_dir())):
        assert (parent / 'README.human.md').is_file()
    for excluded in ('START.md', 'lessons', 'checks/ensure_entrypoint_links.py'):
        assert not (project / excluded).exists()
    assert not (published / '.claude/rules/README.human.md').exists()
    for name in ('AGENTS', 'CLAUDE'):
        assert (published / (name + '.md')).read_bytes() == (common / 'base' / (name + '.template')).read_bytes()
    before = {p: p.stat().st_mtime_ns for p in published.rglob('*')}
    assert startup(published).returncode == 0
    assert before == {p: p.stat().st_mtime_ns for p in published.rglob('*')}


def test_removed_project_recreated_without_old_records(installed, startup):
    project = installed / 'harness/project'
    skeleton = snapshot(project)
    (project / 'testing/evidence/work/old-run.log').write_bytes(b'old result\n')
    shutil.rmtree(project)
    assert startup(installed).returncode == 3
    assert snapshot(project) == skeleton


def test_new_template_applies_only_when_project_missing(published, startup):
    project = published / 'harness/project'
    (project / 'lessons').mkdir(parents=True)
    (project / 'lessons/old.md').write_bytes(b'Keep existing project\r\n')
    (project / 'INDEX.md').write_text('# Local project')
    before = snapshot(project)
    template = published / 'harness/common/base/project-skeleton.json'
    data = json.loads(template.read_bytes())
    data['categories']['local'] = {'purpose': 'Local data', 'example': 'example.md'}
    template.write_text(json.dumps(data))
    assert startup(published).returncode == 3
    assert snapshot(project) == before
    shutil.rmtree(project)
    assert startup(published).returncode == 3
    assert (project / 'local/README.human.md').is_file()


@pytest.mark.parametrize('content', ('not json', '{}', '{"categories":{"../bad":{"purpose":"p","example":"e"}}}'))
def test_invalid_template_prevents_all_repairs(published, startup, content):
    source = published / 'harness/common/base/project-skeleton.json'
    source.write_text(content)
    before = snapshot(published)
    result = startup(published)
    assert result.returncode == 2 and str(source) in result.stderr
    assert before == snapshot(published)
    assert not (published / 'harness/project').exists()


@pytest.mark.parametrize('package', ['common', 'project'])
@pytest.mark.parametrize('contents', [None, b'', b' \r\n', b'\xff'])
def test_missing_or_invalid_map_stops_before_creating_inputs(published, startup, package, contents):
    project = published / 'harness/project'
    project.mkdir()
    (project / 'INDEX.md').write_text('# Local map')
    path = published / 'harness' / package / 'INDEX.md'
    if contents is None:
        path.unlink()
    else:
        path.write_bytes(contents)
    before = snapshot(published)
    result = startup(published)
    assert result.returncode == 2 and str(path) in result.stderr
    assert before == snapshot(published)


@pytest.mark.parametrize(('name', 'data'), [
    ('AGENTS.md', b''), ('AGENTS.md', b'\xff'), ('AGENTS.md', b'Keep extra settings\r\n'),
    ('AGENTS.md', b'```\n[rules](/.claude/rules)\n'), ('CLAUDE.md', b'@AGENTS.md\r\n'),
    ('CLAUDE.md', b' '),
])
def test_different_existing_input_blocks_before_any_write(published, startup, name, data):
    (published / name).write_bytes(data)
    before = snapshot(published)
    result = startup(published)
    assert result.returncode == 2 and name in result.stderr
    assert 'INBOX' in result.stderr
    assert before == snapshot(published)
    assert not (published / 'harness/project').exists()


@pytest.mark.parametrize(('target', 'data'), [
    ('base/AGENTS.template', b''), ('base/AGENTS.template', b'\xff'), ('base/CLAUDE.template', b'\n'),
    ('rules/comm-fixture.md', b' \n'), ('rules/comm-fixture.md', b'\xff'),
    ('skills/comm-example/SKILL.md', b' \n'), ('skills/comm-example/SKILL.md', b'\xff'),
])
def test_invalid_canonical_source_rejects_before_repair(published, startup, target, data):
    path = published / 'harness/common' / target
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    before = snapshot(published)
    result = startup(published)
    assert result.returncode == 2 and str(path) in result.stderr
    assert before == snapshot(published)


@pytest.mark.parametrize('relative', ['.claude','.claude/rules','harness/project','AGENTS.md','CLAUDE.md'])
def test_symlinked_paths_rejected_before_repairs(published, startup, relative):
    outside = published.parent / 'outside'
    outside.write_bytes(b'Keep this file')
    path = published / relative
    path.parent.mkdir(exist_ok=True)
    path.symlink_to(outside)
    result = startup(published)
    assert result.returncode == 2 and str(path) in result.stderr
    assert path.is_symlink() and outside.read_bytes() == b'Keep this file'
    assert not (published / '.agents').exists()


@pytest.mark.parametrize('folder', ['harness/common/rules', '.claude/rules'])
def test_unreadable_nested_directory_is_reported(published, startup, folder):
    private = published / folder / 'nested'
    private.mkdir(parents=True)
    private.chmod(0)
    try:
        if not os.access(private, os.R_OK):
            result = startup(published)
            assert result.returncode == 2 and str(private) in result.stderr
            assert not (published / 'AGENTS.md').exists()
        else:
            pytest.skip('Current account can traverse mode 000 directories')
    finally:
        private.chmod(0o700)


@pytest.mark.parametrize('name', ['team.md', 'nested/team.md', 'README.human.md', 'comm-stale.md'])
def test_unknown_native_markdown_blocks_recovery(installed, startup, name):
    native = installed / '.claude/rules'
    (native / 'comm-fixture.md').unlink()
    path = native / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b'Keep\n')
    result = startup(installed)
    assert result.returncode == 2 and str(path) in result.stderr
    assert path.read_bytes() == b'Keep\n' and not (native / 'comm-fixture.md').exists()


def test_nested_rule_and_skill_resources_recover_only_from_packages(published, startup):
    common = published / 'harness/common'
    project = published / 'harness/project'
    project.mkdir()
    (project / 'INDEX.md').write_text('# Local project')
    for package, prefix in ((common, 'comm'), (project, 'proj')):
        rule = package / 'rules/sub' / f'{prefix}-test.md'
        rule.parent.mkdir(parents=True)
        rule.write_bytes(b'Published canonical rule\r\n')
        skill = package / 'skills' / f'{prefix}-test'
        (skill / 'references/sub').mkdir(parents=True)
        (skill / 'SKILL.md').write_bytes(b'# Body\n')
        (skill / 'references/sub/resource.bin').write_bytes(b'\x00\xff')
        (skill / 'README.human.md').write_bytes(b'Human resource\r\n')
    assert startup(published).returncode == 3
    for package, prefix in ((common, 'comm'), (project, 'proj')):
        relative = Path('sub') / f'{prefix}-test.md'
        target = published / '.claude/rules' / relative
        assert target.read_bytes() == (package / 'rules' / relative).read_bytes()
        target.unlink()
        decoy = package / 'inbox/unpublished/rules' / relative
        decoy.parent.mkdir(parents=True)
        decoy.write_bytes(b'Unpublished')
        for client in ('.claude/skills', '.agents/skills'):
            source = package / 'skills' / f'{prefix}-test'
            mirror = published / client / source.name
            assert snapshot(mirror) == snapshot(source)
            (mirror / 'references/sub/resource.bin').write_bytes(b'damaged')
    assert startup(published).returncode == 3
    assert startup(published).returncode == 0
    for package, prefix in ((common, 'comm'), (project, 'proj')):
        key = Path('sub') / f'{prefix}-test.md'
        assert (published / '.claude/rules' / key).read_bytes() == (package / 'rules' / key).read_bytes()
        for client in ('.claude/skills', '.agents/skills'):
            assert snapshot(published / client / f'{prefix}-test') == snapshot(package / 'skills' / f'{prefix}-test')


def test_publication_journal_blocks_startup_without_writes(published, startup):
    marker = published / '.harness-publication.json'
    marker.write_bytes(b'{"pending":true}')
    before = snapshot(published)
    result = startup(published)
    assert result.returncode == 2 and str(marker) in result.stderr
    assert before == snapshot(published)


@pytest.mark.skipif(os.name != 'posix', reason='POSIX flock integration test')
def test_busy_root_stops_before_work_and_clean_retry_succeeds(published, startup):
    import fcntl
    fd = os.open(published, os.O_RDONLY | os.O_DIRECTORY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        result = startup(published)
        assert result.returncode == 2 and 'busy' in result.stderr
        assert not (published / 'harness/project').exists()
        assert not (published / 'AGENTS.md').exists()
    finally:
        os.close(fd)
    assert startup(published).returncode == 3
