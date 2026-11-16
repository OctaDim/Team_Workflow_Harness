# Подготовка и штатная static-оценка v1

Создано 2026-11-13T01:51:14+03:00, Europe/Minsk. Только стадия создания, not executed.
Версия machine candidate tree: 8e2475ad608ebfc17cc997f2eb4851568705fefbd4f02ea2be942545687a95d4.

## Размер файлов

- `candidate/comm-prepare-browser-check/SKILL.md`: 87 слов, 974 Unicode-символов, 244 static-токенов.
- `candidate/comm-prepare-browser-check/references/artifacts.md`: 97 слов, 745 Unicode-символов, 187 static-токенов.
- `candidate/comm-prepare-browser-check/references/lifecycle.md`: 72 слов, 556 Unicode-символов, 139 static-токенов.
- `candidate/comm-prepare-browser-check/references/preconditions.md`: 81 слов, 702 Unicode-символов, 176 static-токенов.
- `candidate/comm-prepare-browser-check/references/state.md`: 92 слов, 797 Unicode-символов, 200 static-токенов.

Word category always-loaded: N/A, это lazy-скилл, не новое правило.
Полный SKILL ≤200 слов. Штатные bands, thresholds и компоненты:
- trigger_cost_tokens: 40 (good).
- invoke_cost_tokens: 244 (moderate).
- deferred_cost_tokens: 702 (heavy).
- total_tokens: 986 (heavy).

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
