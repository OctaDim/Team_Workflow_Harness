"""Execute one already reviewed inbox request; never advance a queue implicitly."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo

sys.dont_write_bytecode = True
REPO = Path('/home/octadim/MyProjects/Team_Workflow_Harness')
PYTHON = '/tmp/harness-inbox-20261113-venv/bin/python'
ENTRY = Path('/home/octadim/.codex/plugins/cache/openai-curated-remote/plugin-eval/0.1.2/scripts/plugin-eval.js')
CREATOR = Path('/home/octadim/.codex/skills/.system/skill-creator/scripts/quick_validate.py')
spec = importlib.util.spec_from_file_location('helpers', REPO/'harness/common/testing/evidence/2026-10-19-instruction-form-selection/validate.py')
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)


def now():
    return datetime.now(ZoneInfo('Europe/Minsk')).isoformat()


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def protect():
    return {str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else h.snapshot(p)
            for p in (REPO/'AGENTS.md', REPO/'CLAUDE.md', REPO/'harness/project', REPO/'.claude/rules')}


def evaluate(out, target, name, prefix):
    results = {}
    commands = [('profile', [PYTHON, str(CREATOR), str(target)])]
    for action in ('start', 'analyze', 'explain-budget'):
        commands.append((action, ['node', str(REPO/'harness/common/scripts/plugin_eval_without_human.mjs'), str(ENTRY), action, str(target), '--format', 'json']))
    for action, command in commands:
        record = h.run(command, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
        save(out/f'{prefix}-{name}-{action}.json', record)
        assert record['exit_code'] == 0, (name, action, record['stderr'])
        if action == 'analyze':
            parsed = json.loads(record['stdout'])
            save(out/f'{prefix}-{name}-brief.json', parsed.get('improvementBrief'))
            results = {'score': parsed['summary']['score'], 'grade': parsed['summary']['grade'],
                       'checks': parsed['checks'], 'budgets': parsed['budgets']}
            assert results['grade'] == 'A', results
            assert not any(c['status'] in ('fail', 'error') for c in parsed['checks']), parsed['checks']
    return results


def local(args, request, candidates, out):
    assert not out.exists(), out
    out.mkdir()
    (out/'README.human.md').write_text('# Проверка заявки\n\nЗдесь результаты одной заявки harness. Например, local-*-analyze.json содержит штатную оценку кандидата.\n')
    shutil.copyfile(__file__, out/'validate_execution.py')
    h.ordinary(REPO/'harness')
    h.ordinary(ENTRY)
    baseline = {}
    texts = {}
    for name, source in candidates.items():
        h.ordinary(source)
        for parent in ('harness/common/skills', '.agents/skills', '.claude/skills'):
            path = REPO/parent/name
            baseline[str(path.relative_to(REPO))] = h.snapshot(path) if path.exists() else None
        texts[name] = {str(p.relative_to(source)): p.read_text() for p in source.rglob('*')
                       if p.is_file() and p.name != 'README.human.md'}
    save(out/'before.json', {'time': now(), 'protected': protect(), 'targets': baseline,
                            'candidates': {n: h.snapshot(p) for n,p in candidates.items()}, 'machine_texts': texts})
    text = (request/'request.md').read_text()
    text = text.replace('- Status: new.', '- Status: in progress.', 1)
    text += '\n## Текущая обработка\n\n- Result: локальные проверки и сверка текущих владельцев.\n- Updated: '+now()+'\n'
    (request/'request.md').write_text(text)
    results = {name: evaluate(out, source, name, 'local') for name,source in candidates.items()}
    modes = {}
    for mode in ('common', 'both'):
        with tempfile.TemporaryDirectory(prefix='inbox-installation-') as directory:
            root = Path(directory)
            startup = h.prepare(root, mode, 'baseline')
            for name, source in candidates.items():
                for parent in ('harness/common/skills', '.agents/skills', '.claude/skills'):
                    target = root/parent/name
                    if target.exists():
                        shutil.rmtree(target)
                    shutil.copytree(source,target)
                    assert h.snapshot(source) == h.snapshot(target)
            old = None
            for _ in range(2):
                run = h.run(['python3','-B','harness/common/checks/ensure_entrypoint_links.py'],cwd=root)
                assert run['exit_code'] == 0,run
                startup['startup'].append(run)
                snap = h.snapshot(root)
                assert old is None or old == snap
                old = snap
            run = h.run([PYTHON,'-m','pytest',str(root/'harness/common/testing/tests/test_rule_copies.py'),'-q','--import-mode=importlib'],cwd=root,
                        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
            assert run['exit_code'] == 0,run
            save(out/f'local-installation-{mode}.json',{'startup':startup,'suite':run})
            modes[mode] = run['stdout'].strip()
    save(out/'local-summary.json',{'time':now(),'results':results,'modes':modes,
         'Codex':'непроверенный: native checks не завершены','Claude':'непроверенный','overall':'непроверенный',
         'native_obstacle':'../2026-11-13-always-loaded-rule-budgets/green2-codex-candidate-v3-both-author.json'})
    print(json.dumps({'request':request.name,'results':{n:{'grade':r['grade'],'score':r['score'],'invoke':r['budgets']['invoke_cost_tokens']['value'],'deferred':r['budgets']['deferred_cost_tokens']['value']} for n,r in results.items()},'modes':modes},ensure_ascii=False),flush=True)


def publish(args,request,candidates,out):
    before = json.loads((out/'before.json').read_text())
    json.loads((out/'local-summary.json').read_text())
    assert protect() == before['protected']
    for name,source in candidates.items():
        assert h.snapshot(source) == before['candidates'][name],source
        for parent in ('harness/common/skills','.agents/skills','.claude/skills'):
            target=REPO/parent/name;h.ordinary(target.parent)
            assert (h.snapshot(target) if target.exists() else None) == before['targets'][str(target.relative_to(REPO))],target
    paths=[]
    for name,source in candidates.items():
        for parent in ('harness/common/skills','.agents/skills','.claude/skills'):
            target=REPO/parent/name
            if not target.exists():
                shutil.copytree(source,target)
            else:
                assert {str(p.relative_to(target)) for p in target.rglob('*') if p.is_file()} <= {str(p.relative_to(source)) for p in source.rglob('*') if p.is_file()}
                for p in source.rglob('*'):
                    if p.is_file():
                        destination=target/p.relative_to(source)
                        destination.parent.mkdir(exist_ok=True)
                        shutil.copyfile(p,destination)
            assert h.snapshot(source) == h.snapshot(target),target
            paths.extend(str(p.relative_to(REPO)) for p in target.rglob('*') if p.is_file())
    assert protect() == before['protected']
    visibility=h.run(['git','check-ignore','--no-index',*paths])
    assert visibility['exit_code'] == 1 and not visibility['stdout'],visibility
    startup=h.run(['python3','-B','harness/common/checks/ensure_entrypoint_links.py'])
    assert startup['exit_code'] == 0,startup
    save(out/'publication.json',{'time':now(),'paths':paths,'full_copies_equal':True,'protected_unchanged':True,'visibility':visibility,'startup':startup,
                                'source_hashes':{n:h.snapshot(p) for n,p in candidates.items()}})
    results={name:evaluate(out,REPO/'harness/common/skills'/name,name,'installed') for name in candidates}
    save(out/'installed-summary.json',results)
    print(json.dumps({'request':request.name,'published_paths':len(paths),'full_copies_equal':True,'installed_profiles_and_analysis':'passed'},ensure_ascii=False),flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=('local','publish'))
    parser.add_argument('slug')
    parser.add_argument('--candidate',default='candidate')
    args=parser.parse_args()
    request=REPO/'harness/common/inbox'/args.slug
    candidates={p.name:p for p in (request/args.candidate).iterdir() if p.is_dir() and (p/'SKILL.md').is_file()}
    assert candidates,request
    out=REPO/'harness/common/testing/evidence'/('2026-11-13-execute-'+args.slug[11:])
    if args.action=='local':local(args,request,candidates,out)
    else:publish(args,request,candidates,out)
