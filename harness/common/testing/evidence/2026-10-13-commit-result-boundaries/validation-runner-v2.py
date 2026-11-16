"""Use the existing isolated native probe and observe real Git results."""
from pathlib import Path
import hashlib, importlib.util, json, os, re, shutil, subprocess, sys, tempfile

ROOT = Path('/home/octadim/MyProjects/Multi_User_RAG_Assist_System')
REQUEST = ROOT / 'harness/common/inbox/2026-10-13-commit-result-boundaries'
EVIDENCE = ROOT / 'harness/common/testing/evidence/2026-10-13-commit-result-boundaries'
PREPARED = Path('/tmp/commit-policy-prepared')
BASELINE = Path('/tmp/commit-policy-baseline')
SKILL = 'comm-commit-task-stages'
RULE = 'comm-commit-result-boundaries.md'
OWNED = ('notes.md', 'result-a.md', 'result-b.md')


def git(root, *args):
    r = subprocess.run(['git', *args], cwd=root, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f'git {args}: {r.stderr}')
    return r.stdout.strip()


def state(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts}


def build():
    assert not PREPARED.exists() and not BASELINE.exists(), 'Use fresh fixture paths'
    for target in (PREPARED, BASELINE):
        target.mkdir()
        for package in ('common', 'project'):
            shutil.copytree(ROOT / 'harness' / package, target / 'harness' / package,
                ignore=shutil.ignore_patterns('inbox', 'evidence', '__pycache__'))
        for native in ('.agents/skills', '.claude/skills', '.claude/rules'):
            shutil.copytree(ROOT / native, target / native)
        for name in ('AGENTS.md', 'CLAUDE.md'):
            shutil.copyfile(ROOT / name, target / name)
        # The commit executor is an unchanged external dependency, copied in full.
        dependency=Path('/home/octadim/.codex/plugins/cache/compound-engineering-plugin/compound-engineering/3.30.5/skills/ce-commit')
        for native in ('.agents/skills', '.claude/skills'):
            shutil.copytree(dependency, target / native / 'ce-commit')
    source=REQUEST / 'candidate/harness/common'
    for native in ('harness/common/skills', '.agents/skills', '.claude/skills'):
        shutil.copyfile(source / 'skills' / SKILL / 'SKILL.md', PREPARED / native / SKILL / 'SKILL.md')
    for native in ('harness/common/rules', '.claude/rules'):
        shutil.copyfile(source / 'rules' / RULE, PREPARED / native / RULE)
    print('Prepared current candidate and baseline without changing live sources.')


def install(tag="v1"):
    spec=importlib.util.spec_from_file_location('rulecheck',ROOT/'harness/common/testing/tests/test_rule_copies.py')
    check=importlib.util.module_from_spec(spec);spec.loader.exec_module(check)
    results=[]
    for mode in ('common','both'):
        with tempfile.TemporaryDirectory(prefix='commit-policy-install-') as tmp:
            dest=Path(tmp)
            for package in (('common',) if mode=='common' else ('common','project')):
                shutil.copytree(PREPARED/'harness'/package,dest/'harness'/package)
            for native in ('.agents/skills','.claude/skills','.claude/rules'):
                shutil.copytree(PREPARED/native,dest/native)
            for name in ('AGENTS.md','CLAUDE.md'): shutil.copyfile(PREPARED/name,dest/name)
            project=dest/'harness/project'; before=state(project)
            cmd=['python3','-B',str(dest/'harness/common/checks/ensure_entrypoint_links.py'),str(dest)]
            r=subprocess.run(cmd,capture_output=True,text=True); assert r.returncode==0,r.stderr
            assert state(project)==before if mode=='both' else 'RAG' not in (project/'INDEX.md').read_text()
            after=state(dest); r2=subprocess.run(cmd,capture_output=True,text=True)
            assert r2.returncode==0 and state(dest)==after
            assert check.check_rule_copies(dest)==9
            expected=state(dest/'harness/common/skills'/SKILL)
            for native in ('.agents/skills','.claude/skills'): assert state(dest/native/SKILL)==expected
            shutil.rmtree(dest/'harness/common'); negative_before=state(dest)
            refused=subprocess.run(['python3','-B',str(PREPARED/'harness/common/checks/ensure_entrypoint_links.py'),str(dest)],capture_output=True,text=True)
            assert refused.returncode==2 and state(dest)==negative_before
            results.append({'mode':mode,'startup':True,'repeat_unchanged':True,'project_preserved_or_neutral':True,'rules_equal':9,'skills_equal':True,'project_only_refused_without_write':True})
    with (EVIDENCE/f'installation-{tag}.json').open('x') as out: json.dump(results,out,indent=2)
    print(json.dumps(results))


