# Подготовка и штатная static-оценка v1

Дата: 2026-11-13, Europe/Minsk. Создано: 2026-11-13T00:14:11+03:00.
Стадия — создание заявки; исполнение не начиналось.

Состав/хеши: [манифест](candidate-manifest.json).
Версия candidate tree: a998cec9ca43632cd979c240036b6b62e6c97e7dd17fe83c6a04a3d160db294f.

## Объём

- candidate/comm-run-project-checks/SKILL.md: 162 слов, 1368 Unicode-символов, штатная static-оценка 342 токенов.

Полный SKILL ≤200 слов. Категория по словам always-loaded: N/A, это lazy-скилл,
нового постоянно загружаемого правила нет. Реальные штатные категории:
- trigger_cost_tokens: 25 (good).
- invoke_cost_tokens: 342 (moderate).
- deferred_cost_tokens: 0 (good).
- total_tokens: 367 (moderate).

Полный собственный static total ≤1000; deferred ≤1000. Штатные thresholds
не менялись. Trigger — доступные при выборе metadata, invoke — полный SKILL,
deferred — все собственные машинные ресурсы. Human guide тела исключены до
чтения common launcher. Trigger и invoke не являются замером реального расхода;
метод estimated-static, штатный Math.ceil(text.length / 4) считает UTF-16-единицы.
В кандидатах только BMP, поэтому Unicode/UTF-16 counts совпадают. Unicode-число
и слова подсчитаны отдельно; отдельный токенизатор не создавался.

[Исходный JSON](2026-11-13-static-v1-budget.json) сохраняет tool result без изменений. Команда:
`node harness/common/scripts/plugin_eval_without_human.mjs <ordinary-entry> explain-budget <candidate-skill-root> --format json`.
Entry: /home/octadim/.codex/plugins/cache/openai-curated-remote/plugin-eval/0.1.2/scripts/plugin-eval.js. Каталог пакета 0.1.2; package.json version 0.1.0.
Entry/wrapper hashes — в снимке подготовки. Не использован symlink shim.

## Граница результатов

Проверены комплектность, имена/metadata, лимит слов и состав/hashes кандидата;
это подготовительная сверка, не skill-creator quick_validate и не оценка
discovery/качества поведения. Полные start/analyze/grade, benchmark, RED/GREEN,
native Codex/Claude, common-only/common+project и публикация НЕ выполнялись.
Codex: непроверено. Claude: непроверено. Кандидат: непроверенный.

TDD-кандидат использует двух других владельцев: полный реестр доступного
контекста и сумма штатных компонентов будут отдельно показаны в общем отчёте
подготовки тройки после завершения её записи. Собственная оценка plugin-eval
не включает внешние файлы автоматически и не доказывает их доступность.
Разрешения и процедуры проверки harness сохраняются.
