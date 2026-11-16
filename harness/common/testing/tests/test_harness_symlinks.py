"""Reject linked inputs before traversal, execution, reading or mutation."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

COMMON = Path(__file__).absolute().parents[2]


@pytest.fixture
def installation(tmp_path):
    root = tmp_path / 'installation'
    for relative in ('checks', 'scripts'):
        shutil.copytree(COMMON / relative, root / 'harness/common' / relative)
    for relative in ('harness/common/rules', '.claude/rules'):
        folder = root / relative
        folder.mkdir(parents=True)
        (folder / 'comm-fixture.md').write_text('# Fixture\n')
    for package in ('common', 'project'):
        folder = root / 'harness' / package
        folder.mkdir(exist_ok=True)
        for name in ('START.md', 'INDEX.md'):
            (folder / name).write_text('# Fixture\n')
    template = root / 'harness/common/base/project-skeleton.json'
    template.parent.mkdir()
    shutil.copyfile(COMMON / 'base/project-skeleton.json', template)
    (root / 'AGENTS.md').write_bytes(b'# User settings\r\n')
    return root


def python_script(root, script, *args):
    return subprocess.run([sys.executable, '-B', str(root / 'harness/common' / script),
                           *map(str, args)], cwd=root, capture_output=True, text=True)


@pytest.mark.parametrize('folder', ['common/inbox/old/candidate', 'common/testing/evidence/raw', 'project/docs'])
@pytest.mark.parametrize('target_kind', ['internal-file', 'external-file', 'directory', 'broken'])
def test_startup_rejects_every_harness_link_before_repair(installation, tmp_path, folder, target_kind):
    root = installation
    target = (root / 'harness/common/target') if target_kind == 'internal-file' else tmp_path / 'target'
    if target_kind == 'directory':
        target.mkdir()
        (target / 'data').write_bytes(b'unchanged')
    elif target_kind != 'broken':
        target.write_bytes(b'unchanged')
    link = root / 'harness' / folder / 'alias'
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(target, target_is_directory=target_kind == 'directory')
    before = (root / 'AGENTS.md').read_bytes()
    result = python_script(root, 'checks/ensure_entrypoint_links.py')
    assert result.returncode == 2, result.stdout + result.stderr
    assert str(link) in result.stderr
    assert (root / 'AGENTS.md').read_bytes() == before
    assert not (root / 'CLAUDE.md').exists()
    assert link.is_symlink()
    if target_kind != 'broken':
        assert (target / 'data' if target_kind == 'directory' else target).read_bytes() == b'unchanged'


@pytest.mark.parametrize('script', ['scripts/run_tests.py', 'checks/check_human_guide_search.py'])
def test_python_tools_reject_tree_link_before_running_work(installation, script):
    root = installation
    link = root / 'harness/project/broken'
    link.symlink_to(root / 'missing')
    args = ['missing-rule', '--output', 'report.json'] if script.startswith('checks/') else []
    result = python_script(root, script, *args)
    assert result.returncode != 0
    assert str(link) in result.stderr
    assert not (root / 'report.json').exists()


@pytest.mark.parametrize('which', ['rule', 'output', 'output-parent'])
def test_native_check_rejects_linked_inputs_and_outputs_before_probe(installation, tmp_path, which):
    root = installation
    rule = root / 'rule.md'
    rule.write_text('# Fixture\n')
    output = root / 'report.json'
    target = tmp_path / 'preserved'
    target.write_bytes(b'unchanged')
    if which == 'rule':
        rule.unlink()
        rule.symlink_to(target)
        link = rule
    elif which == 'output':
        output.symlink_to(target)
        link = output
    else:
        link = root / 'linked-parent'
        link.symlink_to(tmp_path, target_is_directory=True)
        output = link / 'report.json'
    result = python_script(root, 'checks/check_human_guide_search.py', rule, '--output', output)
    assert result.returncode != 0
    assert str(link) in result.stderr
    assert target.read_bytes() == b'unchanged'
    assert not (tmp_path / 'report.json').exists()
    assert 'bwrap' not in result.stderr


@pytest.mark.parametrize('operation', ['readFile', 'readdir', 'open', 'stat', 'import'])
@pytest.mark.parametrize('target_kind', ['file', 'directory', 'broken'])
def test_node_tool_rejects_links_before_access(installation, tmp_path, operation, target_kind):
    root = installation
    marker = tmp_path / 'executed'
    target = tmp_path / 'target.mjs'
    body = "import fs from 'node:fs'; fs.writeFileSync(" + json.dumps(str(marker)) + ", 'executed');\n"
    if target_kind == 'directory':
        target.mkdir()
        (target / 'data').write_text('private-data')
    elif target_kind == 'file':
        target.write_text(body)
    link = root / 'alias.mjs'
    link.symlink_to(target, target_is_directory=target_kind == 'directory')
    probe = root / 'probe.mjs'
    probe.write_text("import fs from 'node:fs/promises'; await fs." + operation + '(' + json.dumps(str(link)) + ");\n")
    cli = link if operation == 'import' else probe
    result = subprocess.run(['node', str(root / 'harness/common/scripts/plugin_eval_without_human.mjs'), str(cli)],
                            cwd=root, capture_output=True, text=True)
    assert result.returncode != 0
    assert 'Symlink' in result.stderr and str(link) in result.stderr
    assert not marker.exists()
    assert link.is_symlink()
    if target_kind == 'file':
        assert target.read_text() == body


def test_node_tool_rejects_linked_ancestor_even_before_dotdot(installation, tmp_path):
    root = installation
    link = root / 'alias'
    link.symlink_to(tmp_path, target_is_directory=True)
    probe = root / 'probe.mjs'
    probe.write_text('console.log("EXECUTED");\n')
    lexical = str(link) + '/../probe.mjs'
    result = subprocess.run(['node', str(root / 'harness/common/scripts/plugin_eval_without_human.mjs'), lexical],
                            cwd=root, capture_output=True, text=True)
    assert result.returncode != 0
    assert str(link) in result.stderr
    assert 'EXECUTED' not in result.stdout


@pytest.mark.parametrize('dotdot', [False, True])
@pytest.mark.parametrize('leading_hyphen', [False, True])
def test_installed_analyzer_rejects_original_target_before_normalizing(installation, tmp_path, dotdot, leading_hyphen):
    root = installation
    skill = tmp_path / 'skill'
    skill.mkdir()
    (skill / 'SKILL.md').write_text('---\nname: fixture\ndescription: Use for test fixture tasks.\n---\nReport the result.\n')
    target = tmp_path / 'outside'
    target.mkdir()
    link = tmp_path / ('-alias' if leading_hyphen else 'alias')
    link.symlink_to(target, target_is_directory=True)
    raw = link.name if leading_hyphen else str(link)
    original = raw + '/../skill' if dotdot else raw
    cli = Path(shutil.which('plugin-eval')).resolve()
    result = subprocess.run(['node', str(root / 'harness/common/scripts/plugin_eval_without_human.mjs'),
                             str(cli), 'analyze', original, '--format', 'json'],
                            cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode != 0
    assert 'Symlink forbidden' in result.stderr and str(link) in result.stderr
    assert not result.stdout.strip()


@pytest.mark.parametrize('environment_key', ['TMPDIR', 'CODEX_HOME'])
def test_native_check_rejects_linked_runtime_directories_before_writes(installation, tmp_path, environment_key):
    import os
    root = installation
    target = tmp_path / 'external-runtime'
    target.mkdir()
    link = tmp_path / 'runtime-alias'
    link.symlink_to(target, target_is_directory=True)
    rule = root / 'rule.md'
    rule.write_text('# Fixture\n')
    tools = tmp_path / 'tools'
    tools.mkdir()
    # Stop at the subprocess boundary if a missing guard would otherwise run native agents.
    stub = tools / 'bwrap'
    stub.write_text('#!/bin/sh\nexit 1\n')
    stub.chmod(0o755)
    environment = dict(os.environ, PATH=str(tools), **{environment_key: str(link)})
    result = subprocess.run([sys.executable, '-B', str(root / 'harness/common/checks/check_human_guide_search.py'),
                             str(rule), '--output', str(root / 'report.json')],
                            cwd=root, env=environment, capture_output=True, text=True)
    assert result.returncode != 0
    assert 'Symlink forbidden' in result.stderr and str(link) in result.stderr
    assert not list(target.iterdir())
    assert link.is_symlink()


def test_temp_directory_probe_does_not_write_through_link(installation, tmp_path, monkeypatch):
    import os
    import runpy
    import tempfile
    root = installation
    target = tmp_path / 'temp-target'
    target.mkdir()
    link = tmp_path / 'temp-alias'
    link.symlink_to(target, target_is_directory=True)
    rule = root / 'rule.md'
    rule.write_text('# Fixture\n')
    module = runpy.run_path(str(root / 'harness/common/checks/check_human_guide_search.py'))
    monkeypatch.setenv('TMPDIR', str(link))
    monkeypatch.setattr(tempfile, 'tempdir', None)
    monkeypatch.setattr(sys, 'argv', ['check', str(rule), '--output', str(root / 'report.json')])
    attempts = []
    original_open = os.open

    def record_open(file, *args, **kwargs):
        if str(file).startswith(str(link) + os.sep):
            attempts.append(file)
        return original_open(file, *args, **kwargs)

    monkeypatch.setattr(os, 'open', record_open)
    with pytest.raises(ValueError, match='Symlink forbidden'):
        module['main']()
    assert attempts == [], 'Even transient write probes must not follow TMPDIR links'
    assert not list(target.iterdir())
