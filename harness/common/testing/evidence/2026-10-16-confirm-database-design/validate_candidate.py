"""Repeat current candidate checks; append tagged evidence, never overwrite logs."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

import yaml
import native_validation as native

EVIDENCE = Path(__file__).absolute().parent
ENTRY = '/home/octadim/.codex/plugins/cache/openai-curated-remote/plugin-eval/0.1.2/scripts/plugin-eval.js'
WRAPPER = 'harness/common/scripts/plugin_eval_without_human.mjs'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('tag')
    tag = parser.parse_args().tag
    if not tag.replace('-', '').isalnum():
        raise ValueError('Tag must contain letters, numbers or hyphens')

    def run(label, command):
        result = subprocess.run(command, cwd=native.REPO, capture_output=True, text=True)
        native.save(EVIDENCE / f'{tag}-{label}.json', dict(
            command=command, exit=result.returncode, stdout=result.stdout, stderr=result.stderr))
        if result.returncode:
            raise RuntimeError(f'{label}: {result.stderr}')
        print(label, 'passed', flush=True)
        return result.stdout

    def analyze(label, target):
        for action in ('start', 'analyze'):
            output = run(f'{label}-{action}', ['node', WRAPPER, ENTRY, action, str(target), '--format', 'json'])
        parsed = json.loads(output)
        native.save(EVIDENCE / f'{tag}-{label}-evaluation.json', parsed)
        if 'improvementBrief' in parsed:
            native.save(EVIDENCE / f'{tag}-{label}-brief.json', parsed['improvementBrief'])
        return parsed

    native.ordinary(native.REPO / 'harness')
    native.ordinary(Path(ENTRY))
    candidate = native.REQUEST / native.NAME
    native.save(EVIDENCE / f'{tag}-candidate-hashes.json', dict(
        skill=native.snapshot(candidate),
        rule=hashlib.sha256((native.REQUEST / f'{native.NAME}.md').read_bytes()).hexdigest()))
    run('profile', ['python3', '/home/octadim/.codex/skills/.system/skill-creator/scripts/quick_validate.py', str(candidate)])
    analyze('skill', candidate)
    run('comparison', ['node', WRAPPER, ENTRY, 'compare', str(EVIDENCE / 'initial-evaluation.json'),
                       str(EVIDENCE / f'{tag}-skill-evaluation.json'), '--format', 'json'])
    with tempfile.TemporaryDirectory(prefix='db-rule-check-') as directory:
        target = Path(directory)
        (target / 'README.human.md').write_text('# Rule evaluation\n\nExample: evaluate one candidate rule.\n')
        shutil.copyfile(native.REQUEST / f'{native.NAME}.md', target / f'{native.NAME}.md')
        analyze('rule', target)

    results = []
    for mode in ('common', 'both'):
        for phase in ('baseline', 'candidate'):
            with tempfile.TemporaryDirectory(prefix='db-final-check-') as directory:
                root = Path(directory) / 'fixture'
                root.mkdir()
                startup = native.prepare(root, mode, phase)
                before = native.snapshot(root)
                check = ['python3', '-B', 'harness/common/checks/ensure_entrypoint_links.py']
                result = subprocess.run(check, cwd=root, capture_output=True, text=True)
                assert result.returncode == 0 and native.snapshot(root) == before
                paths = [root / 'AGENTS.md', root / 'harness/common/START.md', root / 'harness/project/START.md',
                         *sorted((root / '.claude/rules').rglob('*.md')),
                         root / 'harness/common/INDEX.md', root / 'harness/project/INDEX.md']
                target = Path(directory) / 'startup-budget'
                target.mkdir()
                (target / 'README.human.md').write_text('# Startup measurement\n\nExample: mandatory reads and catalog metadata.\n')
                inventory = []
                for index, path in enumerate(paths):
                    if path.name == 'README.human.md':
                        continue
                    data = path.read_bytes()
                    (target / f'{index:03d}.md').write_bytes(data)
                    inventory.append(dict(path=str(path.relative_to(root)), sha256=hashlib.sha256(data).hexdigest()))
                metadata = []
                for path in sorted((root / '.agents/skills').glob('*/SKILL.md')):
                    front = yaml.safe_load(path.read_text().split('---', 2)[1])
                    metadata.append(f"{front['name']}: {front['description']}")
                (target / 'metadata.md').write_text('\n'.join(metadata))
                analyze(f'startup-{mode}-{phase}', target)
                results.append(dict(mode=mode, phase=phase, startup=startup, repeated_startup_stable=True,
                                    mandatory_reads=inventory, catalog_metadata=metadata))
                if phase == 'candidate':
                    source = root / 'harness/common/skills' / native.NAME
                    assert native.snapshot(source) == native.snapshot(root / '.agents/skills' / native.NAME)
                    assert native.snapshot(source) == native.snapshot(root / '.claude/skills' / native.NAME)
                    (root / '.agents/skills' / native.NAME / 'references/choices.md').unlink()
                    assert native.snapshot(source) != native.snapshot(root / '.agents/skills' / native.NAME)
                    (root / '.claude/rules' / f'{native.NAME}.md').unlink()
                    damaged = native.snapshot(root)
                    result = subprocess.run(check, cwd=root, capture_output=True, text=True)
                    assert result.returncode != 0 and native.snapshot(root) == damaged
                    results[-1].update(resource_damage_detected_by_equality=True, rule_damage_refused=True)
    with tempfile.TemporaryDirectory(prefix='db-project-only-') as directory:
        root = Path(directory)
        (root / 'harness/project').mkdir(parents=True)
        before = native.snapshot(root)
        result = subprocess.run(['python3', '-B', str(native.REPO / 'harness/common/checks/ensure_entrypoint_links.py')],
                                cwd=root, capture_output=True, text=True)
        assert result.returncode != 0 and native.snapshot(root) == before
        results.append(dict(mode='project-only', refused_without_writes=True, stdout=result.stdout, stderr=result.stderr))
    native.save(EVIDENCE / f'{tag}-installation.json', results)
    run('tests', ['.venv/bin/python', '-m', 'pytest', '-q'])
    run('startup', ['python3', '-B', 'harness/common/checks/ensure_entrypoint_links.py'])


if __name__ == '__main__':
    main()