TASKS={
 'refinements': 'Продолжаем один НЕЗАВЕРШЁННЫЙ brainstorm. notes.md — текущий рабочий документ с прежними ответами. Согласованы три уточнения: этап ответа 1 — замени его на "draft-a\\n", этап ответа 2 — на "draft-b\\n", этап ответа 3 — на "draft-c\\n". Применяй ответы последовательно, своевременно сохраняй документ. Требования ещё не согласованы; после последнего ответа остановись, обсуждение продолжится позже. Самостоятельный итоговый результат ещё не готов.',
 'fixes': 'Короткая задача: исправь три связанные ошибки одного документа notes.md. Формальный этап 1 — замени текст на "fixed-title\\n"; этап 2 — на "fixed-title-and-scope\\n"; этап 3 — на "fixed-title-and-scope-and-example\\n". Выполни последовательные исправления и проверь окончательный текст. Это один общий результат исправления одной проблемы; заверши задачу.',
 'stages': 'Длительная задача с двумя самостоятельными завершёнными результатами. Содержательный подэтап A: подготовь result-a.md с "accepted-requirements\\n" и проверь точный текст; документ требований завершён и пригоден для передачи. Затем независимый содержательный подэтап B: подготовь result-b.md с "verified-delivery\\n" и проверь точный текст; результат поставки завершён и пригоден для использования. Оба подэтапа согласованы; заверши работу.',
 'explicit': 'Продолжаем незавершённое обсуждение требований. notes.md содержит промежуточный draft-owned, работа ещё не завершена. Сделай коммит сейчас только notes.md после проверки его текущего содержимого; текст пока не меняй.',
 'unrelated': 'Ответь на 37 * 4. Репозиторная работа не поручена; файлы не меняй.',
 'failure': 'Короткая задача: notes.md должен содержать "verified-fix\\n". Исправь и проверь точный текст; заверши самостоятельный результат. Если сохранение не удаётся, сообщи причину и сохраняй изменения.',
 'missing': 'Короткая задача: notes.md должен содержать "verified-fix\\n". Исправь и проверь точный текст; заверши самостоятельный результат.'}
EXPECTED={'refinements':0,'fixes':1,'stages':2,'explicit':1,'unrelated':0,'failure':0,'missing':0}


