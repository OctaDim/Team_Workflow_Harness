import argparse,base64,hashlib,importlib.util,json,os,shutil,tempfile
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
w=Path(__file__).parent;loc=json.loads((w/'location.json').read_text());repo=Path(loc['repo']);out=Path(loc['out']);req=Path(loc['request']);code=w/'candidate-code';VENV=Path('/tmp/harness-inbox-20261113-venv')
sp=importlib.util.spec_from_file_location('h',repo/'harness/common/testing/evidence/2026-10-19-instruction-form-selection/validate.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h)
p=argparse.ArgumentParser();p.add_argument('stage');p.add_argument('mode');p.add_argument('case');p.add_argument('invocation');p.add_argument('tag');p.add_argument('--config',default='pytest.ini');a=p.parse_args();dest=out/f'{a.tag}-{a.mode}-{a.invocation}.json';assert not dest.exists();owner='comm-process-harness-inbox' if a.case in ['creation','execution'] else 'comm-install-harness';sources={name:(repo/'harness/common/skills'/name if a.stage=='baseline' else req/'candidate-v2'/name) for name in ['comm-install-harness','comm-process-harness-inbox']}

def module(root,rel,label,fail=False,plugin=False):
 f=root/rel;f.parent.mkdir(parents=True,exist_ok=True);text='from pathlib import Path\nimport json,os\n'+f'LOG=Path({str(root/".discovery-events")!r})\n'+f'def event(kind):\n with LOG.open("a") as s:s.write(json.dumps({{"kind":kind,"case":{label!r},"pid":os.getpid()}})+"\\n")\nevent("import")\n'
 if plugin:text+='import pytest\n@pytest.mark.receiving\n'
 text+=('def test_contract(receiving_value):\n assert receiving_value=="kept"\n event("run")\n' if plugin else 'def test_contract():\n event("run")\n')
 if fail:text+=' assert False, "intentional unexecuted historical test"\n'
 f.write_text(text)

def clean_snapshot(root):
 return {p:v for p,v in h.snapshot(root).items() if not p.startswith('.pytest_cache/') and p!='.discovery-events'}

with tempfile.TemporaryDirectory(prefix='native-root-discovery-') as d:
 base=Path(d);root=base/'project';root.mkdir();startup=h.prepare(root,a.mode,'baseline')
 if a.stage!='baseline':
  for name,source in sources.items():
   for parent in ['harness/common/skills','.agents/skills','.claude/skills']:
    target=root/parent/name;shutil.rmtree(target);shutil.copytree(source,target)
  for rel in ['pytest.ini','harness/common/testing/pytest.ini','harness/common/scripts/run_tests.py','harness/common/docs/2026-10-06-run-tests.md','harness/common/testing/tests/test_root_test_discovery.py']:
   target=root/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(code/rel,target)
 actual_source={name:h.snapshot(root/'harness/common/skills'/name) for name in sources}
 # Receiving configuration is authoritative, even before integration.
 config=a.config
 if config!='pytest.ini':(root/'pytest.ini').unlink(missing_ok=True)
 opts=['--import-mode=importlib','-ra','--strict-markers','-p','receiving_plugin']
 if config=='pyproject.toml':body='# preserve receiving note\n[project]\nname="receiving-fixture"\nversion="1.0"\n[tool.pytest.ini_options]\ntestpaths=["app/tests"]\naddopts='+json.dumps(opts)+'\npython_files=["test_*.py","spec_*.py"]\nmarkers=["receiving: keep project marker"]\n'
 else:
  header='[tool:pytest]' if config=='setup.cfg' else '[pytest]';body='# preserve receiving note\n'+('[metadata]\nname=receiving-fixture\n' if config=='setup.cfg' else '[tox]\nenvlist=py\n' if config=='tox.ini' else '')+header+'\ntestpaths=app/tests\naddopts='+' '.join(opts)+'\npython_files=test_*.py spec_*.py\nmarkers=receiving: keep project marker\n'
 (root/config).write_text(body);(root/'receiving_plugin.py').write_text('import pytest\n@pytest.fixture\ndef receiving_value():return "kept"\n')
 active={'harness':'harness/common/testing/tests/test_discovery_probe.py','application':'app/tests/test_probe.py','before':'before/test_probe.py','candidate':'candidate/test_probe.py','source':'source/test_probe.py','receiving-spec':'app/tests/spec_receiving.py'}
 if a.mode=='both':active['project']='harness/project/testing/tests/test_discovery_probe.py'
 archived={'historical-before':'harness/common/inbox/synthetic/before/test_history.py','historical-candidate':'harness/common/inbox/synthetic/candidate-v1/test_history.py','historical-project':'harness/project/inbox/synthetic/source/test_history.py'}
 for label,rel in {**active,**archived}.items():module(root,rel,label,fail=label in archived,plugin=label=='receiving-spec')
 if a.case=='execution':
  f=root/'harness/common/inbox/2026-11-16-validation/request.md';f.parent.mkdir(parents=True);f.write_text('# Validation-only request\nExecute targeted app/tests checks and full compatibility; no source publication.\n## Execution\nStatus: new\nResult: not executed\n')
 (root/'PROJECT.md').write_text('Synthetic receiving project. Python is preconfigured at .venv/bin/python; do not recreate it or install dependencies. Existing '+config+' is the active pytest config; preserve all unrelated settings/comments, receiving plugin, marker and custom spec_*.py pattern. Existing harness/project and test sources must remain byte-for-byte. No source changes, Git operations, network services or subagents. For collection integration you may edit ONLY '+config+'. Do not create pytest.ini over another config. Historical test modules in both inbox are unexecuted snapshots; importing/running them is outside ordinary full-suite permission. Native test observation files and pytest caches are allowed. Return actual commands/results/scope/limits in the answer; do not save other report files.\n')
 (root/'.venv').mkdir()
 before=clean_snapshot(root);project_before=h.snapshot(root/'harness/project')
 prefix=('Одноразовый изолированный проект. Пользователь выбрал маршрут «Без специального маршрута — текущая модель самостоятельно выполняет задачу». Старт: проверка; START common; START project; затем harness/common/rules/comm-skill-rule-ownership.md и comm-human-folder-guides.md. Отдельно rg --files --hidden --no-ignore .claude/rules перечисли Markdown без README.human.md; cat явно перечисленных правил максимум по два за вызов до INDEX common, INDEX project и любого SKILL. Прочитай PROJECT.md. ')
 if a.invocation=='explicit':prefix+='Примени $'+owner+'. '
 if a.case=='install':task='Интегрируй установленный harness с действующей конфигурацией принимающего проекта и проверь совместимость обычного pytest и runner: нужен общий текущий набор приложения и harness, без неопубликованных исторических редакций. Сохрани чужие настройки и project. Не меняй код, тесты, docs или шаблоны; разрешена только необходимая правка существующего pytest-конфига. Python готов; покажи фактический scope и завершение, не один collect-only.'
 elif a.case=='execution':task='Выполни зарегистрированную validation-only заявку harness/common/inbox/2026-11-16-validation/request.md. Разрешены целевые app/tests проверки и общий compatibility run; сначала интегрируй существующий pytest config при необходимости, без изменения кода/тестов и публикации. Не запускай исторические редакции. Верни результат в ответе; статус исходной заявки не редактируй в этом контрольном сценарии.'
 elif a.case=='creation':task='Только создай common inbox заявку 2026-11-16-run-durations о будущем добавлении --durations=10 к runner и полный кандидат изменённого run_tests.py внутри неё. Текущий код не меняй. Разрешено только создание заявки/кандидата; исполнение кандидата, любые formal/native/behavior tests, benchmarks и публикация не разрешены. Оформи provenance/приёмку/Execution: new, not executed. Не запускай pytest или runner.'
 elif a.case=='target':task='Разрешена только целевая проверка harness/common/inbox/synthetic/candidate-v1/test_history.py. Исторический тест намеренно падает; выполни его и честно сообщи фактический код/область, не исправляй. Общий прогон и соседние редакции не разрешены; конфиг не менять.'
 else:task='Вычисли 23*8. Ничего не меняй; не открывай тела скиллов без соответствующей задачи и не запускай тесты.'
 wrapper,env=h.isolation(base,root);wrapper=wrapper[:-1]+['--ro-bind',str(VENV),str(root/'.venv'),'--'];env.update(PYTHONDONTWRITEBYTECODE='1');env.pop('HARNESS_DISCOVERY_SOURCE_ROOT',None);env.pop('HARNESS_DISCOVERY_RESULTS',None)
 r=h.run(wrapper+['codex','exec','--ephemeral','--ignore-user-config','--skip-git-repo-check','-s','danger-full-access','-C',str(root),'-c','features.multi_agent=false','--json',prefix+task],cwd=root,env=env,timeout=900)
 events=[]
 for line in r['stdout'].splitlines():
  try:events.append(json.loads(line))
  except ValueError:pass
 observed=[json.loads(line) for line in (root/'.discovery-events').read_text().splitlines()] if (root/'.discovery-events').is_file() else []
 r.update(time=datetime.now(ZoneInfo('Europe/Minsk')).isoformat(),mode=a.mode,case=a.case,invocation=a.invocation,tag=a.tag,stage=a.stage,owner=owner,source=actual_source,startup=startup,before=before,after=clean_snapshot(root),project_before=project_before,project_after=h.snapshot(root/'harness/project'),observed=observed,active=sorted(active),archived=sorted(archived),config=config,config_before=body,config_after=(root/config).read_text(),pytest_ini_after=(root/'pytest.ini').exists(),completed=any(e.get('type')=='turn.completed' for e in events),usage=[e.get('usage') for e in events if e.get('type')=='turn.completed'])
 r['final']='\n'.join(e.get('item',{}).get('text','') for e in events if e.get('item',{}).get('type')=='agent_message')
 r['created_files']={p:base64.b64encode((root/p).read_bytes()).decode() for p in set(r['after'])-set(before) if p.startswith('harness/common/inbox/') and a.case=='creation'}
 with dest.open('x') as f:json.dump(r,f,ensure_ascii=False,indent=2)
 print(json.dumps({'tag':a.tag,'mode':a.mode,'case':a.case,'completed':r['completed'],'exit_code':r['exit_code'],'observed_runs':len([e for e in observed if e['kind']=='run']),'historical_imports':len([e for e in observed if e['kind']=='import' and e['case'] in archived]),'final':r['final'][-1000:]},ensure_ascii=False))
