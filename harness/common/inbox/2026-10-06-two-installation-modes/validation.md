# Проверка перехода на два режима

## Финальная компактная версия, 2026-10-06

Manifest: `388a37a1654462001cdb2dcf1742e50688a93efd179d8580ee6782f3154ea3ea`.
Ресурсы сокращены 1464 → 1198 estimated-static tokens, metadata/body 47/397
не менялись. Реальный расход не измерен. evaluate-skill start/analyze markdown
и JSON + compare: 86/B → 95/A, бюджет FAIL → WARN, ошибок нет. Coverage INFO
не требует новой инфраструктуры для текстового навыка. Снимок 1464 и comparison
сохранены рядом; это статический RED–GREEN, не заявляется как поведенческий RED.

Сохранены контракты содержания/владения, отсутствие симлинков, ресурсы/инструменты,
две установки/негативный project-only, явный источник каркаса, две отдельные
санкции новой категории, все нативные проверки и gate публикации. Основной
SKILL.md и алгоритмы проверки не изменены; три полные копии ресурсов равны.
quick_validate.py PASS, 38/38 unittest PASS, все 30 hashes manifest PASS.

Повтор Codex использовал разрешённый сервис/кандидат и четыре read-only turns.
Prompt implicit теперь просит подготовить агентские инструкции, не называет
навык; оба implicit выбрали локальный skill до чтения rules и прочитали ресурс.
В первом сообщении каждого turn нативный каталог показал имя/описание навыка
до файлов; первой командой выполнен обязательный старт, exit 0. Изоляция
маскирует весь исходный проект и авторские глобальные инструкции. Ответы
сохранили все продуктовые ограничения; поиск недоступных глобальных helpers
некоторыми turns завершился exit 1, корректно раскрыто, это не скрытая установка
и не успех отсутствующего инструмента. Итоговый проект ответа агенты правильно
отметили непроверенным: он отдельно не выполнялся.

[Полные журналы и ручной review](../../testing/evidence/2026-10-06-two-installation-modes/2026-10-06-codex-two-modes-final-compaction.json)
сохранены вне inbox. Claude не запускался с кандидатными материалами: локальная
проверка авторизации показала expired, exit 1. Codex текущие сценарии PASS;
Claude не проверен; публикация по-прежнему не разрешена. Нижележащие записи
содержат исторические версии и не являются текущей приёмкой.

## Актуальный повтор Codex после явного разрешения передачи, 2026-10-06

Пользователь: «разрешаю вне песочницы. разрешаю передачу». Конкретная команда
вне песочницы разрешена и выполнена, используя текущую авторизацию CLI;
Claude и публикация не запускались. Версия manifest не менялась:
`aef342a0e63d2cac713169c109eb3d9bd04a0542a36c43f06e6f91b3a2cf4830`.

Первые четыре turns завершились exit 0, но review журналов выявил ошибку
тестового скрипта: REQUEST.parents[2] скрывал только repository/harness.
RED подтвердил несовпадение с корнем проекта. Исправлено на parents[3] и
добавлен выполняемый assert расположения; GREEN и все финальные журналы
подтвердили скрытие всего исходного проекта. Старые turns сохранены с
префиксом codex-before-root-isolation и не входят в итоговую изолированную приёмку.

| Режим | Вызов | Exit / turn | Собственный ресурс скилла | Вывод |
|---|---|---|---|---|
| common-only | explicit | 0 / completed, 48.18 с | прочитан | ограниченный сценарий PASS |
| common-only | implicit | 0 / completed, 47.32 с | не прочитан | implicit selection не подтверждён |
| common+project | explicit | 0 / completed, 47.73 с | прочитан | ограниченный сценарий PASS |
| common+project | implicit | 0 / completed, 45.59 с | не прочитан | implicit selection не подтверждён |

Проверены фактические command_execution и ответы: первая команда — обязательный
старт (exit 0); все команды успешны; explicit читает .agents/skills/.../SKILL.md
и свой references/validation-and-publication.md. Во всех ответах корректны
два режима, отрицательный project-only, явный источник каркаса, остановка specs
до двух решений пользователя и gate непроверенной публикации. Команд чтения
тел README.human.md не наблюдалось. Implicit requirements-only запрос обслужен
через правила harness; это не доказательство дефекта маршрутизации скилла при
реальном авторинге, но и не успешная проверка его неявного выбора. Самостоятельный
native listing отдельно не проверялся, статус Codex в целом не повышен.

