# Подготовка восьми заявок группы 5

Дата создания: 2026-11-14. Завершение подготовки: 2026-11-14T12:28:28.162149+03:00.

Status: preparation complete; request execution not started.
Разрешены и выполнены только создание заявок/кандидатов, сверка актуальных владельцев,
редакционная проверка комплектности и stock explain-budget.
Это не formal/native/behavior validation и не публикация.

## Артефакты и фактические статусы

Все восемь request.md имеют Execution/Status: new и Result: not executed.
Полные кандидаты находятся в candidate/<skill-name>/; canonical, .agents, .claude
и пользовательские entrypoints не заменялись. Git commit/push/PR не выполнялись.

Карта 14 согласованных вопросов: [2026-11-14-requirements-map.json](2026-11-14-requirements-map.json).
Источник: octadim/after-disconnect-branch @ a4eb35bf52cce0c304bff5db000330673a9d6526.
Три зеркальные пары .agents/.claude источника учтены как три логики, а не шесть.
Исторические terminal INBOX-тела исключены; проведена status-first сверка и проверка current canonical owners.

## Метод оценки и границы

Штатный установленный plugin-eval: cache 0.1.2, package.json 0.1.0.
Команда: node harness/common/scripts/plugin_eval_without_human.mjs <trusted-entry> explain-budget <candidate-root> --format json.
Все stdout/stderr сохранены неизменяемо в final-budget/; score/grade/findings полного analyze не получались.
budgets.method=estimated-static. Stock использует ceil(UTF-16 string length / 4).
Отдельно приведены Unicode-символы и UTF-16 units; в этих кандидатах они равны.
Собственный tokenizer не создавался. Human-фильтр исключал README.human.md до чтения/стоимости.
Stock total включает trigger + invoke + все собственные deferred-компоненты; это не измеренный контекст.
Внешние linked-файлы не выданы за собственные ресурсы и не спрятаны: они перечислены ниже и в JSON.

Новых always-loaded правил нет. Словесная шкала good/moderate/heavy-warn/excessive-fail
для always-loaded rules здесь N/A; она не подменяет штатные категории lazy-скиллов.
Все главные SKILL.md <=200 слов; собственные deferred <=1000; собственные stock total <=1000.
Никакого общего согласованного лимита полного startup/сессии не предполагалось.

## Полные собственные бюджеты

| Заявка / кандидат | Слова SKILL | Unicode-символы | Static SKILL | Trigger | Deferred / band | Stock total / band |
|---|---:|---:|---:|---:|---|---|
| [comm-check-publication-data](../../2026-11-14-01-check-publication-data/request.md) | 186 | 1455 | 364 | 44 | 0 / good | 408 / moderate |
| [comm-commit-task-stages](../../2026-11-14-02-git-work-and-message-safety/request.md) | 178 | 1563 | 391 | 44 | 339 / moderate | 774 / moderate |
| [comm-verify-project-facts](../../2026-11-14-03-verify-git-facts/request.md) | 165 | 1549 | 388 | 37 | 575 / heavy | 1000 / heavy |
| [comm-create-git-branch](../../2026-11-14-04-create-git-branch/request.md) | 181 | 1459 | 365 | 41 | 222 / moderate | 628 / moderate |
| [comm-update-git-branch](../../2026-11-14-05-update-git-branch/request.md) | 176 | 1626 | 407 | 37 | 481 / moderate | 925 / moderate |
| [comm-process-pull-request](../../2026-11-14-06-process-pull-request/request.md) | 178 | 1467 | 367 | 44 | 557 / heavy | 968 / heavy |
| [comm-recover-git-state](../../2026-11-14-07-recover-git-state/request.md) | 184 | 1529 | 383 | 41 | 262 / moderate | 686 / moderate |
| [comm-migrate-git-repository](../../2026-11-14-08-migrate-git-repository/request.md) | 184 | 1639 | 410 | 43 | 346 / moderate | 799 / moderate |

У всех восьми stock trigger=good и invoke=moderate. Stock deferred heavy у facts/PR сохраняется как heavy.
Это не excessive-fail и не разрешение публикации. Thresholds stock не изменялись:
trigger 48/92/150; invoke 220/480/900; deferred 180/520/1200.

## Данные по каждому файлу и reference

Для каждого файла — слова, символы, штатные static tokens. Для reference дополнительная строка
S + один R + Texts, где Texts=0: других учитываемых ресурсов нет. Строки не складываются.
Дополнительная шкала строки: <=180 good; 181–520 moderate; 521–1200 heavy-warn; >1200 excessive-fail.
Она не заменяет stock band и не означает проведённую поведенческую проверку.

