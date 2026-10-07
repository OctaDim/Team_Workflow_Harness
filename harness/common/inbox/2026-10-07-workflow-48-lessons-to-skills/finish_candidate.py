"""Addressed data/document migration after preserving each operational owner."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent / 'candidate'
COMMON = ROOT / 'harness/common'


def write(path, text):
    p = COMMON / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.strip() + '\n', encoding='utf-8')


write('docs/2026-10-05-compact-authoring.md', '''
# Почему рабочие инструкции компактны

Решение 2026-10-05 разделило обязательные ранние границы и процедуры, выбираемые
по задаче. Распознаваемый сценарий соответствует lazy skill; ранний guard
предотвращает ошибку ещё до выбора. Обязательность алгоритма не делает его
постоянным правилом. Skills-first применяется и к сохраняемому опыту.

Компактность оценивается по сохранённому поведению, а не числу строк/разделов.
Смысловой контракт — применимость, обязательное действие, наблюдаемое соблюдение;
согласования, остановки, missing-data и доступность ресурсов входят в него.
Отложенное чтение требует точного when-read указателя; перенос подробности без
указателя теряет поведение. История ошибки и отчёты имеют отдельные роли.

Сумма всех файлов не означает startup context. Отдельны guards/pointers,
name/description, выбранное body и реально открытые ресурсы. Статическая оценка
токенов не является измеренным расходом или ценой. Сжатие, формат и равенство
копий не доказывают нативное применение.

Текущий владелец авторства: [authoring skill](../skills/comm-create-lazy-claude-codex-skills/SKILL.md).
Методика и gate: [validation](../skills/comm-create-lazy-claude-codex-skills/references/validation-and-publication.md).
Этот документ объясняет решения, не задаёт отдельный порядок действий.
''')
write('docs/2026-10-06-plugin-eval-without-human.md', '''
# Почему plugin-eval запускается с отдельным фильтром

Выбранный 2026-10-06 Node.js launcher исключает README.human.md до чтения и
подсчёта стоимости, не изменяя human files и установленный анализатор.
Прямое чтение и симлинковый обход также отвергаются. Это фильтр известных
файловых API процесса, не OS isolation или общий запрет доступа.

Внешние metric-pack процессы не наследуют фильтр. Обновление анализатора
может изменить API; результаты интеграционной проверки имеют свою версию.
Generic folder analysis не доказывает skill/plugin/native behavior; одиночный
Markdown в plugin-eval 0.1.2 не проходит directory-based budget walk.

Текущая процедура и ограничения запуска:
[evaluation resource](../skills/comm-create-lazy-claude-codex-skills/references/evaluation.md).
Реализация: [launcher](../scripts/plugin_eval_without_human.mjs).
Доказательство границы: [integration test](../testing/tests/test_plugin_eval_without_human.py).
Принятые альтернативы: [decision](../decisions/2026-10-06-plugin-eval-human-filter.md).
Документ объясняет выбор и пределы, не второй workflow.
''')
write('docs/2026-10-05-skill-rule-ownership-contract.md', '''
# Канонический источник и нативные копии

Общие переносимые знания принадлежат common/project; ordinary full native
copies нужны для обнаружения платформой. Редактируемый источник один; копии
восстанавливаются из него. Common независим от исходного приложения; project
зависит от common. Индивидуальные skills — явно выбранный личный режим,
который не ослабляет применимые comm-/proj- требования.

Префикс не меняет системную иерархию агента. Ни один префикс common/project
не решает конфликт за пользователя. Для Claude rules имеют native loading;
Codex читает их по явной стартовой инструкции, ссылка сама не native import.
Link checker проверяет подключения, не публикует и не подтверждает полный набор.

Причина полного сравнения: 2026-10-05 из пяти правил установили три, но проверка
входа прошла. Наборы/bytes/обычные файлы и native behavior — разные свидетельства.
Personal ignore не должен скрывать общие материалы; .gitignore не удаляет историю.

Рабочие владельцы: [ownership rule](../rules/comm-skill-rule-ownership.md),
[inbox workflow](../skills/comm-process-harness-inbox/SKILL.md),
[placement](../skills/comm-create-lazy-claude-codex-skills/references/placement-contract.md),
[validation](../skills/comm-create-lazy-claude-codex-skills/references/validation-and-publication.md).
Решения и прежние разовые исключения: [decision](../decisions/2026-10-05-skill-rule-ownership.md).
Здесь основания и смысл контрактов, не самостоятельная процедура.
''')
write('docs/2026-10-05-protected-entrypoints.md', '''
# Почему входы защищены предупреждающей проверкой

Пользователь 2026-10-05 отменил Git hooks, блокирующие проверки и обязательную
регистрацию исходного текста. Защита AGENTS/CLAUDE — договорённость harness,
а не технический запрет редактору. Узкое исключение допускает согласованное
создание и восстановление стартовых подключений, сохраняя остальные bytes.
Лишний текст CLAUDE сохраняется с предупреждением, не автоматически удаляется.

Checker не требует Git/настроек машины и не блокирует commit. Сравнение с HEAD,
если доступно, не считает сгенерированные стартовые строки изменением настроек.
Без предыдущей версии неизменность произвольных настроек не доказана.
Повреждённый/небезопасный ресурс может дать ошибку: безопасное восстановление
невозможно; это отличается от запрета прямого редактирования.

Текущие рабочие владельцы: [rule](../rules/comm-user-owned-entrypoints.md),
[installation](../skills/comm-install-harness/SKILL.md),
[diagnosis](../skills/comm-install-harness/references/entrypoints.md),
[byte preservation](../skills/comm-preserve-text-line-endings/SKILL.md).
Common содержит реализацию; старый project path — совместимый wrapper.
Прежняя автономная project копия и hooks относятся к отменённым вариантам.
''')
write('docs/2026-10-06-run-tests.md', '''
# Назначение тестового окружения

Переносимый основной набор использует pytest без обязательных сторонних
плагинов; тестовое окружение не требуется для стартового checker. requirements.txt
фиксирует прямые зависимости, requirements.lock — universal compile для Python 3.9
с условными зависимостями. Coverage нужен для сравнения покрытия миграций.

Отдельные редакции inbox тестов могут иметь одинаковые имена; importlib mode
сохраняет их независимость. Основной набор и проверка всех исторических редакций
имеют разную область. Конфигурация существующего проекта не заменяется автоматически.

Команды и сохранение окружения принадлежат
[testing resource](../skills/comm-install-harness/references/testing.md).
Это объяснение состава, не самостоятельная агентская процедура.
''')
write('specs/2026-10-06-structure-and-creation-dates.md', '''
# Структура harness и постоянные даты создания

Дата создания: 2026-10-06. Текущая редакция WORKFLOW-48: 2026-10-07.
Изменение каркаса и польза для всех проектов отдельно подтверждены пользователем.

Одинаковые root categories common/project: base, decisions, testing, rules,
skills, checks, scripts, specs, inbox, docs, handoffs. Testing имеет acceptance,
tests, evidence; планы находятся в docs/plans. Состав нового project задан
base/project-skeleton.json. Lessons исключена; существующий project обычным
стартом не мигрируется. Новый common-only project нейтрален; combined сохраняет
существующий project; project-only не поддерживается.

Skills/ресурсы выражают повторяемые действия, компетенции и применимый опыт;
rules — короткие ограничения до выбора процедуры. Decisions — принятые решения,
контракты, инварианты, ограничения, существенные альтернативы. Base — базовые
контракты/конфигурации/настройки; specs — спецификации; docs — объяснения/
исследования; docs/plans — планы; inbox — временные заявки/кандидаты;
handoffs — незавершённое состояние. Checks/scripts — исполняемые проверки/
служебные программы. Testing/evidence — результаты, ограничения, исходные
свидетельства. Документы и отчёты не отдельные владельцы агентских процедур.

Префикс YYYY-MM-DD файлов знаний specs/docs/decisions/base/handoffs и evidence
означает создание, не обновление. Предметная папка имеет собственную дату;
даты вложенных файлов независимы. Правка сохраняет имя. История с rename/move
или явно записанное создание — основание даты; дата проверки/решения/import
commit/checkout mtime сама по себе не доказательство. Неизвестная старая дата
остаётся неизвестной до адресного согласования. Watchers/hooks/автообновление
и обслуживаемый manifest дат отсутствуют.

Технические исключения: категории, INDEX.md/START.md, README.human.md,
base/project-skeleton.json, Python/Node программы, test_*.py, acceptance.md,
pytest.ini, requirements.txt/requirements.lock, native skill/rule имена и ресурсы.
Каждой папке соответствует human guide с примером; тело не агентский контекст.

Агентское размещение и миграция принадлежат
[material placement](../skills/comm-install-harness/references/material-placement.md);
выбор формы опыта — [inbox skill](../skills/comm-process-harness-inbox/SKILL.md).
Этот файл задаёт согласованный состав и семантику, не отдельный workflow.
''')
write('decisions/2026-10-05-inbox-execution-status.md', '''
# Решение о стадиях и учёте inbox

Принято 2026-10-05; уточнено 2026-10-06. Working owner после WORKFLOW-48:
[inbox workflow](../skills/comm-process-harness-inbox/references/workflow.md).

Причина: проверка материала не равна выполнению заявки; без отдельных статусов
повторная обработка могла повторять завершённую работу. Выбор номера решения
был ошибочно принят за разрешение создать заявку и добавить тесты до отдельного
разрешения выполнить её. Это происхождение контракта, а не новый workflow.

Принятые инварианты:
- Создание, выполнение (включая тесты), публикация и прямой обход inbox —
  разные разрешения. Один явный запрос может покрыть несколько стадий;
  полученное разрешение сохраняется. Номер/путь/срочность не недостающее разрешение.
- Прямой маршрут установлен лишь для названного материала/категории с явным
  разрешением и подтверждением обхода. Проверки и защита входов остаются.
- Inbox временный; постоянный результат понятен независимо от заявки.
  До 2026-10-07 опыт направлялся в категорию lessons; этот маршрут отменён
  [WORKFLOW-48](2026-10-07-skills-first-knowledge.md).
- Каждая заявка имеет контекст пяти полей и отдельный execution status/result/
  reason/update date. Допустимы новая/в работе/выполнена/заблокирована/отклонена.
  Native statuses независимы; publication exception не повышает их.
- Выбранная очередь последовательна от ранней заявки; следующая только после
  закрытия предыдущей. Закрытие означает достигнутый результат и обязательную
  работу либо явное решение закрыть. Кандидат без обязательной публикации
  и состояние «заблокирована» не закрытие. Неясные даты/результаты не выдумываются.
- Выбор пользователя, недостающее разрешение и конфликт требуют ответа;
  silence/time/старое поручение его не заменяют. Известное однозначное
  техническое исправление в разрешённых пределах не требует нового вопроса.

Working owner содержит формы учёта, продолжение каждого статуса, порядок
и сообщения; здесь сохранены принятые ограничения и их причины.
''')
write('decisions/2026-10-07-skills-first-knowledge.md', '''
# WORKFLOW-48: единые владельцы рабочего поведения

Дата создания: 2026-10-07.

Пользователь выбрал убрать lessons и отдельно подтвердил пользу изменения
общего каркаса всем проектам. Планы остаются docs/plans; вариант новой top-level
категории plans не принят. Новый каркас содержит 11 root categories.

Rules/skills с условными ресурсами — единственные источники переиспользуемых
рабочих инструкций и опыта. Skills-first означает сначала нужное будущее
поведение и существующий владелец, а не отдельный skill для каждой ошибки.
Существенные основания/принятые контракты и доказательства сохраняют отдельные
роли. Причина: старый workflow направлял опыт в lessons, а guard требовал читать
там blocker procedure; lazy-first авторство не исправляло сохранение опыта.

Подробный общий blocker workflow нужен для любого permission/decision blocker,
а не только inbox; поэтому у него отдельный lazy skill, guard до выбора остаётся
коротким. Copy drift/permissions развивают существующих владельцев. CRLF
получает отдельный skill по явному scope; исправление и тесты уже существуют.
Процедуры docs/decisions/specs перенесены владельцам; принятые инварианты и
исторические основания сохранены. Архив lessons не создаётся.

Новые проекты используют явный JSON. Текущий project меняется адресно этой
миграцией; ordinary startup сохраняет legacy project и не очищает его сам.
Границы стадий, публикации, защищённых входов, common/project, uv и human
exclusion сохраняются; прежние статусы не приёмка новой версии.

Working owners: [inbox](../skills/comm-process-harness-inbox/SKILL.md),
[authoring](../skills/comm-create-lazy-claude-codex-skills/SKILL.md),
[installation](../skills/comm-install-harness/SKILL.md).
Карта требований/проверки: testing/evidence/2026-10-07-workflow-48-lessons-to-skills.
''')

# Old decisions are explicitly historical where they described the old layout.
for name in ['2026-10-05-harness-architecture.md', '2026-10-05-skill-rule-ownership.md', '2026-10-06-harness-structure.md']:
    p = COMMON / 'decisions' / name
    s = p.read_text()
    first, rest = s.split('\n', 1)
    s = first + '\n\nИстория принятых решений ниже отражает свои даты. Действующая редакция\nмодели знаний и категорий — [WORKFLOW-48](2026-10-07-skills-first-knowledge.md);\nпрежние lessons и механическая блокировка относятся к отменённой модели.\nРабочие процедуры принадлежат rules/skills, не этой исторической записи.\n' + rest
    s = s.replace('по [порядку inbox](2026-10-05-inbox-execution-status.md)', 'по [inbox skill](../skills/comm-process-harness-inbox/SKILL.md)')
    s = s.replace('[подробном контракте](../docs/2026-10-05-skill-rule-ownership-contract.md)', '[placement resource](../skills/comm-create-lazy-claude-codex-skills/references/placement-contract.md)')
    p.write_text(s)
for name in ['2026-10-06-plugin-eval-human-filter.md', '2026-10-04-user-owned-entrypoints.md']:
    p = COMMON / 'decisions' / name
    s = p.read_text().replace('../docs/2026-10-06-plugin-eval-without-human.md', '../skills/comm-create-lazy-claude-codex-skills/references/evaluation.md').replace('../docs/2026-10-05-protected-entrypoints.md', '../skills/comm-install-harness/references/entrypoints.md')
    p.write_text(s)

p = COMMON / 'testing/acceptance/acceptance.md'
s = p.read_text().replace('../../docs/2026-10-05-compact-authoring.md', '../../skills/comm-create-lazy-claude-codex-skills/references/validation-and-publication.md')
s = s.replace('specs/ проверяется только в синтетической разрешённой редакции fixture, не добавляется в действующий состав без решения.', 'Состав текущего каркаса согласован отдельно; новые проекты без lessons, plans в docs/plans. Existing legacy lessons сохраняются обычным стартом.')
p.write_text(s)

for package in ['common', 'project']:
    folder = ROOT / 'harness' / package
    p = folder / 'INDEX.md'
    s = p.read_text().replace('| Ошибки и решения | [lessons/](lessons) |\n', '').replace('| Переиспользуемые процедуры |', '| Процедуры и применимый рабочий опыт |').replace('| Документы и прототипы |', '| Объяснения и исследования |')
    s = s.replace('| Продолжение задачи |', '| Планы | [docs/plans/](docs/plans) |\n| Продолжение задачи |')
    s = s.replace('Заявки inbox могут быть удалены.', 'Рабочее поведение принадлежит rules/skills и условным ресурсам; документы\nсохраняют основания и формальные контракты. До записи опыта skills-first\nпо comm-process-harness-inbox; готовая инструкция не требует новой записи.\n\nЗаявки inbox могут быть удалены.')
    p.write_text(s)
    (folder / 'docs/plans').mkdir(exist_ok=True)
    # Candidate removes them after mapping; live removal still awaits review/gate.
    shutil.rmtree(folder / 'lessons')
    (folder / 'README.human.md').write_text('# Harness\n\nРабочие переиспользуемые инструкции и опыт: skills и короткие rules.\nОснования: decisions/docs/specs/base; доказательства: testing/evidence; планы: docs/plans; временные кандидаты: inbox; незавершённое состояние: handoffs.\nПример: skills содержит применимую процедуру, а testing/evidence сохраняет её фактическую проверку.\n')
    (folder / 'docs/README.human.md').write_text('# Объяснения и исследования\n\nДокументы сохраняют основания без самостоятельных агентских процедур. Планы находятся в plans.\nПример: dated документ объясняет выбор, а соответствующий skill содержит действия.\n')
    (folder / 'docs/plans/README.human.md').write_text('# Планы\n\nСогласованный scope и последовательность работ. Пример: YYYY-MM-DD-topic-plan.md связывает требования с этапами и проверкой.\n')

for skill in (COMMON / 'skills').iterdir():
    if not skill.is_dir():
        continue
    for folder in [skill, *[p for p in skill.rglob('*') if p.is_dir()]]:
        (folder / 'README.human.md').write_text('# Рабочая процедура\n\nКонтекстный скилл и его условно читаемые ресурсы. Пример: SKILL.md определяет применимость, references содержит подробности текущего сценария.\n')
    for native in ['.agents/skills', '.claude/skills']:
        target = ROOT / native / skill.name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(skill, target)
for p in (COMMON / 'rules').glob('comm-*.md'):
    shutil.copyfile(p, ROOT / '.claude/rules' / p.name)

print('Complete migration staged; active source/entrypoints untouched.')
