"""Final local SQL candidate installation and regression checks, serial only."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import json

OUT = Path(__file__).absolute().parent
spec = importlib.util.spec_from_file_location('sql_probe', OUT / 'validate_sql.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def main():
    records = []
    for variant in ('pair', 'candidate'):
        for mode in ('common', 'both'):
            with tempfile.TemporaryDirectory(prefix='sql-final-install-') as directory:
                root = Path(directory)
                startup = m.prepare(root, mode, variant)
                source = root / 'harness/common/skills' / m.NAME
                current = m.base.helpers.snapshot(source)
                for parent in ('.agents/skills', '.claude/skills'):
                    assert m.base.helpers.snapshot(root / parent / m.NAME) == current
                sources = {p.name:p.read_bytes() for p in (root/'harness/common/rules').glob('comm-*.md')}
                native = {p.name:p.read_bytes() for p in (root/'.claude/rules').glob('comm-*.md')}
                assert sources == native
                assert (m.RULE in sources) == (variant == 'pair')
                stat = {
                    'rules_utf8_bytes':sum(len(value) for value in sources.values()),
                    'metadata_utf8_bytes':sum(len(p.read_text().split('---',2)[1].encode())
                        for p in (root/'.agents/skills').glob('*/SKILL.md')),
                    'target_machine_resources':[
                        {'path':str(p.relative_to(source)),'bytes':p.stat().st_size}
                        for p in sorted(source.rglob('*')) if p.is_file() and p.name!='README.human.md'],
                }
                regression = None
                if variant == 'candidate':
                    shutil.copyfile(m.REPO/'pytest.ini',root/'pytest.ini')
                    m.base.git(root,'init','-q','-b','main')
                    regression = m.base.helpers.run([str(m.REPO/'.venv/bin/python'),'-B','-m','pytest','-q'],cwd=root,timeout=180)
                    m.save(f'v1-{mode}-candidate-regression.json',regression)
                    assert regression['exit_code']==0,regression
                resource=root/'.agents/skills'/m.NAME/'references/choices.md'
                resource.unlink()
                assert m.base.helpers.snapshot(root/'.agents/skills'/m.NAME)!=current
                damaged=root/'.claude/rules'/sorted(sources)[0]
                damaged.unlink()
                before=m.base.helpers.snapshot(root)
                negative=m.base.helpers.run(['python3','-B','harness/common/checks/ensure_entrypoint_links.py'],cwd=root)
                assert negative['exit_code']!=0 and m.base.helpers.snapshot(root)==before
                records.append({'variant':variant,'mode':mode,'startup':startup,'equal_rule_count':len(sources),
                    'full_skill_copies_equal':True,'resource_copy_damage_detected':True,
                    'missing_rule_refused_without_write':negative,'context_static':stat})
                print(json.dumps({'variant':variant,'mode':mode,'structural':'passed',
                    'pytest':regression['stdout'].strip().splitlines()[-1] if regression else 'N/A: baseline structure only'},ensure_ascii=False),flush=True)
    with tempfile.TemporaryDirectory(prefix='sql-project-only-') as directory:
        root=Path(directory);(root/'harness/project').mkdir(parents=True)
        before=m.base.helpers.snapshot(root)
        negative=m.base.helpers.run(['python3','-B',str(m.REPO/'harness/common/checks/ensure_entrypoint_links.py')],cwd=root)
        assert negative['exit_code']!=0 and m.base.helpers.snapshot(root)==before
        records.append({'mode':'project-only','refused_without_write':True,'result':negative})
    m.save('v1-final-installations.json',records)


if __name__=='__main__':
    main()
