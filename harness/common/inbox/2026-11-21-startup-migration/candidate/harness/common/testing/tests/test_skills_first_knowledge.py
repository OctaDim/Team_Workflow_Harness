"""Structural integrity only: native behavior is checked in fresh CLI sessions."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[4]


def test_active_skill_resources_and_native_copies_are_complete():
    common = ROOT / 'harness/common'
    sources = sorted((common / 'skills').glob('comm-*/SKILL.md'))
    assert sources, 'An empty selection proves nothing'
    for entry in sources:
        files = {p.relative_to(entry.parent): p.read_bytes()
                 for p in entry.parent.rglob('*') if p.is_file()}
        for native in ['.agents/skills', '.claude/skills']:
            folder = ROOT / native / entry.parent.name
            assert all(not p.is_symlink() for p in [folder, *folder.rglob('*')])
            copies = {p.relative_to(folder): p.read_bytes()
                      for p in folder.rglob('*') if p.is_file()}
            assert copies == files, (entry.parent.name, native)
        for relative, data in files.items():
            if relative.suffix != '.md' or relative.name == 'README.human.md':
                continue
            text = data.decode('utf-8')
            assert not re.search(r'(?:harness/(?:common|project)/|\.\./)lessons/', text)
            local_links = [target for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text)
                           if '://' not in target and not target.startswith('#')]
            assert not local_links, (entry, relative, local_links)
            for target in re.findall(r'`(harness/[^`\s]+\.(?:md|py|mjs|json))`', text):
                assert (ROOT / target).is_file(), (entry.parent.name, relative, target)


def test_internal_paths_from_actual_installation_copies():
    root_paths = re.compile(r'`((?:harness/(?:common|project)/[^\s`{}*]+\.(?:md|py|json|mjs|template)|\.claude/rules))`')
    for package in ('common', 'project'):
        base = ROOT / 'harness' / package
        for category in ('rules', 'skills'):
            for source in (base / category).rglob('*.md'):
                relative = source.relative_to(base / category)
                if category == 'rules' and source.name == 'README.human.md':
                    continue
                if relative.parts == ('README.human.md',):
                    continue
                natives = ('.claude',) if category == 'rules' else ('.agents', '.claude')
                for file in [source, *(ROOT / client / category / relative for client in natives)]:
                    assert file.read_bytes() == source.read_bytes(), file
                    text = file.read_text()
                    for path in root_paths.findall(text):
                        target = ROOT / path
                        assert target.is_dir() if path == '.claude/rules' else target.is_file(), (file, path)
                    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
                        assert '://' in target or target.startswith('#'), (file, target)

    for entry in [ROOT / 'AGENTS.md', ROOT / 'harness/common/base/AGENTS.template']:
        assert root_paths.findall(entry.read_text()) == ['.claude/rules']
    assert (ROOT / '.claude/rules').is_dir()


def test_active_maps_and_approved_template_have_no_lessons():
    common = ROOT / 'harness/common'
    categories = json.loads((common / 'base/project-skeleton.json').read_text())['categories']
    assert 'lessons' not in categories
    assert 'plans' not in categories
    assert 'docs/plans' in categories
    for package in ['common', 'project']:
        folder = ROOT / 'harness' / package
        assert not (folder / 'lessons').exists()
        text = (folder / 'INDEX.md').read_text()
        assert '(lessons)' not in text
        assert (folder / 'docs/plans').is_dir()
        for file in (folder / 'rules').glob('*.md'):
            if file.name != 'README.human.md':
                assert not re.search(r'harness/(?:common|project)/lessons/', file.read_text())
