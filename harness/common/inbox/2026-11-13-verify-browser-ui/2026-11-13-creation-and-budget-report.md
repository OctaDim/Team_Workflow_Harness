# Подготовка и штатная static-оценка v1

Создано 2026-11-13T01:51:33+03:00, Europe/Minsk. Только стадия создания, not executed.
Версия machine candidate tree: e44135dd017fcab49859c5d2a6bde96bc6768a24be2559c20edb8a357a782c1f.

## Размер файлов

- `candidate/comm-verify-browser-ui/SKILL.md`: 157 слов, 1444 Unicode-символов, 361 static-токенов.
- `candidate/comm-verify-browser-ui/references/coverage.md`: 94 слов, 821 Unicode-символов, 206 static-токенов.
- `candidate/comm-verify-browser-ui/references/fidelity.md`: 168 слов, 1260 Unicode-символов, 315 static-токенов.

Word category always-loaded: N/A, это lazy-скилл, не новое правило.
Полный SKILL ≤200 слов. Штатные bands, thresholds и компоненты:
- trigger_cost_tokens: 35 (good).
- invoke_cost_tokens: 361 (moderate).
- deferred_cost_tokens: 521 (heavy).
- total_tokens: 917 (heavy).

[Raw JSON](2026-11-13-static-v1-budget.json) сохранён без изменения. Собственный полный
комплект ≤1000 static; deferred ≤1000. Метод estimated-static — штатный
Math.ceil(text.length / 4), UTF-16. В этих текстах только BMP, поэтому Unicode
и UTF-16 counts совпадают. Слова — split по пробельным символам полного файла.
Собственный токенизатор, fake baseline или изменённые thresholds не создавались.
Static не равен фактическому расходу/стоимости. Human bodies исключены до чтения.

## Baseline и зависимости

Новый самостоятельный владелец: установленного baseline этого скилла нет; исходный RED поведения не выполнялся.

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
