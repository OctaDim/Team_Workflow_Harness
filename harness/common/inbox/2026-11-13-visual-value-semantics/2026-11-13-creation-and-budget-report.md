# Подготовка и штатная static-оценка v1

Создано 2026-11-13T01:51:46+03:00, Europe/Minsk. Только стадия создания, not executed.
Версия machine candidate tree: f57b355fe56cfc3dcc7e6b1f235ff0e6514751f0a09c915da81324f4daa51a67.

## Размер файлов

- `candidate/comm-preserve-visual-design/SKILL.md`: 198 слов, 1835 Unicode-символов, 459 static-токенов.
- `candidate/comm-preserve-visual-design/references/value-semantics.md`: 162 слов, 1129 Unicode-символов, 283 static-токенов.

Word category always-loaded: N/A, это lazy-скилл, не новое правило.
Полный SKILL ≤200 слов. Штатные bands, thresholds и компоненты:
- trigger_cost_tokens: 47 (good).
- invoke_cost_tokens: 459 (moderate).
- deferred_cost_tokens: 283 (moderate).
- total_tokens: 789 (moderate).

[Raw JSON](2026-11-13-static-v1-budget.json) сохранён без изменения. Собственный полный
комплект ≤1000 static; deferred ≤1000. Метод estimated-static — штатный
Math.ceil(text.length / 4), UTF-16. В этих текстах только BMP, поэтому Unicode
и UTF-16 counts совпадают. Слова — split по пробельным символам полного файла.
Собственный токенизатор, fake baseline или изменённые thresholds не создавались.
Static не равен фактическому расходу/стоимости. Human bodies исключены до чтения.

## Baseline и зависимости

Исходный canonical: 201 слово, 1833 Unicode-символа; trigger_cost_tokens=47 (good), invoke_cost_tokens=459 (moderate), deferred_cost_tokens=0 (good), total_tokens=506 (moderate).
Метаданные и шаги 1–5 сохранены. Число слов сокращено только за счёт заголовка/заключения; invoke сравнивается фактически, экономия расхода не заявляется. Новая нагрузка — условный ресурс и указатель.

Plugin-eval автоматически не включает внешние skill-файлы. Имена зависимых
владельцев и условия использования указаны в SKILL/resources/request.md.
Полный доступный набор и сравнительные суммы собственных компонентов показаны
в общем отчёте тройки после её подготовки; это не замер фактического чтения.
При будущем исполнении учитывать все реально необходимые зависимости и
проверять их доступность/размер отдельно. Старые кандидаты не считаются установленными.

## Инструмент и границы

Команда: node harness/common/scripts/plugin_eval_without_human.mjs
<ordinary-entry> explain-budget <skill-root> --format json.
Entry: /home/octadim/.codex/plugins/cache/openai-curated-remote/plugin-eval/0.1.2/scripts/plugin-eval.js; cache 0.1.2, package.json 0.1.0.
Entry/wrapper hashes в source-snapshot.json; пути/предки обычные, shim не использован.

Сверены комплектность, metadata/name, word goal, ссылки и hashes, не формальная
skill-creator/native проверка. Полные start/analyze/grade, benchmark, RED/GREEN,
Codex/Claude discovery/behavior, оба режима и публикация не выполнялись.
Codex: непроверено. Claude: непроверено. Кандидат: непроверенный.
