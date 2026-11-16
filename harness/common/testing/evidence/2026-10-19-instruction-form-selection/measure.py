"""Measure static context and actual read receipts, without conflating usage."""
import hashlib
import json
from pathlib import Path
import re
import tempfile
import argparse

import validate


def tokens(text):
    # Same estimator as plugin-eval src/lib/tokens.js: ceil(JS string length / 4).
    units = len(text.encode('utf-16-le')) // 2
    return (units + 3) // 4


def file_record(path, root):
    data = path.read_bytes()
    return dict(path=str(path.relative_to(root)), bytes=len(data),
                sha256=hashlib.sha256(data).hexdigest(), estimated_static_tokens=tokens(data.decode()))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tag', default='v1')
    args = parser.parse_args()
    assert re.fullmatch(r'[A-Za-z0-9-]+', args.tag)
    records = []
    for mode in ('common', 'both'):
        for phase in ('baseline', 'candidate'):
            with tempfile.TemporaryDirectory(prefix='form-context-') as directory:
                root = Path(directory)
                installation = validate.prepare(root, mode, phase)
                paths = [root / 'AGENTS.md', root / 'harness/common/START.md', root / 'harness/project/START.md',
                         *sorted(p for p in (root / '.claude/rules').rglob('*.md') if p.name != 'README.human.md'),
                         root / 'harness/common/INDEX.md', root / 'harness/project/INDEX.md']
                startup = [file_record(p, root) for p in paths]
                metadata = []
                for path in sorted((root / '.agents/skills').glob('*/SKILL.md')):
                    front = path.read_text().split('---', 2)[1]
                    name = re.search(r'^name: (.*)$', front, re.M).group(1)
                    description = re.search(r'^description: (.*)$', front, re.M).group(1)
                    metadata.append(dict(name=name, description=description,
                                         estimated_static_tokens=tokens(name) + tokens(description)))
                resources = [file_record(p, root) for p in sorted((root / 'harness/common/skills' / validate.NAME).rglob('*'))
                             if p.is_file() and p.name != 'README.human.md']
                all_skills = [file_record(p, root) for p in sorted((root / 'harness/common/skills').rglob('*'))
                              if p.is_file() and p.suffix == '.md' and p.name != 'README.human.md']
                records.append(dict(mode=mode, phase=phase, installation=installation,
                                    startup_files=startup, catalog_metadata=metadata,
                                    startup_guard_tokens=sum(p['estimated_static_tokens'] for p in startup),
                                    catalog_metadata_tokens=sum(p['estimated_static_tokens'] for p in metadata),
                                    selected_owner_all_resources=resources,
                                    selected_owner_resource_tokens=sum(p['estimated_static_tokens'] for p in resources),
                                    all_common_skill_files=all_skills,
                                    all_common_skill_tokens=sum(p['estimated_static_tokens'] for p in all_skills)))
    native = []
    expected = {'.claude/rules/' + p.name: p.read_text()
                for p in (validate.REPO / '.claude/rules').glob('*.md') if p.name != 'README.human.md'}
    paths = sorted(validate.OUT.glob(f'{args.tag}-native-*.json'))
    if args.tag != 'v1':
        paths += sorted(validate.OUT.glob('v1-native-baseline-*.json'))
    for path in paths:
        raw = json.loads(path.read_text())
        commands = []
        for line in raw['stdout'].splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            item = event.get('item', {})
            if event.get('type') == 'item.completed' and item.get('type') == 'command_execution':
                commands.append(item)
        reads = [dict(command=c['command'], exit_code=c.get('exit_code'),
                      output_bytes=len(c.get('aggregated_output', '').encode()),
                      output_estimated_static_tokens=tokens(c.get('aggregated_output', '')))
                 for c in commands if 'cat ' in c.get('command', '')]
        owner = validate.CANDIDATE if raw['phase'] == 'candidate' else validate.BASELINE
        missing = [name for name, body in expected.items()
                   if not any(body in c.get('aggregated_output', '') and c.get('exit_code') == 0 for c in commands)]
        skill_body = (owner / 'SKILL.md').read_text()
        resource_body = (owner / 'references/content-contract.md').read_text()
        skill_read = any(skill_body in c.get('aggregated_output', '') for c in commands)
        resource_read = any(resource_body in c.get('aggregated_output', '') for c in commands)
        native.append(dict(file=path.name, mode=raw['mode'], phase=raw['phase'], case=raw['case'],
                           completed=raw['completed'], exit_code=raw['exit_code'],
                           complete_rule_reading=not missing, missing_rules=missing,
                           selected_skill_read=skill_read, own_resource_read=resource_read,
                           read_receipts=reads,
                           repeated_actual_read_output_bytes=sum(r['output_bytes'] for r in reads),
                           repeated_actual_read_output_estimated_tokens=sum(r['output_estimated_static_tokens'] for r in reads),
                           usage=raw['usage'],
                           changes=sorted(k for k in raw['before'].keys() | raw['after'].keys()
                                          if raw['before'].get(k) != raw['after'].get(k))))
    validate.save(f'{args.tag}-context-and-native-receipts.json', dict(
        method='plugin-eval static estimator: ceil(UTF-16 code units/4), per file/output; not billed usage',
        estimator_source='/home/octadim/.codex/plugins/cache/openai-curated-remote/plugin-eval/0.1.2/src/lib/tokens.js',
        startup_cap=None, note='No agreed startup token cap. Repeated tool outputs include complete task dependencies and repeats. '
        'CLI usage is cumulative provider-reported input/output, including cached inputs; it cannot isolate the skill cost.',
        contexts=records, native=native))
    for row in records:
        print(row['mode'], row['phase'], row['startup_guard_tokens'], row['catalog_metadata_tokens'], row['selected_owner_resource_tokens'])
    print('Native receipts:', len(native))


if __name__ == '__main__':
    main()
