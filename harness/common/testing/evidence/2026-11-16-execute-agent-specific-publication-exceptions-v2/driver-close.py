import importlib.util,json,os,shutil
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
w=Path(__file__).parent;loc=json.loads((w/'location-v2.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);source=Path(loc['source']);sp=importlib.util.spec_from_file_location('g',repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
assert json.loads((out/'publication.json').read_text())['full_copies_equal'];r=g.h.run([g.PYTHON,'-m','pytest','-q'],cwd=repo,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'),timeout=300);g.save(out/'installed-root-suite.json',r);assert r['exit_code']==0,r['stdout'][-1800:];before=json.loads((out/'before.json').read_text());assert g.protect()==before['protected'];actual=g.h.snapshot(source)
for parent in ['harness/common/skills','.agents/skills','.claude/skills']:assert g.h.snapshot(repo/parent/source.name)==actual
now=datetime.now(ZoneInfo('Europe/Minsk')).isoformat();report=out/'2026-11-16-report.md'
text='''# Отдельные результаты и исключения в гейте публикации

Опубликован comm-publish-harness-instructions candidate-v2:15 файлов полных
равных canonical/.agents/.claude папок. Из машинных файлов изменены только
SKILL.md и gate.md; placement-contract сохранён целиком. Сначала каждый
обязательный agent/mode слот сопоставляется с полным текущим успехом либо
точным согласованным исключением. Исправление/остановка относятся к оставшимся
неохваченным результатам. Исключение не превращает fail/not-run в pass.
Общее «публиковать», A100, exit0, частичный успех или overall unverified не
заменяют отсутствующий результат/исключение. Новое правило и исполняемый
production-путь не добавлены; подтверждённый дефект устраняется в lazy-гейте.

Маршрут writing-skills: свежие canonical baseline на Claude-only/Codex failure
и позднем необъяснённом pass остановили выпуск. Исторический инцидент не
воспроизведён этими свежими контролями; причинное улучшение относительно них
не заявляется. Начальный fixture с подсказкой правильного ответа сохранён
отдельно и не используется как RED.

Подготовленный кандидат v1 дал реальный RED: combined implicit scoped-exception
отказался выполнить точно согласованную операцию. В SKILL/resolve-разделе
безусловное «stop on unresolved» перекрывало следующий раздел исключений.
Отдельный all-pass сценарий содержал противоречивое diagnosis=unresolved;
это ошибка fixture, не дополнительный дефект кандидата. V1 не опубликован;
полные34 raw и диагноз сохранены в ../2026-11-16-execute-agent-specific-publication-exceptions/.
V2 классифицирует покрытие слотов перед разбором неохваченных результатов;
успешный fixture имеет diagnosis=N/A. Оба прежних combined сценария сначала
повторены успешно, затем повторены ВСЕ обязательные текущие проверки.

Реальная проверка CodexCLI0.166.0:34/34 свежих native сценария —17/17 в каждом
common-only/common+project. Наблюдаются настоящие file-copy и queue действия
во временных изолированных проектах, не только обещания в ответах. Проверены
неверный диапазон publication-base..HEAD→base..HEAD, разные агенты/режимы,
исправление подтверждённой причины сценария/среды без правки инструкции,
изменение кандидата до v2 с полным новым результатом и недостающим v2 решением,
необъяснённый lucky retry, точное исключение без повторного вопроса, полный
успех, новые version/failure/native scope, неоднозначное подтверждение,
отказ передачи данных, недоступный инструмент и unrelated non-loading.

Для ремонтов сверены фактический запуск producer и полный текущий результат
ДО первого copy; исходные raw/contract/status/tools неизменны. Для запрещённого
выпуска source/native и очередь сохранены, completed/rejected не записаны.
Для разрешённого — полный current source равен всем native-копиям, порядок
publish→advance наблюдаем, gate+placement прочитаны перед копированием.
Статусы разрешённого исключением fail/not-run дополнительно сверены по полным
финальным ответам в status-preservation-audit.json. Защищённые project/rules/
entrypoints и прочие файлы сохранены; весь поддерживаемый source/native scope
проверен до и после переносов.

Важно различать уровни: Codex/Claude slots, A100/19-of20 и waiver-данные ВНУТРИ
fixture — явно синтетические входы моделируемого решения. Producer не является
реальной модельной проверкой или заменой plugin-eval. Настоящие34 Codex-сеанса
проверяют поведение владельца на этих входах. Реальный Claude не вызывался.
Ни одного синтетического fail не выдают за реальное прохождение; исходные
данные и фактические статусы сохраняются. Универсальная невозможность будущих
ошибок модели или злонамеренного обхода не обещается.

Actual skill-creator/stock plugin-eval0.1.2: A95 до и после публикации,
без fail/error. Invoke373, deferred841, trigger39, total1253, estimated-static
char/4. Heavy warning стоимости ресурсов/total сохранён;841 ниже ориентира
суммы ресурсов1000 и порога deferred1200. Пороги/coverage не менялись; guides
исключены. Полные source/native наборы и ordinary типы равны. Изолированные
полные наборы:195 passed common-only и195 passed common+project; project-only
отказал до записи, повторный startup неизменен. Рабочий набор после публикации:
ROOT_RESULT.

Точная версия и проверенные raw hashes: before.json, native-review-final.json,
publication-gate.json, publication.json. Зависимости сверены с before всех34
сеансов: external-dependencies.json. Startup/metadata, весь доступный логический
lazy-каталог, собственные ссылки, отдельный toy target/fixture code и реальные
reads/session usage разделены в context-accounting.json; расход всей сессии
не приписывается одному SKILL. Human bodies не загружались в инструктивный
контекст. Python3.12.15, pytest8.4.2, Node22.14.0; CLI model/effort default без
override. Исторические evidence-скрипты и чужие результаты не редактировались.

Codex/common-only: проверен в документированной текущей области.
Codex/common+project: проверен в документированной текущей области.
Claude/common-only и Claude/common+project: not run, непроверенные.
Итоговый статус: непроверенный.
'''.replace('ROOT_RESULT',r['stdout'].strip().splitlines()[-1]+'; exit0')+'\nЗавершено: '+now+'.\n'
with report.open('x') as f:f.write(text)
p=source.parent.parent/'request.md'
with p.open('a') as f:f.write('\n## Execution — результат текущего исполнения\n\nStatus: completed\nResult: candidate-v2 существующего comm-publish-harness-instructions опубликован;15 полных файлов равны. Реальный Codex34/34,17/17 в каждом режиме, A95,195/195 изолированно и195 passed в рабочем наборе.\nReason: противоречие остановки/точного исключения исправлено по наблюдаемому v1 сбою; все текущие обязательные проверки повторены. Fixture slot data явно синтетические; actual Claude не запускался.\nReport: ../../testing/evidence/'+out.name+'/2026-11-16-report.md\nUpdated: '+now+'\nCodex/common-only: verified (documented current scope)\nCodex/common+project: verified (documented current scope)\nClaude/common-only: not run; unverified\nClaude/common+project: not run; unverified\nOverall: unverified\n')
for filename in ['publish.py','close.py']:shutil.copyfile(w/filename,out/('driver-'+filename))
g.save(out/'completion.json',{'source':actual,'protected_unchanged':True,'full_copies_equal':True,'completed':now,'root_suite':r['stdout'].strip().splitlines()[-1]});print('Agent-specific publication request completed; '+r['stdout'].strip().splitlines()[-1])
