import hashlib,importlib.util,json,os,shutil
from pathlib import Path
w=Path(__file__).parent;loc=json.loads((w/'location-v3.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);source=Path(loc['source']);skill=Path(loc['skill']);sp=importlib.util.spec_from_file_location('g',repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
publication=json.loads((out/'publication.json').read_text());assert publication['source_native_equal'] and publication['full_folder_sets_equal'];r=g.h.run([g.PYTHON,'-m','pytest','-q'],cwd=repo,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'),timeout=300);g.save(out/'installed-root-suite.json',r);assert r['exit_code']==0,r['stdout'][-2000:]
for parent in ['harness/common/skills','.agents/skills','.claude/skills']:assert g.h.snapshot(repo/parent/skill.name)==g.h.snapshot(skill)
assert all((repo/rel).read_bytes()==source.read_bytes() for rel in ['harness/common/rules/comm-confirm-development-workflow.md','.claude/rules/comm-confirm-development-workflow.md'])
before=json.loads((out/'before-other-installed.json').read_text());protected=g.protect();protected['.claude/rules'].pop('comm-confirm-development-workflow.md',None);assert protected==before['protected']
review=json.loads((out/'native-review-final-v3.json').read_text());counts={mode:sum(row['mode']==mode for row in review['case_results']) for mode in ['common','both']};root_result=r['stdout'].strip().splitlines()[-1];now=g.now();text=f'''# Маршрут перед реализацией: короткое правило и lazy-меню

Опубликован candidate-v3: существующий comm-confirm-development-workflow.md
и новый comm-select-development-workflow со всеми ресурсами и human guides.
Всего17 файлов:2 обычные равные копии правила,3 полных равных папки скилла
по5 файлов. AGENTS/CLAUDE, существующий project, общий skeleton и остальные
владельцы сохранены. Индексы и настройки среды не менялись.

Правило определяет аналитику, отдельно разрешённую подготовительную запись,
реализацию пяти видов изменений, смешанные задачи, заранее выбранный маршрут,
продолжение того же набора и новую отдельную реализацию. Аналитика и подготовка
не запускают меню. Выбранный маршрут принимается без повторного запроса;
отдельные разрешения остаются обязательными. Только при нужном меню/разборе
ответа открывается скилл; menu.md и choice.md загружаются по соответствующему
действию. Обязательные CE/no-special формулировки, меню и предупреждение,
модель/effort/delegation и другие согласования сохранены.

Baseline: простые read-only аудиты и подготовительная запись уже прошли без
меню; улучшение относительно этих контролей не заявляется. Диагностика и
предложение остановились перед ненужным выбором. Отдельные текстовые проверки
в обоих режимах подтвердили, что буквальный старый scope включает аналитику.
Пять fresh диагностических контролей и пять текущих повторений сохранены в
baseline-and-form-assessment.json и текущих raw. Первоначальный rule-only v1
сокращён742→572 слова,1531→1190T, но превышения не были автоматически разрешены.
Для текущего исполнения выбрана пара с новым lazy-скиллом; v1 не опубликован.

V2 дал реальный RED: агент прочитал полное предупреждение, затем сократил его
и потерял уточнение, что основной агент executing-plans пишет весь код сам.
V3 задаёт положительный рецепт полного дословного блока. Пять свежих повторов
прошли; затем повторены все текущие обязательные проверки. V2-логи сохранены,
очередь незапущенных v2 вызовов остановлена без зачёта skip как pass. Четыре
первых v3 результата при передаче управления проверены по точным source/native
hashes; происхождение координатора не заменяет проверку версии.

CodexCLI:65 текущих routing-сценариев, common-only{counts['common']}, common+project{counts['both']}.
Все прошли: аналитика/диагностика/предложение/подготовка, пять типов реализации,
смешанный запрос, предвыбранный маршрут, неправильный номер/конфликт/несколько
ответов, продолжения, новая задача, явный нужный навык, отдельные согласования,
явный вызов нового владельца, числовой выбор/исполнитель, короткая/полная
рекомендация. Для двух recommendation-сценариев каждого режима использованы
полные настоящие локальные Superpowers7.0.1, не выдуманные рекомендации.
В недоступном варианте отсутствие SP/CE явно сообщается. Проверены реальные
изменения/отсутствие изменений и действия до выбора, source/native байты,
полное чтение startup и условных ресурсов, native catalogue, а не обещания.

Дополнительно:2 реальных Codex thread по6 CLI resume шагов. После статуса и
уточнения согласованный маршрут сохранился; continue изменил только порт.
Отдельная новая B дождалась своего меню; затем реальный показанный номер
no-special принят без повторного меню и изменён только config. Платформенное
сжатие принудительно не вызывалось: его входная граница проверена отдельными
fresh-context случаями с явно переданной сводкой. Ещё2 независимых read-only
семантических ревью дали PASS; они не заменяют остальные проверки.

Отдельный combined-контроль с ПОЛНОЙ копией существующего project, включая
архивные каталоги, подтвердил сохранение каждого файла по byte hashes.
Обычные изолированные наборы исключают исторические inbox/evidence; это
санитарная граница fixture, не разрешение изменять реальный project.
Рабочий project также полностью сохранён. В record-сценариях исправлена
неоднозначная подготовка папки: необходимые human guides созданы до сеанса,
агент создаёт только request.md. Первоначальные raw сохранены и не выданы за
прохождение этой исправленной среды.

Структура/profile/stock plugin-eval: текущий скилл A95,0 fail/error,
trigger35/invoke206/deferred889/total1130. Heavy-warning ресурсов сохранён;
889 ниже ориентира1000 и порога1200. Правило W178 moderate, C1502, T376;
UTF16 units=C, stock per-file unnormalized estimate; словесные/token исключения
больше не требуются. Generic-оценка правила не считается skill/native proof.
Пакет plugin-eval0.1.2, JSON self-version0.1.0. Целевая часть startup:
старое правило1531T → короткое правило376T +metadata35T =411T. Вся пара со
всеми ресурсами по сумме полей оценщика1506T; сокращение startup не выдаётся
за равное снижение чтения на каждом menu/reply шаге или стоимости сессии.
Все guards, весь доступный логический каталог, дополнительные настоящие SP,
фактические model tool outputs и session usage разделены в context-accounting.

Полные изолированные наборы:195 passed common-only и195 common+project;
повторный startup неизменен, project-only отказал до записи. После публикации:
{root_result}; exit0. Установленный скилл повторно прошёл профиль/stock A95.
GUIDE-body аудит, native catalogue и действия до разрешения проверены отдельно;
исходные результаты и завершённые evidence не перезаписывались.

Ошибки локального драйвера (имя assessment-каталога, переменная resume и синтаксис
аргумента) исправлены без изменения инструкции, исходные выводы сохранены.
Первый финальный judge ошибочно требовал непрерывную строку full-chain:
реальный ответ вставил обязательные согласования дизайна/плана, сохранив порядок
всех стадий и оба исполнения. Исправлена проверка порядка стадий внутри нужного
нумерованного пункта; CE/no-special и полное предупреждение остаются дословными.
Объяснение и старый judge сохранены; окончательный результат —
native-review-final-v3.json. Пропуск, старый успех или lucky retry не использованы.

Точные версии/область/зависимости/исходные байты: before-source.json,
external-dependencies.json, publication-gate.json и publication.json.
Только инструкции и их проверка: проверки запуска приложения/UI неприменимы.
Наблюдение не гарантирует любое будущее поведение модели.

Codex/common-only: проверен в документированной текущей области.
Codex/common+project: проверен в документированной текущей области.
Claude/common-only и Claude/common+project: not run, непроверенные.
Итоговый статус: непроверенный.

Завершено: {now}.
'''
with (out/'2026-11-16-report.md').open('x') as f:f.write(text)
with (Path(loc['request'])/'request.md').open('a') as f:f.write('\n## Execution — результат текущего исполнения\n\nStatus: completed\nResult: candidate-v3 короткого существующего правила и нового comm-select-development-workflow опубликован;17 файлов source/native равны. Codex65 routing случаев,12 реальных resume шагов и2 семантических ревью прошли; A95;195 passed в каждом изолированном режиме и рабочем наборе.\nReason: граница analytics/implementation сделана явной, полное меню отложено в lazy-скилл; предвыбранный маршрут и продолжения сохраняются, остальные разрешения не ослаблены. Объяснённые ошибки candidate/fixture/oracle исправлены и проверены; окончательный judge native-review-final-v3.json.\nReport: ../../testing/evidence/'+out.name+'/2026-11-16-report.md\nUpdated: '+now+'\nCodex/common-only: verified (documented current scope)\nCodex/common+project: verified (documented current scope)\nClaude/common-only: not run; unverified\nClaude/common+project: not run; unverified\nOverall: unverified\n')
g.save(out/'completion.json',{'completed':now,'rule_sha256':publication['rule_sha256'],'skill':publication['skill'],'paths':publication['paths'],'root_suite':root_result,'project_entrypoints_preserved':True,'Codex/common':'verified','Codex/both':'verified','Claude':'not run/unverified','Overall':'unverified'})
for name in ['publish-v3.py','close-v3.py']:
 dest=out/('driver-'+name)
 if dest.exists():assert dest.read_bytes()==(w/name).read_bytes()
 else:shutil.copyfile(w/name,dest)
print('Request completed; '+root_result)
