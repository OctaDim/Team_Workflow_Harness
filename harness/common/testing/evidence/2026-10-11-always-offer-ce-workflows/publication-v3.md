# Публикация v3

Дата: 2026-10-11, Europe/Berlin. Опубликована исправленная и подтверждённая
в чате версия `7b9cddee04cc0fccbcc4aa6972ffbc9eba7a5234ffb2f58795df46ca1d3bf9f8`.
Подготовка и проверки сохранены коммитом `107cc27`.

- Канонический источник: harness/common/rules/comm-confirm-development-workflow.md.
- Равная обычная native-копия: .claude/rules/comm-confirm-development-workflow.md.
- До записи сверены исходные hashes, затем оба файла заменены точными байтами
  [candidate-v3.md](candidate-v3.md). Все восемь installed common/project правил
  имеют полный равный набор native-копий без symlink-компонентов.
- AGENTS.md и CLAUDE.md сохранили исходные hashes. Другие владельцы не менялись.
- [Интеграционная проверка](publication-integration-v3.json): стартовая проверка
  и контракт PASS, pytest 77 passed / 2 прежних skip (8.47s). git diff --check PASS.

В [заявке](../../../inbox/2026-10-10-always-offer-superpowers-ce-workflows/request.md)
установлен completed; подтверждённый объём выполнен. Повторная инвентаризация
common inbox: 43 заявки, все completed; project inbox: 0 заявок.
Предыдущие completed-заявки не переисполнялись и их свидетельства не изменялись.

Публикация непроверенной версии выполнена по подтверждению именно исправленного
текущего состава в чате после представления кандидата и ограничений.
Фактические результаты и границы — [проверка v3](validation-v3.md),
[матрица](native-matrix-v3.json), [статусы публикации](publication-status-v3.json).
Codex в целом **непроверенный**: 20 поведенческих сценариев успешны, четыре
начальных отклонения startup раскрыты, полная CE-цепочка не проверена.
Claude **skip, непроверенный**. Итог **непроверенный**. Публикация и
прохождение интеграционных проверок не повышают эти статусы.