Полные актуальные [журналы и review](../../testing/evidence/2026-10-06-two-installation-modes/2026-10-06-codex-two-modes-native-retry.json)
сохранены вне временного inbox. AGENTS.md/CLAUDE.md совпадают с HEAD; все 30
кандидатных hashes совпадают с manifest. Claude, deferred budget FAIL и gate
публикации остаются. Прежние сообщения об отказе сетевого запуска ниже — история,
а не актуальный результат повторной проверки.

## Повторный запрос Codex CLI вне песочницы, 2026-10-06

Пользователь поручил повторить нативную проверку Codex CLI, запросив запуск
конкретной проверочной команды вне песочницы либо другие разрешения. Запрошен
`exec_command` с `sandbox_permissions=require_escalated`: Python загружает
`check_native.py`, сверяет текущий manifest и вызывает
`probe('codex', 'common', 'explicit')`; только при завершённом turn запускает
common/implicit, both/explicit и both/implicit. Claude не вызывается.
Запрос объяснял передачу инструкций кандидата и проверочного prompt сервису Codex,
временный runtime, сохранение логов и отсутствие публикации.

Автоматическая проверка разрешений отклонила конкретную команду до создания
процесса: проверка отправляет частные файлы/инструкции кандидата сервису Codex
с локальной авторизацией, а пользователь ещё не разрешил явно передачу именно
этого содержимого этому адресату. Это отказ исполнения, не результат Codex CLI;
новых native logs и успешного сценария нет. Отказ не обходился.

Для следующего запуска требуется явное разрешение передать сервису Codex
содержимое временного проверочного комплекта из
`harness/common/inbox/2026-10-06-two-installation-modes/candidate/`
(выбранные harness/common, harness/project, .agents/skills, .claude/skills и
.claude/rules) и два проверочных prompt из `check_native.py`, используя текущую
авторизацию CLI. Исходный проект и глобальные инструкции скрываются bwrap;
README.human.md не загружаются в агентский контекст. Разрешение такой проверки
не означает разрешения публикации или запуска Claude. Codex остаётся непроверенным.

Дата: 2026-10-06. Объект — кандидат внутри этой заявки, а не опубликованная версия harness. План: ../../docs/plans/2026-10-06-1014-feat-two-installation-modes-plan.md.

## Версия и сохраняемый контракт

Точные изменяемые пути, размеры и SHA256 каждого файла: [candidate-manifest.json](candidate-manifest.json). SHA256 manifest: `aef342a0e63d2cac713169c109eb3d9bd04a0542a36c43f06e6f91b3a2cf4830`. В нём 30 предложенных изменений; служебные человеческие пояснения папки candidate в публикацию не входят. Исходные AGENTS.md/CLAUDE.md совпадают с HEAD; Git-конфигурация и .gitignore не изменялись.

Common обязателен. Перенос только common создаёт десять ранее согласованных пустых категорий project по явному base/project-skeleton.json, нейтральные INDEX/START и человеческие пояснения. Перенос обоих пакетов сохраняет существующий project без перезаписи или автоматического дополнения по новому шаблону. Project-only — только отрицательный контроль. Совместимый старый путь проектной проверки вызывает common, чтобы сохранить старую команду защищённого входа; в новом каркасе он не создаётся.

Состав шаблона не выводится из project. Новая категория требует отдельной common inbox-заявки, отдельного явного решения пользователя и отдельного явного подтверждения её пользы для всех проектов. Агент может предложить, но до обоих ответов её не включает. Ответа или такого разрешения на specs/ нет; specs/ использовалась только в синтетическом временном тесте, в кандидатный шаблон не добавлена. Следующие новые проекты получают разрешённое обновление; существующие автоматически не дополняются.

## План и независимый review

ce-doc-review: coherence, feasibility и scope. Scope: замечаний нет. Coherence указал проблему удаления пути диагностики project-only; feasibility — старую стартовую команду защищённого AGENTS.md. Оба замечания разрешены коротким совместимым вызовом common; KTD3/U2 уточнены в плане.

Финальный review реализации выявил P2: симлинк каталога common/common-checks мог исполнить внешний код через shim до проверки. Добавлен отказ по симлинкам файла и его предков до runpy. Новый тест сначала подтвердил исполнение внешнего marker-скрипта в обоих подслучаях (RED), затем подтвердил отказ до исполнения (GREEN). Повторный review исправления: замечаний нет. [Findings](review-findings.json).

