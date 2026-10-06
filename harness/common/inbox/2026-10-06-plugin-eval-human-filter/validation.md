# Проверка кандидата

Дата: 2026-10-06.

Контракт: сохранить прежние требования человеческого правила, добавить однозначный маршрут plugin-eval через фильтр, не переносить описания и не менять статичные входы.

RED: новый интеграционный тест до создания launcher завершился ожидаемым отказом MODULE_NOT_FOUND. GREEN: тот же тест после реализации успешен для настоящего skill/plugin/generic analyzer, включая прямое чтение, симлинковый обход и запрет записи. Этот программный RED/GREEN не заменяет поведенческий RED/GREEN агента.

Codex — не проверено: реальный CLI 0.159.3 запущен для исходного и нового правила, common-only и common+project. Все запуски exit 1 до агентского поведения: failed to initialize in-process app-server client: Read-only file system. Изолированные fixture сохранены в /tmp/plugin-human-native-bp3y96w8; временные пути не являются переносимыми prerequisites.
Claude — не проверено: реальный Claude Code 2.1.260 запущен с новым правилом, exit 1, Failed to authenticate: OAuth session expired and could not be refreshed. Поведенческий RED/GREEN и вся обязательная матрица не подтверждены.
Итог — не полностью проверено; кандидат правила пока не опубликован.

## Общие проверки текущей версии

- `python3 -B harness/common/checks/test_plugin_eval_without_human.py`: успех; реальные skill/plugin/generic анализы, вложенные файлы, прямое чтение и alias, запрет записи, неизменность входов и installed plugin JS.
- `python3 -B -m unittest discover -s harness/common/checks -p test_*.py`: 31/31, успех.
- `git diff --check`: успех.
- Filtered analyze существующего скилла: 86/100, B, прежний fail deferred=1572 сохраняется; человеческие README отсутствуют в компонентах. Объект скилла не изменён, его статус не повышен.
- Generic analyze папки этой заявки: 95/100, A, 0 fail/1 budget warn до добавления данного отчёта; это оценка папки, не native proof правила.
- `skill-creator`: применён для scope/non-duplication и разделения rule/skill; quick_validate N/A, скилл не создавался и не изменялся.
- Нативные результаты: [native-checks.json](native-checks.json). Версии: [manifest.json](manifest.json).

Запрошено исключение для текущего кандидата указателя в `harness/common/rules/comm-human-folder-guides.md` и его одинаковой обычной копии `.claude/rules/comm-human-folder-guides.md`. До явного разрешения публикация этих файлов не выполнена.

## Независимый review

Read-only reviewer проверил launcher, интеграционный тест, процедуру, решение и кандидат правила, выполнил entrypoint check и интеграционный тест. Замечаний корректности или scope не найдено. Проверены используемые plugin-eval 0.1.2 promises API; ограничения ОС/native/future API остаются. Это не замена нативной приёмки двух агентов.

Публикация текущего кандидата и идентичной подключённой копии предложена пользователю с сохранением обеих отметок «не проверено». Ответ ещё не получен; зависимая запись не выполнена.

## Текущая версия после завершения B, 2026-10-06

Предшествующая установка B опубликована и сохранена коммитом cdf8e55.
Все четыре hashes C manifest неизменны; source/native прежнего правила равны.
Интеграционный тест повторно PASS (1 test, 0.369 с).
Четыре текущих Codex turns common/both × explicit/implicit PASS;
[постоянные полные журналы/review](../../checks/codex-human-filter-native.json).
Процедура прочитана перед filtered start/analyze; fixture файлы не изменены.
Bounded generic start/analyze только папки текущего plain rule через launcher:
100/A, без FAIL/WARN. Это статическая общая оценка, не skill/native proof.
Claude — не проверено. Публикация ожидает явного разрешения и подтверждения
текущего SHA-256 100036e5fc40a58ba24d9556dbb916aa311decfba447b50c43d6406309aa288d
по двум путям harness/common/rules/comm-human-folder-guides.md и
.claude/rules/comm-human-folder-guides.md. Snapshot назначения сохранён.
