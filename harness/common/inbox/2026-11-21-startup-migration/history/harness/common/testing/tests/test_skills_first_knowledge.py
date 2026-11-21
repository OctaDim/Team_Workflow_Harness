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
            for target in re.findall(r'\[[^\]]*\]\(([^)#]+)(?:#[^)]*)?\)', text):
                if '://' not in target:
                    path = entry.parent / relative.parent / target
                    assert path.exists(), (entry.parent.name, relative, target)
            for target in re.findall(r'`(harness/[^`\s]+\.(?:md|py|mjs|json))`', text):
                assert (ROOT / target).is_file(), (entry.parent.name, relative, target)


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
