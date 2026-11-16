# Кандидат запрета симлинков в harness

Дата создания отчёта: 2026-10-13T14:07:33+03:00 (Europe/Minsk).
Стадия: исполнение и проверки завершены; публикация не разрешена и не выполнена.
Заявка: [request.md](../../inbox/2026-10-13-ban-harness-symlinks/request.md).
Точная версия: `b5da5a4ecb752fc21f25aa9953c78c7b113b240de585fbd06c4f891110a4ba24`.
[Машинные SHA-256](candidate-version-final-v2.json); [полный состав публикации](publication-scope.json).

## Изменение и охват

Подготовлены полные кандидаты четырёх рабочих скриптов common, нового общего
правила и равной .claude-копии, нового test_harness_symlinks.py, скорректированного
integration-теста plugin-eval, полного навыка comm-validate-harness-instructions
с обновлённым evaluation.md и равными .agents/.claude папками. В версии 17 машинных
файлов, в полном составе публикации 23 файлов, включая неизменённые human guides
внутри папки навыка. Вспомогательные guides родительских папок кандидата не заменяют
действующие guides. Тела README.human.md агентом не загружались; программные проверки
проверяют наборы и исключение human-содержимого, возвращая только результаты.

- В существующий ensure_entrypoint_links.py добавлены ordinary_path и ordinary_tree.
  Исходные компоненты проверяются от корня к листу через lstat до нормализации;
  обход scandir не следует по ссылкам и не скрывает ошибки чтения каталогов.
  Всё дерево harness проверяется до чтения ресурсов, создания project и ремонта.
- run_tests.py и check_human_guide_search.py проверяют bootstrap пути до runpy
  существующего общего скрипта; нового guard-скрипта, wrapper или launcher нет.
  Проверяются rule/output, runtime paths, tempfile-кандидаты до writable probe,
  выбранный temp parent и созданный root до записи. run_tests сохраняет отдельный
  запуск каждой фактической редакции тестов.
- Существующий Node launcher проверяет working harness, исходный CLI, исходные
  позиционные и файловые аргументы до импорта/нормализации установленным CLI,
  promises чтение/обход/open/stat/access/realpath/readlink; запись/создание ссылок
  запрещены. Учитываются `..` и позиционные имена с начальным дефисом.
- Ресурс evaluation.md больше не предлагает разыменование shell shim;
  задаёт доверенный обычный installed JS entry и сохраняет фактические пределы
  promises-фильтра. Новое правило задаёт раннюю границу до выбора навыка;
  алгоритм проверки остаётся у существующего скрипта.

Зависимости не добавлялись. Прямой старт и коды 0/2, пользовательские настройки,
LF/CRLF, metadata/ACL, проверки копий, отказ project-only и сохранение existing
project подтверждены регрессиями. Симлинки/их цели не удаляются/не исправляются.
Исторические кандидаты и исходные evidence не переписывались. Рабочие скрипты,
AGENTS/CLAUDE, общий skeleton и project сохранены: structural-final-v2.json
содержит пустой working_protected_changes и совпадение кандидата с проверенной копией.

## Проверки кода и установки

`.venv/bin/python -B -m pytest -q -p no:cacheprovider` в полной изолированной
установке `/tmp/harness-symlinks-stage-v2`: **168 passed in 11.16s**, без skipped
([полный вывод](green-suite-final-v2.txt)). 40 новых сценариев включают внутренние,
внешние, каталожные, файловые, оборванные ссылки, архивные inbox/evidence/project,
выходные пути и родителей, оригинальные Node аргументы с `..`/дефисом, tempfile
transient probes, сохранность цели и отказ до исполнения/ремонта. Прежние 128
регрессий сохранены.

RED: первый набор 32 failed / 1 passed; реальные CLI/runtime регрессии ревью
4 failed, дополнительные дефисные случаи 2 failed; transient tempfile probe
1 failed. Причины разобраны и исправлены до итогового GREEN; сырые выводы
red-*.txt сохранены. Первый широкий прогон дал 3 failed / 158 passed из-за
неполного test installation (отсутствовали native skills/rules/project), затем
полная установка дала 161 passed, после регрессий ревью — 165/167/168 passed.
Провал fixtures не выдаётся за дефект кода и не скрыт.

