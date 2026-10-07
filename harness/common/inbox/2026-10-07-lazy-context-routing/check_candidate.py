"""Check startup reduction, local routing resources and installable copies."""
import argparse
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent


def check(root):
    baseline = json.loads((HERE / 'baseline.json').read_text())
    old = sum(v['chars'] for k, v in baseline.items() if '/rules/' in k)
    rules = list((root / 'harness/common/rules').glob('comm-*.md'))
    current = sum(len(p.read_text()) for p in rules)
    assert current < old, f'Unchanged startup: {current} >= {old}'
    for p in rules:
        assert p.read_bytes() == (root / '.claude/rules' / p.name).read_bytes(), p
        for relative in re.findall(r'`(harness/[^`]+\.md)`', p.read_text()):
            assert (root / relative).is_file(), relative
    for name, resource in [('comm-process-harness-inbox', 'workflow.md'),
                           ('comm-install-harness', 'checks.md'),
                           ('comm-create-lazy-claude-codex-skills', 'content-contract.md')]:
        source = root / 'harness/common/skills' / name
        assert (source / 'SKILL.md').is_file(), name
        assert (source / 'references' / resource).is_file(), name
        files = {p.relative_to(source): p for p in source.rglob('*') if p.is_file()}
        for native in ['.agents/skills', '.claude/skills']:
            mirror = root / native / name
            assert set(files) == {p.relative_to(mirror) for p in mirror.rglob('*') if p.is_file()}, name
            for relative, p in files.items():
                assert not p.is_symlink() and not (mirror / relative).is_symlink(), p
                if p.name != 'README.human.md':
                    assert p.read_bytes() == (mirror / relative).read_bytes(), p
        for p in source.rglob('*.md'):
            if p.name == 'README.human.md':
                continue
            for link in re.findall(r'\[[^\]]+\]\(([^)]+)\)', p.read_text()):
                if not link.startswith(('https://', 'http://', '#')):
                    assert (p.parent / link.split('#')[0]).is_file(), (p, link)
    return {'baseline_rule_chars': old, 'candidate_rule_chars': current,
            'reduction_percent': round(100 * (old - current) / old, 1)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    print(json.dumps(check(args.root), ensure_ascii=False))
