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