### comm-check-publication-data

- SKILL.md: слова=186, Unicode=1455, UTF16=1455, stock=364.
- SKILL.md=364/references=нет /Texts=0 --> 364 (moderate).
- Raw: [stdout](final-budget/candidate-comm-check-publication-data.stdout.json).

### comm-commit-task-stages

- SKILL.md: слова=178, Unicode=1563, UTF16=1563, stock=391.
- references/message-transfer.md: слова=86, Unicode=581, UTF16=581, stock=146.
- references/work-safety.md: слова=107, Unicode=770, UTF16=770, stock=193.
- SKILL.md=391/references/message-transfer.md=146 /Texts=0 --> 537 (heavy-warn).
- SKILL.md=391/references/work-safety.md=193 /Texts=0 --> 584 (heavy-warn).
- Raw: [stdout](final-budget/candidate-comm-commit-task-stages.stdout.json).

### comm-verify-project-facts

- SKILL.md: слова=165, Unicode=1549, UTF16=1549, stock=388.
- references/git-base-state.md: слова=101, Unicode=761, UTF16=761, stock=191.
- references/git-integration.md: слова=115, Unicode=856, UTF16=856, stock=214.
- references/git-operation-result.md: слова=85, Unicode=679, UTF16=679, stock=170.
- SKILL.md=388/references/git-base-state.md=191 /Texts=0 --> 579 (heavy-warn).
- SKILL.md=388/references/git-integration.md=214 /Texts=0 --> 602 (heavy-warn).
- SKILL.md=388/references/git-operation-result.md=170 /Texts=0 --> 558 (heavy-warn).
- Raw: [stdout](final-budget/candidate-comm-verify-project-facts.stdout.json).

### comm-create-git-branch

- SKILL.md: слова=181, Unicode=1459, UTF16=1459, stock=365.
- references/naming.md: слова=122, Unicode=888, UTF16=888, stock=222.
- SKILL.md=365/references/naming.md=222 /Texts=0 --> 587 (heavy-warn).
- Raw: [stdout](final-budget/candidate-comm-create-git-branch.stdout.json).

### comm-update-git-branch

- SKILL.md: слова=176, Unicode=1626, UTF16=1626, stock=407.
- references/conflicts.md: слова=124, Unicode=928, UTF16=928, stock=232.
- references/methods.md: слова=131, Unicode=996, UTF16=996, stock=249.
- SKILL.md=407/references/conflicts.md=232 /Texts=0 --> 639 (heavy-warn).
- SKILL.md=407/references/methods.md=249 /Texts=0 --> 656 (heavy-warn).
- Raw: [stdout](final-budget/candidate-comm-update-git-branch.stdout.json).

### comm-process-pull-request

- SKILL.md: слова=178, Unicode=1467, UTF16=1467, stock=367.
- references/merge.md: слова=92, Unicode=752, UTF16=752, stock=188.
- references/preparation.md: слова=79, Unicode=654, UTF16=654, stock=164.
- references/remote-deletion.md: слова=115, Unicode=818, UTF16=818, stock=205.
- SKILL.md=367/references/merge.md=188 /Texts=0 --> 555 (heavy-warn).
- SKILL.md=367/references/preparation.md=164 /Texts=0 --> 531 (heavy-warn).
- SKILL.md=367/references/remote-deletion.md=205 /Texts=0 --> 572 (heavy-warn).
- Raw: [stdout](final-budget/candidate-comm-process-pull-request.stdout.json).

### comm-recover-git-state

- SKILL.md: слова=184, Unicode=1529, UTF16=1529, stock=383.
- references/modes.md: слова=146, Unicode=1048, UTF16=1048, stock=262.
- SKILL.md=383/references/modes.md=262 /Texts=0 --> 645 (heavy-warn).
- Raw: [stdout](final-budget/candidate-comm-recover-git-state.stdout.json).

### comm-migrate-git-repository

- SKILL.md: слова=184, Unicode=1639, UTF16=1639, stock=410.
- references/inventory.md: слова=80, Unicode=668, UTF16=668, stock=167.
- references/platform.md: слова=92, Unicode=716, UTF16=716, stock=179.
- SKILL.md=410/references/inventory.md=167 /Texts=0 --> 577 (heavy-warn).
- SKILL.md=410/references/platform.md=179 /Texts=0 --> 589 (heavy-warn).
- Raw: [stdout](final-budget/candidate-comm-migrate-git-repository.stdout.json).

