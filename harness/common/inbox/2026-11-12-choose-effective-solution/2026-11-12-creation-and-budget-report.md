# Подготовка и штатная static-оценка v1

Дата: 2026-11-12, Europe/Minsk. Стадия: создание заявки, не исполнение.
Версия машинного кандидата: 2a808a61a9b8f840bf14f31f17d5959ff210236e6437e52359d4468e9c48f1da.
Полный SKILL.md: 199 слов; тело: 178 слов;
Unicode-символов: 1626. Это lazy-скилл; word bands always-loaded правил
не применяются. Нового постоянно загружаемого правила нет.

Штатные показатели plugin-eval, method=estimated-static:
- Trigger: 38 (good).
- Invoke: 407 (moderate).
- Deferred: 0 (good); ресурсов нет.
- Total: 445 (moderate).

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
