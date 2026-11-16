"""Local-only checks; no model/provider calls and no publication."""
import importlib.util
import json
from pathlib import Path
import tempfile

OUT = Path(__file__).absolute().parent
spec = importlib.util.spec_from_file_location('sequential_probe', OUT / 'validate.py')
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def main():
    helpers = probe.helpers
    repo = probe.REPO
    versions = {}
    for command in (['codex', '--version'], ['claude', '--version'], ['node', '--version'],
                    ['uv', '--version'], ['python3', '--version'], ['claude', 'auth', 'status']):
        versions[' '.join(command)] = helpers.run(command, timeout=45)
    probe.save('local-tool-status.json', versions)
    installations = []
    for variant in ('pair', 'lazy'):
        for mode in ('common', 'both'):
            with tempfile.TemporaryDirectory(prefix='lazy-commit-install-') as directory:
                root = Path(directory)
                startup = probe.prepare(root, mode, variant)
                sources = sorted(p.name for p in (root/'harness/common/rules').glob('comm-*.md'))
                copies = sorted(p.name for p in (root/'.claude/rules').glob('comm-*.md'))
                assert sources == copies
                for name in sources:
                    assert (root/'harness/common/rules'/name).read_bytes() == (root/'.claude/rules'/name).read_bytes()
                assert (probe.RULE in sources) == (variant == 'pair')
                skill = root/'harness/common/skills'/probe.NAME
                for native in ('.agents/skills', '.claude/skills'):
                    assert helpers.snapshot(skill) == helpers.snapshot(root/native/probe.NAME)
                stats = {
                    'rules_utf8_bytes': sum(p.stat().st_size for p in (root/'.claude/rules').glob('*.md') if p.name!='README.human.md'),
                    'skill_metadata_utf8_bytes': sum(len(p.read_text().split('---', 2)[1].encode())
                        for p in (root/'.agents/skills').glob('*/SKILL.md')),
                    'target_available_machine_bytes': (skill/'SKILL.md').stat().st_size,
                    'actual_task_reads': None,
                    'actual_task_reads_reason': 'Native provider connection blocked; not a zero cost.',
                }
                damaged = root/'.claude/rules'/sources[0]
                damaged.unlink()
                before = helpers.snapshot(root)
                negative = helpers.run(['python3', '-B', 'harness/common/checks/ensure_entrypoint_links.py'], cwd=root)
                assert negative['exit_code'] != 0 and helpers.snapshot(root) == before
                installations.append({'variant':variant, 'mode':mode, 'startup':startup,
                    'repeat_unchanged':True, 'neutral_or_preserved_project':True,
                    'canonical_rule_count':len(sources), 'native_rules_equal':True,
                    'skill_copies_equal':True, 'missing_rule_refused_without_write':negative,
                    'context_static':stats})
    with tempfile.TemporaryDirectory(prefix='lazy-commit-project-only-') as directory:
        root = Path(directory)
        (root/'harness/project').mkdir(parents=True)
        before = helpers.snapshot(root)
        result = helpers.run(['python3', '-B', str(repo/'harness/common/checks/ensure_entrypoint_links.py')], cwd=root)
        assert result['exit_code'] != 0 and helpers.snapshot(root) == before
        installations.append({'mode':'project-only','refused_without_write':True,'result':result})
    probe.save('local-installations.json', installations)
    creator = Path('/home/octadim/.codex/skills/.system/skill-creator/scripts/quick_validate.py')
    skill = repo/'harness/common/inbox/2026-10-19-sequential-rule-to-lazy-skills/candidate-v0/skills'/probe.NAME
    result = helpers.run(['python3', str(creator), str(skill)])
    probe.save('local-quick-validate-v0.json', result)
    assert result['exit_code'] == 0, result
    entry = Path('/home/octadim/.codex/plugins/cache/openai-curated-remote/plugin-eval/0.1.2/scripts/plugin-eval.js')
    helpers.ordinary(entry)
    launcher = repo/'harness/common/scripts/plugin_eval_without_human.mjs'
    for label, target in (('skill',skill), ('rule',skill.parents[1]/'rules')):
        for action in ('start','analyze'):
            result = helpers.run(['node', str(launcher), str(entry), action, str(target), '--format','json'])
            probe.save(f'local-{label}-{action}-v0.json', result)
            assert result['exit_code'] == 0, result
    regression = helpers.run([str(repo/'.venv/bin/python'), '-B','-m','pytest','-q'], timeout=180)
    probe.save('local-regression.json', regression)
    assert regression['exit_code'] == 0, regression
    print(json.dumps({'installations':4,'project_only_refused':True,'quick_validate':'passed',
        'plugin_eval':'completed; see reports','pytest':regression['stdout'].strip().splitlines()[-1]},ensure_ascii=False))


if __name__ == '__main__':
    main()