## Предыдущие редакции и отсутствие искусственного baseline

Первая полная оценка: facts total=1040, PR total=1028. Тексты сжаты в том же составе требований;
v1/v2/v3 snapshots, stdout/stderr и hashes сохранены в draft-history/, не перезаписывались.
Прямые указания владельцев отчётов и защищённого маршрута затем уточнены; окончательные пути измерены отдельно.
Факт сохранения семантики зафиксирован редакционной картой; native/behavior доказательства ещё не получены.

| Неизменённый current canonical | Старые слова | Старый invoke/deferred/total | Кандидат invoke/deferred/total |
|---|---:|---|---|
| comm-commit-task-stages | 209 | 396/0/440 | 391/339/774 |
| comm-verify-project-facts | 195 | 387/0/424 | 388/575/1000 |

Сумма stock trigger шести новых metadata: 250. У двух изменённых владельцев trigger неизменён.
Это расчёт добавляемых metadata, не замер startup агента.

## Внешние условные зависимости: отдельная стоимость

| Текущий владелец | Invoke / band | Deferred / band | Stock total / band |
|---|---|---|---|
| comm-separate-application-config | 449 / moderate | 0 / good | 490 / moderate |
| comm-test-project-behavior | 320 / moderate | 0 / good | 349 / moderate |
| comm-assess-project-tests | 330 / moderate | 519 / moderate | 884 / moderate |
| comm-run-project-checks | 342 / moderate | 0 / good | 367 / moderate |
| comm-validate-harness-instructions | 434 / moderate | 1049 / heavy | 1529 / heavy |
| comm-choose-effective-solution | 407 / moderate | 0 / good | 445 / moderate |
| comm-resolve-permission-blockers | 473 / moderate | 0 / good | 524 / moderate |
| comm-confirm-database-design | 477 / moderate | 1193 / heavy | 1712 / heavy |
| comm-protect-harness-evidence | 335 / moderate | 395 / moderate | 773 / moderate |
| ce-commit | 1300 / excessive | 0 / good | 1343 / excessive |

**Предупреждение:** собственные кандидаты <=1000 не означают, что весь рабочий контекст <=1000.
Существующие conditional dependencies comm-validate-harness-instructions, comm-confirm-database-design
и внешний ce-commit имеют stock total >1000; первые два >1200, ce-commit invoke имеет штатный excessive.
Они не изменены и не объявлены новыми допустимыми исключениями. Рекомендуется загружать только
применимых владельцев/ресурсы и при разрешённой валидации измерить реальные чтения с контролем.
Если потребуется изменение этих владельцев или разбиение согласованной процедуры, отдельно предложить решение
и дождаться пользователя. Не поднимать thresholds и не исключать нужные зависимости ради оценки.

Примеры статической суммы конкретно перечисленных файлов (без metadata/system/startup):
- Создание новой ветки: 971 static tokens.
- Создание обычного PR: 1041 static tokens.
- Слияние существующего согласованного PR: 1256 static tokens.
- Полный вариант PR 3 с созданием и удалением remote-ветки: 1625 static tokens.
- Актуализация с конфликтом и проверками приложения: 2264 static tokens.

Файлы каждого примера указаны в [2026-11-14-dependency-read-profiles.json](2026-11-14-dependency-read-profiles.json).
Это не трасса выполнения и не полный контекст. Дополнительные условия (SQL, controlled mutations,
неясный результат, конфигурация, permissions, evidence) могут загрузить другие текущие ресурсы.
Подробный JSON включает все доступные собственные ресурсы каждого отдельно оценённого владельца.

## Статусы проверки

- Редакционная комплектность/карта файлов/снимки/сохранность: результат отдельного preparation-integrity.json.
- Stock estimated-static: завершено; фактические stdout/stderr приложены.
- Formal structural/skill-creator/start/analyze/improve/native/RED–GREEN/benchmark: not run; нет разрешения этой стадии.
- Codex и Claude, common-only и common+project: все четыре статуса not verified.
- Публикация и нативная установка: not performed; root entrypoints и рабочие наборы сохранены.

## Следующие разрешения

Создание этих заявок не разрешает исполнение. Перед исполнением сверить current canonical и открытые
предложения, проверить prerequisites и выбрать разрешённый маршрут. Исполнять последовательно 1→8,
закрывая предыдущую по требуемому результату; публикация остаётся отдельной явно разрешённой стадией.
Будущие rationale/evidence разместить в постоянных категориях вне inbox по действующим процедурам.
Группы 6–11 исходной цели ещё не завершены.
