---
name: comm-process-harness-inbox
description: Use when recording experience in harness, creating an inbox request, processing one or several requests, or updating their execution status. Handles permission stages and closure; skill/rule authoring also uses its authoring skill.
---

# Обработка harness inbox

До записи или начала обработки прочитай [workflow](references/workflow.md):
разрешения, состав заявки, статусы и закрытие. Определи пакет common/project
по содержанию; обычную просьбу сохранить сначала направляй в inbox.

Выбранные заявки выполняй по одной от ранней к поздней, учитывая прежние
статусы. Не начинай следующую до закрытия предыдущей. Если для развилки или
конфликта нужен ответ, останови зависимые действия; молчание не ответ.
Однозначную техническую ошибку исправляй в уже разрешённых пределах.

Для создания/изменения/проверки/публикации скилла или правила до действия
открой из корня проекта `harness/common/skills/comm-create-lazy-claude-codex-skills/SKILL.md`.
Готовый кандидат без обязательной публикации не закрывает заявку.
Пример: «создай заявку и выполни» разрешает обе стадии, но не публикацию
непроверенной версии. Сохраняй результат вне inbox и обновляй учёт по workflow.
