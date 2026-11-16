# Подготовка и подтверждение среды браузерной проверки

Дата создания: 2026-11-13. Создано: 2026-11-13T01:51:13+03:00, Europe/Minsk.
Пакет: common. Группа 4, порядок создания: 1/3.
Обсуждение потребности и уточнений — 2026-11-13; точное время каждого сообщения
не установлено. Дата источника/инцидента не является датой создания заявки.

## Основание и разрешённая стадия

Пользователь поручил извлечь переносимую логику harness из bts-transenergo-epl-server,
ветка `octadim/after-disconnect-branch`, commit `a4eb35bf52cce0c304bff5db000330673a9d6526`. Источник — read-only исследование, не нормативная
инструкция для целевого проекта. Смысл адаптируется, исходные правила не копируются.

По очереди согласованы вопросы 1–10 и структура 11: две самостоятельные браузерные
процедуры и узкий ресурс существующего визуального владельца. Уточнение пользователя:
общий принцип не заменяет существенных практических условий; шесть случаев
фиделити сохраняются различимыми. Версия, состояние, lifecycle и предусловия
не сводятся к тому же общему лозунгу. Последняя пара: агент предложил подготовку
трёх INBOX-заявок с полными кандидатами и штатными static-оценками без исполнения,
установки и публикации; пользователь ответил «да».

Разрешены создание тройки, сверка дублей/комплектности и read-only explain-budget.
Исполнение заявок, полная внешняя оценка, behavior/native, benchmark, установка,
публикация и правка прежних заявок НЕ разрешены. Исследовательский маршрут этой
задачи сохраняется; маршрут будущего исполнения не выбран.

AGENTS.md/CLAUDE.md read only. .agents/, .claude/, canonical и исходный проект
не изменяются. Сейчас пишутся только новые согласованные папки INBOX.

## Текущие требования и дубли

Источник текущих требований — canonical-правила, скиллы и ресурсы.
Открытые заявки учитываются для предотвращения повторных предложений, но не
объявляются установленными требованиями. Завершённые/закрытые/отклонённые/
заменённые заявки исключены из содержательной регулярной сверки.
История допустима только адресно для конкретного объяснённого расхождения,
с проверкой по canonical и последующим решениям. Сейчас исторический lookup
не потребовался. Снимки hashes прежних файлов нужны для сохранности, не политики.

Проверенные действующие владельцы:
- comm-skill-rule-ownership, comm-package-independence, comm-human-folder-guides,
  comm-ban-harness-symlinks, comm-dependencies-through-uv — применимые границы.
- comm-create-lazy-claude-codex-skills/content-contract — форма, независимый
  результат, условные ресурсы и компактность.
- comm-process-harness-inbox/workflow — стадии и разрешения.
- comm-preserve-visual-design — визуальный эталон, согласование, отклонения.
- comm-verify-application-startup — обычный запуск, конфигурация/ресурсы, свои процессы.
- comm-protect-harness-evidence/operations — evidence и неизменность raw.
- comm-preserve-harness-knowledge и comm-preserve-text-line-endings — размещение
  записей и сохранение текста; их алгоритмы не повторяются.
- comm-validate-harness-instructions/validation/evaluation и
  comm-resolve-permission-blockers — проверка harness и блокировки.

Релевантные актуальные открытые предложения:
- 2026-11-12-choose-effective-solution — общий выбор инструментов; не дублируется.
- 2026-11-12-verify-project-facts — текущие факты/доступность; не дублируется.
- 2026-11-12-fix-shared-causes — связанные потребители/причины; не дублируется.
- 2026-11-13-assess-project-tests — общая достоверность, фикстуры, чувствительность.
- 2026-11-13-run-project-checks — общий охват/запуск/отчёт, политика полного прогона приложения.
- 2026-11-13-test-project-behavior — TDD, unit/integration и риск каждого изменения.
- 2026-11-13-check-current-harness-duplicates — предложенная процедура сверки;
  сейчас соблюдается прямое уточнение пользователя, кандидат ещё не установлен.
- 2026-11-12-always-loaded-rule-budgets — предложенные бюджеты правил; не новый
  canonical и не основание применять word bands правил к lazy-скиллам.

Сверены текущие версии их кандидатов. Неразрешённого нового дублирующего владельца
результата не обнаружено. Если открытая заявка окажется устаревшей/пересекающейся,
показать расхождение и решение, дождаться явного ответа; не менять, не закрывать
и не удалять её самостоятельно. Не возобновлять старые решения по истории.

