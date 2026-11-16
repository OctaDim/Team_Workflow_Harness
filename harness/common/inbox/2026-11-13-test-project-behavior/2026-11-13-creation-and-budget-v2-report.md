# Подготовка TDD-кандидата v2

Создано: 2026-11-13T00:20:55+03:00, Europe/Minsk. Стадия создания, not executed.
Полный SKILL: 150 слов, 1280 Unicode-символов.
Категория по словам always-loaded: N/A — lazy-скилл, новое правило отсутствует.

- trigger_cost_tokens: 29 (good).
- invoke_cost_tokens: 320 (moderate).
- deferred_cost_tokens: 0 (good).
- total_tokens: 349 (moderate).

Штатный метод estimated-static: Math.ceil(text.length / 4), UTF-16; здесь только
BMP-символы. Формула, thresholds и tool не менялись. Static — не расход/стоимость.
Собственный total ≤1000, deferred=0.

Изменение v2: условия, права, зависимости, форматы и настройки запуска прямо
классифицированы как поведенческие изменения согласно решению пользователя.
Согласованные обязанности не сокращены. Для сравнения сохранены
[полный v1](candidate-v1-snapshot.json), [v1 manifest](candidate-manifest.json),
[v1 budget](2026-11-13-static-v1-budget.json) и первоначальный отчёт.
Текущие [v2 manifest](candidate-v2-manifest.json), [v2 raw budget](2026-11-13-static-v2-budget.json).

Команда: node harness/common/scripts/plugin_eval_without_human.mjs
<ordinary-entry> explain-budget <candidate-skill-root> --format json.
Entry: /home/octadim/.codex/plugins/cache/openai-curated-remote/plugin-eval/0.1.2/scripts/plugin-eval.js; cache package 0.1.2, package.json 0.1.0.
Пути/предки обычные, shim не использовался, human guides исключены до чтения.
Entry/wrapper hashes сохранены в source-snapshot.json.

Полные проверки skill-creator, plugin-eval start/analyze/grade, native discovery,
behavior, оба агента/режима, benchmark и публикация не выполнялись.
Codex: непроверено. Claude: непроверено. v2: непроверенная.
Собственные budgets не включают внешние файлы автоматически. Суммы доступного
контекста и зависимостей показаны в общем отчёте подготовки; фактические чтения
ещё не измерены. Специальные требования проверки harness сохраняются.
