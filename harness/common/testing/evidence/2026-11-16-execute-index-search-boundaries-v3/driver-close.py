import hashlib,importlib.util,json,os,shutil
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v2.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);source=Path(loc['source']);sp=importlib.util.spec_from_file_location('g',repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
publication=json.loads((out/'publication.json').read_text());assert publication['source_sha256']==publication['installed_sha256']==hashlib.sha256(source.read_bytes()).hexdigest();r=g.h.run([g.PYTHON,'-m','pytest','-q'],cwd=repo,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'),timeout=300);g.save(out/'installed-root-suite.json',r);assert r['exit_code']==0,r['stdout'][-1500:];assert g.protect()==json.loads((out/'before.json').read_text())['protected'];now=g.now();a=json.loads((out/'stock-assessment-summary.json').read_text());size=json.loads((out/'content-and-size.json').read_text())
text='''# INDEX: границы текущего поиска и чтения истории

Опубликован полный candidate-INDEX-v3.md в единственный canonical
harness/common/INDEX.md. Остальной текст карты, категории и ссылки сохранены
байтово. README.human.md исключён одной фразой на любой глубине. Обычный поиск
текущих требований ограничен выбранной canonical категорией без inbox/evidence;
для inbox сначала устанавливаются статус и применимость. Имя/возраст копии не
делают её текущей. Выбранный актуальный кандидат, проверка требований и нужные
свидетельства доступны по конкретной задаче. Нового правила/скилла не создано.

Маршрут writing-skills: настоящий baseline дал правильный UTF8 ответ, но
глобальным rg раскрыл закрытую заявку и ненужную историческую копию.
Подготовленный v1 повторил этот дефект. V2 добавил границу обычного поиска, но triage всё ещё читал закрытую заявку
целиком вместе с текущей. V3 требует сначала извлекать только статус; актуальный
кандидат и необходимая история остаются доступны. Вся текущая матрица повторена.
V3 содержит эту явную границу
обычного содержательного поиска; все остальные части INDEX сохранены.
Исходные ответы/снимки и v1 diagnosis лежат в соседнем исходном evidence;
v2 результаты и оба наблюдаемых сбоя сохранены в соседнем evidence-v2,
они не переписаны. Локальный static checker после замены вводной фразы ошибочно
искал старый полный anchor; исправлен только anchor проверки, весь неизменный
prefix/suffix по-прежнему сравнивается. Неудачная попытка сохранена отдельно.

Реальная текущая проверка Codex:10/10 свежих изолированных native сценариев,
5/5 в common-only и5/5 в common+project. Ordinary читает canonical контракт
без ненужной истории; selected и triage сначала читают текущий статус и затем
выбранный before/selected-2020.json, игнорируя исторический candidate-2099;
history действительно читает указанные report+raw и текущий контракт и
объясняет UTF8/UTF16 расхождение; unrelated решает задачу без лишнего поиска.
Правильный конечный ответ сам по себе не считается прохождением: проверены
фактические завершённые команды/выводы, порядок startup/status, источники,
маркеры исторических тел, отсутствие human bodies, неизменность файлов/project.
Это наблюдаемое поведение в заданном наборе, не запрет I/O на уровне ядра и
не универсальная гарантия для будущих сессий. Claude не запускался.

Полные изолированные наборы:195 passed в каждом режиме. Все category links
существуют в логическом целевом месте, переносы/common skeleton сохранены,
повторный startup неизменен, project-only отказал до записи. Рабочий набор
после публикации: ROOT_RESULT. AGENTS/CLAUDE/project/.claude/rules сохранены.

Форма: существующая навигационная карта; новые always-loaded rules/skills не
добавлены. Для INDEX rule-only word-band и skill-creator неприменимы; общего
лимита на весь startup нет. Фактическая карта выросла с345 слов/2863 символов
до447/3661 (+102/+798); UTF8 bytes4587→6011. Обязательная startup-стоимость
растёт на200 по статической ceil(chars/4) оценке. Stock plugin-eval package0.1.2
(JSONtool self-version0.1.0) применён к ограниченной generic папке с полным
INDEX.md, без SKILL/manifest/coverage-обходов: A95,0 fail/error. Сохранён warning
heavy: generic deferred estimator916 (до716), хотя INDEX реально читается
обязательно на startup. Ни generic A, ни это название budget-поля не являются
проверкой skill/plugin или поведением модели. Component/per-file данные,
реальные reads/usage, startup и весь доступный lazy каталог разделены в
context-accounting.json и stock-assessment-summary.json.

Точные source/raw/dependency hashes и текущие проверки: publication-gate.json,
native-review-final.json, external-dependencies.json, publication.json.
Codex/common-only и Codex/common+project: проверен в указанной текущей области.
Claude/common-only и Claude/common+project: not run, непроверенные.
Итоговый статус: непроверенный.
'''.replace('ROOT_RESULT',r['stdout'].strip().splitlines()[-1]+'; exit0')+'\nЗавершено: '+now+'.\n'
with (out/'2026-11-16-report.md').open('x') as f:f.write(text)
with (source.parent/'request.md').open('a') as f:f.write('\n## Execution — результат текущего исполнения\n\nStatus: completed\nResult: candidate-INDEX-v3 опубликован в canonical INDEX; только поисковый абзац изменён. Codex10/10,5/5 в каждом режиме; generic A95;195/195 изолированно и195 passed в рабочем наборе.\nReason: baseline и первоначальный кандидат открывали лишнюю историю; уточнена граница обычного поиска, необходимая работа с актуальным кандидатом и историей сохранена и проверена.\nReport: ../../testing/evidence/'+out.name+'/2026-11-16-report.md\nUpdated: '+now+'\nCodex/common-only: verified (documented current scope)\nCodex/common+project: verified (documented current scope)\nClaude/common-only: not run; unverified\nClaude/common+project: not run; unverified\nOverall: unverified\n')
g.save(out/'completion.json',{'time':now,'source_sha256':publication['source_sha256'],'installed_equal':True,'protected_unchanged':True,'root_suite':r['stdout'].strip().splitlines()[-1]})
for n in ['publish.py','close.py']:shutil.copyfile(w/n,out/('driver-'+n))
print('INDEX completed; '+r['stdout'].strip().splitlines()[-1])