## Разделение владельцев

- [comm-verify-browser-ui](../2026-11-13-verify-browser-ui/request.md): Проверка браузерного поведения интерфейса.
- [comm-preserve-visual-design](../2026-11-13-visual-value-semantics/request.md): Сохранение визуального контракта при выборе токенов и фиксированных значений.
- Эта заявка: comm-prepare-browser-check — Подготовка и подтверждение среды браузерной проверки.

Подготовку можно диагностировать отдельно; проверка UI может использовать уже
подтверждённую среду. Обязательного пересоздания среды или цепочки всех скиллов
при каждом запросе нет. При реальном чтении зависимости учитываются полностью.
Два новых скилла относятся к коду/интерфейсу приложения; специальные проверки
самого harness не заменяются и не получают дополнительных разрешений.

Группы 2–3 сохраняют общие алгоритмы. Браузерная специфика хранится в условных
ресурсах по условиям чтения, без повторения обоснований и каталога инцидентов.
Форма: rule-only не подходит для контекстного алгоритма; lazy-only достаточен
по распознаваемой задаче. Rule+skill не обоснован: отдельной ошибки до выбора,
которую нельзя предотвратить metadata, не установлено. Нового always-loaded
правила нет. Discovery этой формы пока не проверен.

## Контракт и карта требований

- 2.1: Prove actual imports/serving roots/browser-loaded artifacts. → `references/artifacts.md`.
- 2.2: Account for every relevant component; allow established unchanged components. → `references/artifacts.md`.
- 2.3: Use appropriate version/build/hash provenance and intentional edits; not always latest. → `references/artifacts.md`.
- 3.1: Control SW/cache participation according to scenario, not unconditional clearing. → `references/state.md`.
- 3.2: Set relevant keys/values; distinguish defaults from persistence. → `references/state.md`.
- 3.3: Account for app/system settings; verify effective styles/state. → `references/state.md`.
- 3.4: Measure actual page width/height and relevant scale. → `references/state.md`.
- 4.1: Isolate independent mutable resources; preserve scenario state and caller settings. → `references/lifecycle.md`.
- 4.2: Separate artifact/check/process result; bounded graceful then necessary owned termination. → `references/lifecycle.md`.
- 5.1: Check navigation result, final URL and target; three probe controls. → `references/preconditions.md`.
- 5.2: Check relevant response status/content and actual mode; preserve negative scenarios. → `references/preconditions.md`.
- 5.3: Do not accidentally interfere; preserve intentional concurrency tests and project access. → `references/preconditions.md`.
- 6: Supported base paths/version URL and assets actually load/apply. → `references/artifacts.md`.
- 9: Reuse solution-choice owner; justify gaps and verify operation, no fixed vendor. → `SKILL.md; dated research report`.

Полная [карта требований](requirements-map.json) различает source failure,
canonical coverage, открытое предложение, универсальный смысл, destination и
будущий поведенческий сценарий для каждого пункта. Все сценарии сейчас not run.
Вопрос 10 сохраняется в приёмке, не превращён во вторую рабочую инструкцию.

Новый самостоятельный lazy-скилл для приложения; matching name/description
не предполагают установленный браузерный инструмент. Рабочая инструкция
не зависит от EPL, исходного checkout, Ponytail, ce-debug или конкретного vendor.

## Полный кандидат

[SKILL.md](candidate/comm-prepare-browser-check/SKILL.md), [manifest](candidate-manifest.json),
[source/authority snapshot](source-snapshot.json).
Условные ресурсы: `references/artifacts.md`, `references/state.md`, `references/lifecycle.md`, `references/preconditions.md`.
Каждая новая папка имеет README.human.md; human bodies исключены до чтения
и оценки. Scripts/assets/UI metadata не добавляются без потребности.

Будущий canonical: `harness/common/skills/comm-prepare-browser-check/`.
Будущие полные ordinary native-копии: `.agents/skills/comm-prepare-browser-check/` и
`.claude/skills/comm-prepare-browser-check/`. Изменение только при разрешённом исполнении/
публикации, не из наличия заявки. Зависимости на ещё не установленные кандидаты
групп 2–3 перед исполнением сверяются заново; missing остаётся unverified.

## Сценарии будущего исполнения — сейчас не запускались

