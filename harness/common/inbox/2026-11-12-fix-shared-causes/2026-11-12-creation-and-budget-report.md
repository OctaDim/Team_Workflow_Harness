# Подготовка и штатная static-оценка v1

Дата: 2026-11-12, Europe/Minsk. Стадия: создание заявки, не исполнение.
Версия машинного кандидата: 6b01bcf87f22122ba19e52c20c2fae8da3efc98fb28943eaff969d8a85ca2092.
Полный SKILL.md: 198 слов; тело: 174 слов;
Unicode-символов: 1488. Это lazy-скилл; word bands always-loaded правил
не применяются. Нового постоянно загружаемого правила нет.

Штатные показатели plugin-eval, method=estimated-static:
- Trigger: 38 (good).
- Invoke: 372 (moderate).
- Deferred: 0 (good); ресурсов нет.
- Total: 410 (moderate).

[Сырой штатный JSON](2026-11-12-static-v1-budget.json) сохраняет thresholds
и компоненты. Оценщик — Math.ceil(text.length / 4), UTF-16-единицы JavaScript;
это не реальная токенизация или расход сессии. Новый tokenizer не создавался,
пороги не менялись. Analyze/score/grade, benchmark, native и поведение сейчас
не проверялись; кандидат непроверенный.

Команда: node harness/common/scripts/plugin_eval_without_human.mjs
<ordinary-installed-plugin-eval.js> explain-budget <candidate-skill-root>
--format json. Проверенный entry:
/home/octadim/.codex/plugins/cache/openai-curated-remote/plugin-eval/0.1.2/scripts/plugin-eval.js.
Каталог пакета 0.1.2; package.json сообщает 0.1.0. Human guide тела исключены
common launcher до чтения и оценки. Полные candidate-файлы и hashes сохранены;
рабочие/native инструкции не публиковались.
