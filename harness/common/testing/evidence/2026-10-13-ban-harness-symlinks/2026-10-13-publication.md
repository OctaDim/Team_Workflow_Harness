# Публикация общего запрета симлинков

Завершено: 2026-10-13T14:27:38+03:00 (Europe/Minsk).
Заявка: [request.md](../../inbox/2026-10-13-ban-harness-symlinks/request.md).
Точная версия: `b5da5a4ecb752fc21f25aa9953c78c7b113b240de585fbd06c4f891110a4ba24`. Кандидат и исходные проверки сохранены коммитом `68d70ce`.
После отдельного вопроса о точной версии и составе пользователь ответил «разрешаю»;
это разрешение и подтверждение её публикации при непроверенных Claude/итоговом статусах.
Общие настройки разрешений не изменялись.

## Опубликованный результат

Согласованный состав: [publication-scope.json](publication-scope.json), **23 файла**.
Все SHA-256 равны утверждённому кандидату; реально изменено **11 файлов**
([publication-files.json](publication-files.json)).
Опубликованы четыре рабочих скрипта, два тестовых модуля, новое общее правило
и равная обычная .claude/rules-копия, полный validation-навык и равные .agents/.claude
папки. Неизменные файлы и human guides не перезаписывались. Before hashes и file modes
сохранены в publication-before.json; параллельные изменения проверены до замены.

Общий прямой startup отвергает симлинки во всём working harness, включая архивные
inbox и evidence, до чтения ресурсов/создания project/ремонта входов. Входы, выходы,
bootstrap paths и предки проверяются по исходному пути. Node CLI аргументы проверены
до нормализации установленным analyzer; Python временные пути — до writable probe.
Существующий общий checker содержит переиспользуемые guards. Нового рабочего
launcher/wrapper/guard-скрипта, hooks или зависимостей нет. Физические ссылки и их
цели не изменяются. Поведение установки, ordinary copies и LF/CRLF сохранено.

AGENTS.md, CLAUDE.md, общий skeleton и прежние файлы project не изменены.
Материалы и коммит другой задачи RAG оставлены в её собственности. Объединение
согласованного source/native состава не включает изменения механизма project.

## Проверки опубликованной версии

- `.venv/bin/python -B -m pytest -q -p no:cacheprovider`: **168 passed in 23.17s**, без skipped
  ([полный неизменяемый вывод](published-tests-v1.txt)). Новые 40 сценариев и прежние
  128 регрессий подтверждают симлинки разных форм, exact отказ/сохранность, CLI
  `..`/дефис, runtime directories и отсутствие даже временной записи через TMPDIR.
- `python3 -B harness/common/checks/ensure_entrypoint_links.py`: exit0, ремонт не нужен
  ([вывод](published-startup-v1.txt)). Всё дерево без симлинков; 10 canonical правил
  равны native; полный source/native skill set равен; все пути Git-visible;
  неожиданных изменений protected материалов нет ([целостность](published-integrity-v1.json)).
- Quick profile valid. Installed plugin-eval start → analyze: skill A/95, 0 errors,
  required fixes пусты; прежнее предупреждение о deferred budget сохранено.
  Текущие статические budgets совпадают с версией кандидата; thresholds не изменены.
- Codex CLI 0.161.0: **6 свежих published-v2 read-only probes**, implicit/explicit/unrelated
  в common-only и common+project, все exit0/turn.completed. Проверены ordered startup,
  отдельный полный filtered listing/чтение 10 правил, installed own resources,
  implicit diagnosis и unrelated skill non-loading. Синтетическая linked note
  отвергнута до содержимого; private canary не появился; fixture hashes неизменны.
  Команды/raw events/actual usage — native-codex-*-published-v2.json;
  [проверенный результат](published-native-review-v2.json).

Итоговый helper скрывает **весь исходный workspace** и global author skill roots.
Ранний candidate helper скрывал только harness из-за неверно выбранного parent;
фактически читавшиеся temp paths были проверены, но те runs не доказывали полную
недоступность исходных native copies. Для утверждений о независимой интеграции
используются только свежие published-v2 с исправленным masking. Helpers — evidence
валидации, не новый способ рабочего запуска harness; ранние raw results не исправлены.

**Codex: проверено в указанной области. Claude: непроверенный (на стадии публикации
не запускался). Итоговый статус: непроверенный.** Публикация/копирование эти статусы
не повышают. Причинный instruction RED baseline не установлен: прежняя diagnosis
уже отвергала alias; кодовый RED/GREEN установлен и сохранён отдельно.

## Сохранность и пределы

[Завершённый отчёт кандидата](2026-10-13-candidate-report.md), все raw runs и исходные
снимки сохранены. [Уточнение whitespace](2026-10-13-diff-check-addendum.md) фиксирует
пробелы в неизменяемых failed pytest logs; они не исправлялись. Содержательные файлы
проверяются отдельно; итоговый publication diff проверяется перед коммитом.

Требуется доверенный обычный прямой запуск: self-check не предотвращает исполнение
уже подменённого файла. Promises-фильтр не является OS sandbox; arbitrary callback/sync
APIs доверенного analyzer и hostile TOCTOU path replacement не заявлены защищёнными.
Private tempfile candidate-list API отмечена shortcut для перепроверки при обновлении Python.

Заявка completed: согласованное исполнение, проверки, разрешённая публикация и
постоянные результаты завершены. Отдельного последующего разрешения не требуется.
