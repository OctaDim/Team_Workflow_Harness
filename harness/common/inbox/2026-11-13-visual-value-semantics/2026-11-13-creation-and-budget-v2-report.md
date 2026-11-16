# Подготовка визуального кандидата v2

Создано 2026-11-13T01:56:42+03:00, Europe/Minsk. Стадия создания, not executed.
Текущая [версия/manifest](candidate-v2-manifest.json): e33def235fccb357b00e9c7a7f0ce937880705e15529133a881567bcfbfcde69.

- `candidate/comm-preserve-visual-design/SKILL.md`: 200 слов, 1848 Unicode-символов, 462 static-токенов.
- `candidate/comm-preserve-visual-design/references/value-semantics.md`: 162 слов, 1129 Unicode-символов, 283 static-токенов.

- trigger_cost_tokens: 47 (good).
- invoke_cost_tokens: 462 (moderate).
- deferred_cost_tokens: 283 (moderate).
- total_tokens: 792 (moderate).

SKILL ≤200 слов; собственный полный static total ≤1000. Word bands always-loaded:
N/A. Штатные категории сохранены; метод estimated-static, Math.ceil(text.length / 4),
UTF-16. Здесь BMP-only, Unicode count совпадает. Слова — split полного файла.
Это не замер расхода/стоимости; собственный tokenizer и fake baseline не создавались.

V2 восстанавливает явное требование держать product-specific business rules в
project. Метаданные и пять шагов визуального согласования сохранены дословно.
Сохранены [полная v1](candidate-v1-snapshot.json), первоначальные manifest,
raw budget и отчёт; они описывают v1, не текущий файл.
[Текущий raw budget](2026-11-13-static-v2-budget.json).
[Canonical static baseline](2026-11-13-static-canonical-before-budget.json) не менялся:
201 слово, 1833 символа; trigger 47, invoke 459, deferred 0, total 506.
Структура токенных показателей не является RED поведения; экономия расхода не заявлена.

Команда: node harness/common/scripts/plugin_eval_without_human.mjs
<ordinary-entry> explain-budget <candidate-skill-root> --format json.
Entry /home/octadim/.codex/plugins/cache/openai-curated-remote/plugin-eval/0.1.2/scripts/plugin-eval.js; cache 0.1.2, package.json 0.1.0.
Пути/предки обычные, entry/wrapper hashes сохранены. Human bodies исключены до чтения.

Полные skill-creator/start/analyze/grade, native Codex/Claude, discovery/behavior,
оба режима, benchmark, установка и публикация не выполнялись.
Codex: непроверено. Claude: непроверено. Кандидат: непроверенный.
Внешние зависимости не включаются plugin-eval автоматически; реестр и сравнение
показаны в общем отчёте, фактические чтения ещё не измерены.
