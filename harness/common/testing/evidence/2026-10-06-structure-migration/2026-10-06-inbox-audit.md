# Проверка всех заявок inbox

Дата создания: 2026-10-06. Проверены все 19 заявок common; project inbox пуст.

Прочитаны исходные требования и результаты каждой заявки, проверены актуальные артефакты и свидетельства. Все заявки выполнены; завершение заявки не означает полной нативной приёмки.

## Исправленные расхождения

- Удалён README.human.md из .claude/rules/octadim, чтобы человеческое пояснение не оставалось в каталоге правил. Байты сохранены без чтения тела в [архиве](2026-10-06-obsolete-native-human-guide.md.gz); [hash и результат](2026-10-06-native-guide-cleanup.json).
- Исправлены пять путей результатов в трёх заявках после миграции; исторические команды и hashes не менялись.
- В заявке о согласовании inbox добавлено датированное уточнение: последний абзац о незавершённой работе относится к остановке до последующей публикации.

## Проверки

Свежий запуск всех семи редакций: 239 PASS, основной набор — 57. Startup и git diff --check PASS. Шесть обычных копий правил и полные копии скилла равны; 51 hash утверждённой версии неизменен, защищённые входы сохранены. В живом Python-коде нет imports unittest. Локальная .venv существует.

[Контроль чувствительности](2026-10-06-inbox-audit-mutation.json): во временном checker снят запрет симлинка входа; исходный тест проходит, мутант падает. Production код не менялся. Прежние шесть сверок coverage и десять mutation-запусков сверены как исторические свидетельства, не новые измерения.

## Заявки и текущие результаты

| Заявка | Подтверждённый текущий артефакт |
|---|---|
| [Расширение процесса создания скиллов и правил](../../../inbox/2026-10-05-authoring-skill-workflows/request.md) | [validation-and-publication.md](../../../skills/comm-create-lazy-claude-codex-skills/references/validation-and-publication.md) |
| [Разделение обязательного порядка и процедуры создания скиллов](../../../inbox/2026-10-05-create-lazy-skill-authoring/request.md) | [SKILL.md](../../../skills/comm-create-lazy-claude-codex-skills/SKILL.md) |
| [Сохранение CRLF при восстановлении входных ссылок](../../../inbox/2026-10-05-entrypoint-crlf/request.md) | [2026-10-05-entrypoint-crlf-evidence.md](../2026-10-05-entrypoint-crlf-evidence.md) |
| [Единый разбор fenced-блоков при проверке входов](../../../inbox/2026-10-05-entrypoint-fenced-code/request.md) | [ensure_entrypoint_links.py](../../../checks/ensure_entrypoint_links.py) |
| [Учёт статуса выполнения заявок](../../../inbox/2026-10-05-inbox-execution-status/request.md) | [2026-10-05-inbox-execution-status.md](../../../decisions/2026-10-05-inbox-execution-status.md) |
| [Полнота установочных копий общих правил](../../../inbox/2026-10-05-rule-copy-drift/request.md) | [test_rule_copies.py](../../tests/test_rule_copies.py) |
| [Подключение и размещение правил](../../../inbox/2026-10-05-rules-entrypoint/request.md) | [comm-entrypoint-links-rule.md](../../../rules/comm-entrypoint-links-rule.md) |
| [WORKFLOW-43: контракт скиллов и правил](../../../inbox/2026-10-05-workflow-43-skills-rules/request.md) | [content-contract.md](../../../skills/comm-create-lazy-claude-codex-skills/references/content-contract.md) |
| [Сократить правило человеческих пояснений без потери поведения](../../../inbox/2026-10-06-compress-human-folder-guides/request.md) | [comm-human-folder-guides.md](../../../rules/comm-human-folder-guides.md) |
| [Все зависимости устанавливать через uv](../../../inbox/2026-10-06-dependencies-through-uv/request.md) | [comm-dependencies-through-uv.md](../../../rules/comm-dependencies-through-uv.md) |
| [Устранить сбой исключения человеческих пояснений из общего поиска](../../../inbox/2026-10-06-fix-human-guide-content-search/request.md) | [comm-human-folder-guides.md](../../../rules/comm-human-folder-guides.md) |
| [Расширение структуры harness и постоянные даты создания](../../../inbox/2026-10-06-harness-structure-and-update-dates/request.md) | [2026-10-06-structure-and-creation-dates.md](../../../specs/2026-10-06-structure-and-creation-dates.md) |
| [Актуализация человеческих пояснений harness](../../../inbox/2026-10-06-human-readme-refresh/request.md) | [2026-10-06-human-readme-refresh-evidence.md](../2026-10-06-human-readme-refresh-evidence.md) |
| [Однозначное согласование inbox и канонической записи](../../../inbox/2026-10-06-inbox-authorization-interpretation/request.md) | [2026-10-05-inbox-execution-status.md](../../../decisions/2026-10-05-inbox-execution-status.md) |
| [Последовательная обработка inbox и остановка для решения пользователя](../../../inbox/2026-10-06-inbox-sequential-user-decisions/request.md) | [comm-skill-rule-ownership.md](../../../rules/comm-skill-rule-ownership.md) |
| [Фильтр README.human.md для plugin-eval](../../../inbox/2026-10-06-plugin-eval-human-filter/request.md) | [plugin_eval_without_human.mjs](../../../scripts/plugin_eval_without_human.mjs) |
| [Два режима установки harness](../../../inbox/2026-10-06-two-installation-modes/request.md) | [project-skeleton.json](../../../base/project-skeleton.json) |
| [Полный перевод тестов с unittest на pytest](../../../inbox/2026-10-06-unittest-to-pytest/request.md) | [run_tests.py](../../../scripts/run_tests.py) |
| [Проверка AGENTS.md и CLAUDE.md: подтверждённая заявка](../../../inbox/protected-entrypoints-request.md) | [comm-user-owned-entrypoints.md](../../../rules/comm-user-owned-entrypoints.md) |

## Оставшиеся исторические ограничения

Три ссылки в старых кандидатных текстах остаются нерабочими: premature-lesson.md и два материала заявки последовательности. Эти файлы сохраняют исходные hashes; их актуальные канонические replacements существуют и проверены. Исторические формулировки project-only, старые числа тестов и прежние hashes не выданы за текущее поведение.

285 человеческих пояснений программно проверены на заголовок, пример и локальные ссылки без вывода тел; ошибок этих требований нет. Все действующие папки пакетов вне inbox имеют пояснения. Шесть пропусков относятся к временным native fixture каталогам; правила этих fixtures исключают human guides. Старый рецепт с обязательными тремя абзацами и без исключения runtime-кэшей описывает прежний снимок, а не актуальную каноническую форму.

Codex — проверено в области этого аудита требований/артефактов, свежих тестов и контроля чувствительности. Прежние нативные результаты учитываются только для своей версии; полная новая нативная проверка всех 19 заявок не заявляется. Claude — непроверенный, не запускался. Итог — непроверенный.

[Машинный протокол](2026-10-06-inbox-audit.json).