Отдельная свежая проверка поведения без исходного контекста прочитала кандидатный SKILL и нужные ресурсы: корректно вывела обе установки, остановку включения новой категории до обоих ответов, отсутствие автоматического дополнения существующего project и gate непроверенной публикации. Замечаний нет. Это проверка инструкций подагентом, а не нативная проверка Codex/Claude.

## RED–GREEN и локальные проверки

- Исходная common-only проверка завершалась exit 0, но не создавала project или его стартовые ссылки. Новый сценарий на прежней реализации упал (RED); после реализации создание прошло (GREEN).
- Прежний check_rule_copies принимал project-only; отрицательный сценарий сначала упал, после обязательной зависимости common прошёл.
- Финальный `python3 -B -m unittest discover -s candidate/harness/common/checks -p 'test_*.py'`: 38 тестов, OK, проверено 5 обычных нативных копий правил.
- Две чистые установки запускались в bwrap с маскировкой исходного проекта и авторских глобальных правил/скиллов. Probe подтвердил пустоту скрытых путей. Проверка запуска: `python3 -I -B harness/common/checks/ensure_entrypoint_links.py`, exit 0 в обоих режимах. Затем весь unittest-набор: common-only — Ran 38, OK (skipped=2: две симлинковые под-проверки совместимого старого пути, которого нет в новом пустом project); common+project — 38, OK без пропусков. [Команды, вывод и маски](isolated-local-checks.json).
- `quick_validate.py candidate/harness/common/skills/comm-create-lazy-claude-codex-skills`: Skill is valid! Метаданные непустые; локальные ссылки ресурсов существуют; полные обычные папки источника и обеих нативных копий совпадают по наборам файлов и байтам.
- CLI human-guide search теперь объявляет только `--mode {common,both}`; --help exit 0. Реальный поисковый прогон нового helper не выполнен: он требует нативного Codex. README.human.md тела не выводились в контекст и исключены из Plugin Eval. При промежуточном вспомогательном подсчёте размера 2026-10-06 README.human.md был ошибочно прочитан через read_text, в вывод попал только численный размер. Нарушение сообщено пользователю, фильтр исправлен; последующие оценки исключают человеческие файлы. Byte equality не считается чтением тела в контекст.

## Объём и внешняя оценка

Plugin Eval 0.1.2 analyze, без чтения README.human.md и без записи самим анализатором: 86/100, B. Единственная error/fail — deferred_cost_tokens-budget-high: 1464 статически оценённых токена ресурсов при верхнем пороге 1200. Trigger 47, invoke 397; validation-and-publication.md — 728. [Полный результат](plugin-eval.json). Это та же категория ошибки исходного аудита (тогда ресурсы 1572), а не доказанная ошибка поведения или утечка. Источник baseline содержит лишь один skill sample; это ограничение оценки, не разрешение игнорировать fail.

Оценка выбранных стартовых указателей и всех пяти правил методом ceil(Unicode characters/4): common-only 3688, common+project 3781. Это выбранные файлы, не измеренный расход сессии; реальный нативный каталог и runtime overhead не измерены. Численный стартовый бюджет пользователем не согласован. Применён plugin-eval:improve-skill: brief выделил только обязательное уменьшение deferred budget; recommended fixes отсутствуют. По skill-creator сохранён контракт, сокращены повторы в трёх ресурсах, повторены format/resources/equality/tests/evaluation. Оценка уменьшилась с 1705 до 1464 (~14%); score остался 86/B и budget fail не закрыт. [До](before-compaction-plugin-eval.json), [сравнение](plugin-eval-comparison.json). Свежий review сжатия подтвердил поведение: имя длины 64 разрешено, rule-scope только в metadata недопустим, Claude fail останавливает публикацию без текущего исключения, проектная папка не экспортируется, specs требует решения и отдельного подтверждения. Потерянное слово portable для common восстановлено с уточнением зависимости только для harness; повторный review исправления — без замечаний. Любая правка ресурсов отменяет прежние native статусы; у итоговой версии они «не проверено».

## Нативные агенты и ограничение выполнения

Codex CLI 0.159.3; Claude Code 2.1.260. `check_native.py` строит чистые временные common-only/common+project установки, полные обычные нативные копии, маскирует исходный проект и глобальные инструкции и разделяет explicit/implicit prompts. Содержимое auth-файлов не выводится; временные runtime-копии удаляются.