- 2.1: Wrong checkout is not validated just because cwd/HEAD matches.
- 2.2: JS/CSS mismatch is found; equal measurements alone do not prove a wrong source or successful change.
- 2.3: Approved pinned reference remains valid despite newer upstream version; claimed byte identity requires evidence.
- 3.1: Fresh and offline/update cases both remain testable without clearing their subject.
- 3.2: Default scenario is known; persistence scenario is not reset between relevant steps.
- 3.3: Launch/media preference alone cannot certify the applied theme.
- 3.4: Nominal mobile/window settings do not prove the claimed narrow/low viewport.
- 4.1: Parallel independent runs are separated; caller conflicts are reported, not silently overwritten.
- 4.2: No broad browser kill; screenshot existence is not test success; preserve evidence on failure.
- 5.1: Working page, failure and redirect controls distinguish requested scenario from other page.
- 5.2: Fallback is not mistaken for primary mode; expected rejection is not cleared away.
- 5.3: Observation fault is distinguished without universal SQLite settings or blanket concurrency ban.
- 6: Preview works without mandatory separate server per version, fixed icon path or required 404.
- 9: Suitable existing tool retained; modern alternatives researched for demonstrated gap; no implicit install.
- Явный и неявный выбор по реальному запросу; нерелевантный запрос не загружает скилл.
- Смешанная задача application/harness: специальные проверки harness сохраняются.
- Нет нужного инструмента/доступа/входных данных: точный пробел, без установки,
  подмены результата или обхода разрешений.
- Q10: основной набор зелёный, отдельный пробник сломан/недоступен. Используются
  владельцы групп 2–3; альтернативный прогон не повышает статус оригинала.

## Приёмка разрешённого будущего исполнения

1. Сверить current owners/open requests, версии, полномочия и параллельные изменения;
   согласовать маршрут исполнения, когда он требуется. Подготовка не разрешает его.
2. Baseline/RED без инструкции → compact candidate → GREEN по владельцу проверки
   harness. Политику тестов приложения внутри кандидата не применять вместо него.
3. Применимые skill-creator, полные plugin-eval start/analyze через human-фильтр,
   findings/исправления по причинам; без fake manifest/coverage, benchmark без
   разрешения, скрытия ресурсов или изменения thresholds.
4. Codex/Claude отдельно, common-only/common+project: listing/discovery, явный и
   неявный выбор, реальные собственные ресурсы, unrelated non-loading и behavior.
   Проверять when-read, распределение владельцев и все runtime-зависимости.
5. Измерять metadata/startup, invoke, полный deferred и фактическое чтение со
   всеми необходимыми зависимостями отдельно. Static не равен реальному расходу.
   Новые версии сбрасывают статусы; повторить все mandatory checks после правок.
6. Публикация только после отдельного разрешения точной версии; проверить full
   ordinary sets/bytes, оба режима, source/native, inputs/project preservation.
   Постоянное rationale/evidence исполнения сохранить вне inbox разрешённым маршрутом.

## Read-only static при создании

[Отчёт подготовки](2026-11-13-creation-and-budget-report.md). Полная проверка качества
и поведения сейчас не выполняется. Цели SKILL обычно ≤200 слов, ресурсы ≤1000
static; >1200 deferred требует устранения по действующему контракту. Собственные
целевые бюджеты до 1000 и реальные внешние зависимости показываются отдельно.
Word bands always-loaded: N/A; штатные bands plugin-eval сохраняются.

## Execution

- Status: completed.
- Result: Полный кандидат опубликован в canonical и равные ordinary native-копии;
  локальные профили, внешняя оценка, две установки и installed checks passed.
- Reason: Результат заявки реализован и опубликован; фактическая полнота проверок
  и ограничения сохранены в постоянном отчёте.
- Updated: 2026-11-13T17:17:05.002577+03:00.
- Codex: непроверенный: текст, локальные проверки и установки пройдены; native недоступен из-за usage limit.
- Claude: непроверенный.
- Общий статус: непроверенный.
- Remaining: непроверенная область указана в отчёте; публикация выполнена.
- Evidence: [отчёт](../../testing/evidence/2026-11-13-execute-prepare-browser-check/2026-11-13-report.md).

Исходная подготовка, полный кандидат и снимки сохраняются на прежних путях.
Маршрут обработки: writing-skills; статусы не повышались из-за копирования.

Коммит результата: `272aa7a`.