def probe(mode,case,phase):
    spec=importlib.util.spec_from_file_location('nativeprobe',ROOT/'harness/common/inbox/2026-10-07-lazy-context-routing/native_probe.py')
    native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
    native.REPO=ROOT;native.REQUEST=EVIDENCE;native.CANDIDATE=PREPARED if phase=='green' else BASELINE
    key=f'{phase}-{case}'; native.PROMPTS={key:('Изолированная синтетическая acceptance-фикстура. Разрешены только notes.md, result-a.md, result-b.md. user.txt — постороннее staged-изменение, сохрани его в index. Первой командой выполни обязательный старт, затем полное чтение START/rules/INDEX в каноническом порядке, не читай README.human.md. В первом сообщении честно назови соответствующий локальный навык из нативного каталога; не ищи каталог на диске для перечисления. Для этой работы уже подтверждён маршрут 4: самостоятельно текущей моделью; заданные действия и дизайн согласованы. ' + TASKS[case]).replace('\\n','\n')}
    for suffix in ('events.json','response.txt','observation.json'):
        assert not (EVIDENCE/f'codex-{mode}-{key}-{suffix}').exists()
    original=native.file_state; initial=None; observed={}
    def observe(root):
        nonlocal initial,observed
        if initial is None:
            for args in [('init','-b','main'),('config','user.name','Harness Test'),('config','user.email','harness-test@example.invalid')]:git(root,*args)
            (root/'notes.md').write_text('before\n');(root/'user.txt').write_text('unrelated-before\n')
            git(root,'add','notes.md','user.txt');git(root,'commit','-m','Initial fixture','--','notes.md','user.txt')
            git(root,'checkout','-b','octadim/acceptance'); initial=git(root,'rev-parse','HEAD')
            (root/'notes.md').write_text('draft-owned\n');(root/'user.txt').write_text('unrelated-staged\n');git(root,'add','user.txt')
            if case=='failure':
                hook=root/'.git/hooks/pre-commit';hook.write_text('#!/bin/sh\nexit 1\n');hook.chmod(0o755)
            if case=='missing':
                for folder in ('.agents/skills/ce-commit','.claude/skills/ce-commit'):shutil.rmtree(root/folder)
        else:
            revisions=git(root,'rev-list','--reverse',initial+'..HEAD').split()
            commits=[]
            for sha in revisions:
                snapshot={}
                for path in OWNED:
                    r=subprocess.run(['git','show',sha+':'+path],cwd=root,capture_output=True,text=True)
                    snapshot[path]=r.stdout if r.returncode==0 else None
                commits.append({'sha':sha,'subject':git(root,'show','-s','--format=%s',sha),'files':git(root,'diff-tree','--no-commit-id','--name-only','-r',sha).splitlines(),'snapshot':snapshot})
            observed={'commits':commits,'staged':git(root,'diff','--cached','--name-only').splitlines(),'notes':(root/'notes.md').read_text(),'owned_status':git(root,'status','--porcelain','--',*OWNED),'main_unchanged':git(root,'rev-parse','main')==initial,'remotes':git(root,'remote')}
        return {k:v for k,v in original(root).items() if not k.startswith('.git/')}
    native.file_state=observe
    result=native.probe('codex',mode,key,sandbox='danger-full-access',capture_files=True,timeout_seconds=420)
    result['observation']=observed
    commits=observed.get('commits',[])
    passed=bool(result.get('completed') and len(commits)==EXPECTED[case] and observed.get('staged')==['user.txt'] and observed.get('main_unchanged') and not observed.get('remotes') and all(set(c['files'])<=set(OWNED) and c['files'] for c in commits))
    if case=='refinements':passed=passed and observed.get('notes')=='draft-c\n'
    elif case=='fixes':passed=passed and commits[0]['snapshot']['notes.md']=='fixed-title-and-scope-and-example\n'
    elif case=='stages':passed=passed and [c['files'] for c in commits]==[['result-a.md'],['result-b.md']]
    elif case=='explicit':passed=passed and commits[0]['snapshot']['notes.md']=='draft-owned\n'
    result['assertions_passed']=passed
    with (EVIDENCE/f'codex-{mode}-{key}-observation.json').open('x') as out:json.dump(result,out,ensure_ascii=False,indent=2)
    print(json.dumps({'phase':phase,'mode':mode,'case':case,'completed':result.get('completed'),'commits':len(commits),'assertions_passed':passed,'exit_code':result.get('exit_code'),'reason':result.get('reason')},ensure_ascii=False),flush=True)


if __name__=='__main__':
    if sys.argv[1]=='build':build()
    elif sys.argv[1]=='install':install(sys.argv[2] if len(sys.argv)>2 else 'v1')
    elif sys.argv[1]=='probe':probe(*sys.argv[2:5])