Первый ограниченный запуск common-only: Codex explicit/implicit завершились exit 1 до работы агента (`workspace routing discovery failed`, соединение с сервисом недоступно). Первые команды Claude завершились exit 1 из-за поглощения prompt вариативным аргументом --tools; аргументы исправлены добавлением разделителя `--`, повторный запуск ещё не выполнен. Эти попытки не доказывают listing/selection/resource use.

Повторный запуск исправленного сценария с доступом к сети отклонён автоматической проверкой разрешений: он мог передать содержимое кандидата внешним Codex/Claude сервисам, а конкретное разрешение на передачу этого payload этим адресатам не зафиксировано. Отказ не обходился. [Независимые статусы](native-statuses.json); исходные event logs — sandbox-*-events.json рядом. Common+project и самостоятельное native listing не запускались.

| Агент | common-only | common+project | Итог |
|---|---|---|---|
| Codex | не проверено: native turn failed | не проверено: не запускался | не проверено |
| Claude | не проверено: первый CLI-вызов некорректен, исправленный не запускался | не проверено: не запускался | не проверено |

Общий итог: не полностью проверено. Неуспешная внешняя budget-проверка и отсутствующие нативные результаты остаются ограничениями даже при локальном успехе.

## Публикация и дальнейший шаг

Кандидат остаётся в inbox. Разрешение и подтверждение на публикацию этой непроверенной версии НЕ получены. Запрос изменения и решения о модели установки не являются таким исключением. Возможные следующие действия: отдельное явное разрешение на передачу материалов кандидата сервисам Codex/Claude для повторных native проверок; либо явное разрешение и подтверждение непроверенной публикации этой версии с сохранением указанных статусов, по точным путям manifest. Gate — ../../rules/comm-skill-rule-ownership.md и ../../docs/compact-authoring.md.

Предложенные source/native пути (относительно корня проекта):

- `.agents/skills/comm-create-lazy-claude-codex-skills/references/content-contract.md`
- `.agents/skills/comm-create-lazy-claude-codex-skills/references/placement-contract.md`
- `.agents/skills/comm-create-lazy-claude-codex-skills/references/validation-and-publication.md`
- `.claude/rules/comm-entrypoint-links-rule.md`
- `.claude/rules/comm-package-independence.md`
- `.claude/skills/comm-create-lazy-claude-codex-skills/references/content-contract.md`
- `.claude/skills/comm-create-lazy-claude-codex-skills/references/placement-contract.md`
- `.claude/skills/comm-create-lazy-claude-codex-skills/references/validation-and-publication.md`
- `harness/common/INDEX.md`
- `harness/common/START.md`
- `harness/common/base/project-skeleton.json`
- `harness/common/checks/acceptance.md`
- `harness/common/checks/check_human_guide_search.py`
- `harness/common/checks/ensure_entrypoint_links.py`
- `harness/common/checks/test_ensure_entrypoint_links.py`
- `harness/common/checks/test_entrypoint_notifications.py`
- `harness/common/checks/test_entrypoint_portability.py`
- `harness/common/checks/test_rule_copies.py`
- `harness/common/decisions/harness-architecture.md`
- `harness/common/docs/compact-authoring.md`
- `harness/common/docs/protected-entrypoints.md`
- `harness/common/docs/skill-rule-ownership-contract.md`
- `harness/common/lessons/comm-rule-copy-drift.md`
- `harness/common/rules/comm-entrypoint-links-rule.md`
- `harness/common/rules/comm-package-independence.md`
- `harness/common/skills/comm-create-lazy-claude-codex-skills/references/content-contract.md`
- `harness/common/skills/comm-create-lazy-claude-codex-skills/references/placement-contract.md`
- `harness/common/skills/comm-create-lazy-claude-codex-skills/references/validation-and-publication.md`
- `harness/project/START.md`
- `harness/project/checks/ensure_entrypoint_links.py`

## Остановка цели на согласовании

2026-10-06: третий последовательный goal-turn подтвердил тот же блокирующий фактор: отдельного разрешения на передачу материалов сервисам Codex/Claude или разрешения/подтверждения непроверенной публикации текущей версии нет. Предыдущий turn был progress: ресурсы сокращены, review и применимые локальные проверки повторены, версия manifest обновлена. Текущий аудит подтвердил hashes всех 30 файлов; опубликованного project-skeleton.json по-прежнему нет, действующая проверка остаётся прежней. Сетевой native запуск был окончательно rejected, живого процесса ожидания нет. Доступная локальная подготовка завершена; goal отмечается blocked до пользовательского решения, а не complete. Автоматическое продолжение цели не является таким решением.
