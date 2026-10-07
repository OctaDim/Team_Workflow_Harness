# Проверка узкого ремонта

Из корня целевого проекта с установленным тестовым окружением:

```sh
.venv/bin/python -m pytest harness/common/testing/tests/test_ensure_entrypoint_links.py harness/common/testing/tests/test_entrypoint_notifications.py harness/common/testing/tests/test_entrypoint_portability.py
```

Если окружения нет, прочитай
`harness/common/skills/comm-install-harness/references/testing.md`; установка
зависимостей через uv, не обходить недоступный инструмент.

Existing tests выполняют реальное восстановление временных файлов:
- LF/CRLF AGENTS: исходные bytes являются неизменным префиксом, вставки имеют
  EOL этого файла; CLAUDE с собственным CRLF сохраняет исходный bridge.
- Уже правильный CRLF импорт без ремонта/ложного предупреждения.
- Повторный запуск сохраняет bytes и не выводит сообщение о повреждении.
- Git HEAD comparison после CRLF link repair без ложного settings warning.
- Common-only и combined, старый project wrapper; независимая project копия
  не создаётся. Unsafe resources и незакрытые fences дают отказ до записи.

Для другого узкого ремонта проверь исходные bytes вне согласованных вставок,
EOL новых строк, распознавание повторного результата и Git comparison, если
история доступна. Отсутствие Git означает непроверенное сравнение с историей,
а не доказанную неизменность. Не выполнять прямой ремонт реальных входов ради
теста: использовать временные fixtures. Историческое CRLF evidence остаётся
в testing/evidence/2026-10-05-entrypoint-crlf-evidence.md; это provenance,
а не успешная проверка текущей версии.
