---
name: comm-diagnose-harness-entrypoints
description: Use when diagnosing harness startup errors, repaired working copies, entrypoint conflicts or unsafe input paths.
---

# Диагностика старта

До диагностики прочитай файл `harness/common/skills/comm-diagnose-harness-entrypoints/references/entrypoints.md`. Записать корень установки, команду, код возврата и проблемный путь. Определить состояние публикации и вид файла. Для неизвестной копии или конфликтующего защищённого входа сохранить существующие байты, сообщить причину и получить решение пользователя. Для восстановленной копии проверить свежий сеанс. Для установки в двух режимах использовать контекстный lazy скилл `comm-install-harness`. При разрешённом узком ремонте текста до операции прочитай файл `harness/common/skills/comm-preserve-text-line-endings/SKILL.md`.

Результат — воспроизводимая причина, разрешённый способ продолжения и фактический статус проверки.