Две отдельные чистые установки common-only/common+project: два успешных старта,
10 равных canonical/native правил, existing project сохранён; повторные inputs
не меняются ([структурный результат](structural-final-v2.json)). Runner smoke
запустил две независимые test editions, включая архивную, без смешивания модулей.
`git diff --check` прошёл. Ревью отдельным агентом выявило обходы raw CLI paths и
tempfile probes; после исправлений замечаний не осталось, 40 symlink-тестов прошли.

## Нативные проверки и статусы

Codex CLI 0.161.0: шесть свежих read-only сессий окончательной версии — implicit,
explicit, unrelated в каждом режиме. Все завершились exit0/turn.completed.
Проверены startup → START обоих пакетов → отдельный полный filtered listing и
чтение 10 правил → INDEX → применимый навык/собственные resources. Explicit
прочитал installed .agents validation/evaluation; implicit выбрал diagnosis;
unrelated не загрузил тела навыков. Синтетическая linked note отвергнута до
чтения: private canary в events отсутствует; human тела не появлялись; hashes
изолированных файлов не изменились. Команды, фактические чтения, версии,
фактический native usage/cached usage и ограничения каждого запуска —
[native-review-final-v2.json](native-review-final-v2.json), raw native-*-final-v2.json.
Промежуточные v1/raw не заменяют итоговую версию.

Без нового правила baseline control уже отказался читать alias по существующему
навыку diagnosis. Это не доказывает причинный instruction RED/GREEN эффект;
такого утверждения нет. RED изменения механических guards доказан отдельно
кодовым набором. Native probes не покрывают каждую форму ссылки под каждым
сочетанием давления.

**Codex: проверено в описанной области. Claude: непроверенный. Итог: непроверенный.**
Попытки Claude Code 2.1.260 в обоих режимах не смогли пройти authentication:
`Failed to authenticate: OAuth session expired and could not be refreshed`.
Ни installation equality, ни permission, ни будущая публикация не повышают статус.

## Компактность и измерения

Quick profile valid; plugin-eval start → analyze: skill A/95, generic rule directory
A/100, ошибок и required fixes нет. Generic A не доказывает поведение правила.
Skill metadata 46, body 407 estimated-static tokens неизменны. Deferred resources:
783 → 846 (+63); оценка heavy выше moderateMax=520, но ниже heavyMax=1200 и
внутреннего ориентира 1000. RecommendedFix — уменьшать повторы; необходимые
границы безопасного запуска сохранены в прежнем условном ресурсе, отдельный
новый skill/ресурс не добавлен. Полный доступный skill budget 1299 — не стоимость
одного запуска. Rule directory budget 278 ниже generic moderateMax=640.
Локальные START/rules/INDEX: 7201 → 7479 (+278); metadata 14 common навыков 536
неизменны. AGENTS и сторонние plugin metadata не включены и не названы общим
startup cap. Сравнимые явные прочтённые тела и все dependencies из native events
перечислены отдельно; actual CLI usage — отдельно, не смешан со статическими оценками.
Метод plugin-eval: ceil(UTF16 length / 4), не tokenizer/billing.
[Бюджеты и baseline](budgets-final-v2.json) содержат пути, компоненты, thresholds,
recommended fixes и причины роста; thresholds не повышались.

## Пределы и оставшаяся стадия

Запуск уже подменённого скрипта нельзя защитить его собственной проверкой;
интерпретатор и установленный analyzer остаются доверенными. Promises patch не
является OS sandbox и не покрывает произвольные callback/sync APIs чужого кода.
TOCTOU hostile path substitution не заявлена решённой; сохраняются ранее
существовавшие проверки snapshot/concurrent changes входных файлов.
Private tempfile candidate enumeration отмечена shortcut: пересмотреть при
обновлении поддерживаемого Python. Новые ссылки разрешены только в изолированных
негативных fixtures вне рабочего harness, чтобы проверить отказ; это не валидные
рабочие установки.

Заявка остаётся in progress: кандидат готов, публикация source/native не выполнена.
Для продолжения требуется разрешение и подтверждение публикации именно версии
`b5da5a4e` с сохранением фактических непроверенных Claude/overall статусов.
