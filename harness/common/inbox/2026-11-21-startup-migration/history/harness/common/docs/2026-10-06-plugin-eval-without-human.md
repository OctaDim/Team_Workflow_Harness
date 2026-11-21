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
[evaluation resource](../skills/comm-validate-harness-instructions/references/evaluation.md).
Реализация: [launcher](../scripts/plugin_eval_without_human.mjs).
Доказательство границы: [integration test](../testing/tests/test_plugin_eval_without_human.py).
Принятые альтернативы: [decision](../decisions/2026-10-06-plugin-eval-human-filter.md).
Документ объясняет выбор и пределы, не второй workflow.

Указатели на текущих владельцев обновлены 2026-10-08; даты и исторические
результаты выше не изменены этим переносом.
