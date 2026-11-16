# Публикация политики частоты Git-коммитов

Создан: 2026-10-13T10:44:02+03:00, Europe/Minsk. Отчёт завершён: 2026-10-13T10:45:45+03:00. Публикация выполнена.
Заявка: ../../../inbox/2026-10-13-commit-result-boundaries/request.md.

## Версия и область

SKILL.md: `14b0f014c400cc8e8fa5f403e3b0fa96ebb3ce4bdbe4e1e106a87c10cfcd1473`.
Правило: `1bffa2c007d734f500a380c7501c50a093363a7b639c97aa3a0c0198b0ec13ce`.
Точные машинные снимки: candidate-v2-SKILL.md и candidate-v2-rule.md.

Область публикации: canonical `harness/common/skills/comm-commit-task-stages/`
и полные обычные копии `.agents/skills/comm-commit-task-stages/`,
`.claude/skills/comm-commit-task-stages/`; новое canonical правило
`harness/common/rules/comm-commit-result-boundaries.md` и копия
`.claude/rules/comm-commit-result-boundaries.md`. В каждом skill-каталоге
SKILL.md и human guide, машинных ресурсов нет. Старые evidence, другие заявки,
AGENTS/CLAUDE, project skeleton и внешние plugin cache не изменяются.

Один общий владелец определяет единицу завершённого проверенного результата;
короткое правило нужно до выбора внешнего workflow с частыми commit-шагами.
Самостоятельные результаты сохраняются отдельно, связанные малые уточнения
накапливаются. История и карта прежних требований независимо от inbox:
source-inventory-before-publication.md.

## Проверки текущей версии

- Codex CLI 0.161.0; нативный каталог и неявный выбор навыка в синтетических
  репозиториях. Использован существующий native_probe.py с bwrap: реальный
  проект и домашние инструкции скрыты, запись только в временную фикстуру.
  Model/effort принудительно не задавались; default CLI configuration.
- quick_validate: passed. Тело 187 слов; изменение v1→v2 касается только
  ясности trigger description, без смены политики. Сырые результаты v1 не
  заменены и не считаются проверкой финального trigger.
- plugin-eval 0.1.0 через human-фильтр: final skill A100 без ошибок/предупреждений;
  rule directory A100 — generic анализ, не native proof. Полные JSON рядом.
- Исходная политика на связанных исправлениях: четыре реальных коммита
  (pending draft и три формальных шага). Финальная: один общий коммит.
  В baseline незавершённые уточнения уже дали 0 коммитов; данный сценарий
  не воспроизвёл регрессию. Сводка не подменяет этот факт.
- Основные финальные сценарии: 8/8, по четыре в каждом режиме.
- Посторонний арифметический запрос: 2/2 итоговых прогона, без чтения тела
  commit-навыка и без коммитов. Первый common+project прогон завершился ошибкой
  сервиса `Selected model is at capacity`. Его лог сохранён; новый прогон
  unrelated-r2 на той же модели завершён успешно, версия не менялась.
- Во всех успешных сценариях посторонний staged user.txt оставался в index,
  main не менялся; файлы коммитов принадлежат назначенной задаче, пустых
  коммитов и remote operations нет. Наблюдатель проверяет фактические Git
  commits/snapshots, а не обещания агента; его 0/1 self-check passed.
- Installation-v2: common-only и common+project passed, neutral/preserved
  project, repeat startup без изменений, полные skill-копии, все 9 rule-копий
  одинаковы. Project-only отвергается до записи. До проверки сборки фикстуры
  один запуск системным Python не нашёл pytest; повтор через готовую .venv
  прошёл без установки зависимостей. Итоговая установка проверена после
  изменения description. Первичные результаты установки сохранены отдельно.
- Базовый основной pytest: 77 passed, 2 прежних legacy skips. После публикации
  текущий основной набор также дал 77 passed, 2 прежних legacy skips
  (published-pytest.txt).

| Сценарий | common-only | common+project |
|---|---|---|
| Незавершённые уточнения brainstorm, своевременные сохранения | 0 commits, pass | 0 commits, pass |
| Связанные исправления одного результата | 1 commit, pass | 1 commit, pass |
| Два самостоятельных проверенных результата | 2 commits, pass | 2 commits, pass |
| Явная команда commit now внутри незавершённой работы | 1 commit, pass; исключение объяснено | 1 commit, pass; исключение объяснено |
| Посторонняя арифметика, без загрузки тела навыка | pass | pass после повторного прогона |

Команды: `python3 -B /tmp/commit-policy-checks.py probe <mode> <case> <phase>`;
для установки `.venv/bin/python -B /tmp/commit-policy-checks.py install v2`.
Точные prompts/commands, Git-снимки, exit codes, actual completed reads и usage
записаны в codex-*-events.json, *-observation.json, native-matrix-v2.json и
actual-reads-and-usage.json. Снимки runner v1/v2 находятся рядом. Повтор
unrelated-r2 использует тот же probe с дополнительным именем сценария,
без перезаписи сырого лога. Зависимости не устанавливались.

## Объём и пределы

Статические оценки baseline навыка: metadata 32, invoke 296, deferred 0.
Final: metadata 44, invoke 396, deferred 0; новое правило 137 статических
токенов (always-loaded guard; analyzer классифицирует directory как deferred).
Итого при загрузке owner: 440 оценочных токенов, рост 112 к baseline.
Внешний ce-commit 3.30.5 неизменён: B86, metadata 43, invoke 1185,
ошибка invoke budget остаётся. Его полный source не скрывался из оценки;
прямая цепочка owner+executor — 1668, guard отдельно +137.

CLI usage — фактические счётчики целого turn, включая повторные startup-чтения
и cached input. Они сохраняются отдельно, не выдаются за цену одного чтения
и не используются как доказательство экономии. Human guide bodies не
подключались в оценку. Полный ресурсный объём owner — 0; алгоритм executor
не дублируется.

Целевая частота проверена в 10 итоговых сценариях, но полная нативная проверка
всех инструкций Codex остаётся непроверенной: некоторые трассы объединяли
команды startup/чтения правил до повторного корректного чтения; некоторые
коммиты создавались с -m вместо требуемого executor -F. Полный SP/CE/AS
lifecycle, risky controller/lease, missing executor и failing hook не
прогонялись в этой версии. Это предел проверенной области, не успех таких
непроведённых проверок. Нет blanket proof для всех будущих диалогов.

Codex: целевые сценарии частоты — проверены 10/10; полная проверка инструкции —
непроверенный. Claude: проверка пропущена, непроверенный.
Итоговый статус: непроверенный. Публикация статусы не повышает.

## Итог публикации

Canonical и native файлы опубликованы в указанной выше области, их полные
составы/байты/типы совпадают. published-copy-checks.json фиксирует равенство
всех 9 canonical правил и трёх полных skill-каталогов, действительные ссылки,
Git visibility и неизменность entrypoints/project. Рабочий startup passed.
Основной набор после переноса: 77 passed, 2 прежних legacy skips.
Старые evidence и чужие файлы сохранены. Публикация локальная; push/PR/merge
не выполнялись. Статусы проверки из раздела выше сохраняются.
