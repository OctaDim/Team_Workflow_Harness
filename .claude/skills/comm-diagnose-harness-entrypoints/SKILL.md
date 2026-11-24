---
name: comm-diagnose-harness-entrypoints
description: Use when diagnosing harness startup errors, repaired working copies, entrypoint conflicts or unsafe input paths.
---

# Диагностика старта

До диагностики прочитай файл `harness/common/skills/comm-diagnose-harness-entrypoints/references/entrypoints.md`. Запиши корень установки, команду, результат и затронутые пути. Определи состояние публикации и вид файла. Укажи причину отказа, результат восстановления и полный Git ID резерва, если он создан. После восстановления проверь свежий сеанс. Для установки в двух режимах используй контекстный lazy скилл `comm-install-harness`.

Результат — воспроизводимая причина, разрешённый способ продолжения и фактический статус проверки.
