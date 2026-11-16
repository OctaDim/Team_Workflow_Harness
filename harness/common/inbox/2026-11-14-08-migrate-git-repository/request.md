# Переносить репозиторий с проверкой связанных интеграций

Дата создания: 2026-11-14. Создано: 2026-11-14T03:23:17.866930+03:00. Порядок группы 5: 8/8.
Место назначения: harness/common/skills/comm-migrate-git-repository/.
Потребность возникла в текущем согласовании переноса harness; точное время исходного запроса не установлено и не выдумывается.

## Разрешение и границы стадии

После поэтапного согласования 14 вопросов и общей группировки пользователь отдельно разрешил:
«даю явное разрешение на восемь будущих заявок».
Разрешены создание этой заявки, полного кандидата/ресурсов, сверка дублей,
редакционная проверка комплектности и штатный explain-budget.
Исполнение заявки, formal/native/behavior tests, benchmarks, установки,
публикация canonical/native, Git commit/push/PR и изменение root entrypoints не разрешены.
Это перенос смысла в собственный кандидат, не копирование правил источника.

## Причина и требуемый результат

Миграция репозитория: источник содержит полезные требования, но они связаны с
конкретным проектом и частично пересекаются с текущим common. Нужен компактный
владелец указанного поведения с сохранением действующих разрешений и проверок.
Предлагается новый lazy-владелец с самостоятельным входом и проверяемым результатом.

## Согласованные требования

- **13. Миграция репозитория:** Согласовать исходный/целевой repo, цель transfer/rename/copy/cross-host, сохраняемые свойства и метод. Сравнить native transfer и import/mirror. Инвентарь refs/history/LFS/metadata/rights/protections/apps/hooks/runners/automation/docs по применимости. Проверить URL-формы, корректные старые имена и историю. Host-specific редиректы/возможности проверять по текущим данным. Нет автоматического удаления/перезаписи/расширения доступов. Проверить существенные свойства/интеграции; production и secrets отдельно.

Карта всех требований и единственных владельцев:
[requirements map](../2026-11-14-01-check-publication-data/preparation/2026-11-14-requirements-map.json).
Пункты, принадлежащие соседям, переиспользуются по явному условию чтения;
копировать их алгоритмы в этот SKILL не требуется. Применимые comm-/proj-
ограничения, защищённые записи и отдельные владельцы проверки приложения/harness сохраняются.

## Текущие владельцы, открытые заявки и зависимости

Действующие владельцы и результат status-first сверки:
[current owners](../2026-11-14-01-check-publication-data/preparation/2026-11-14-current-owner-and-open-inbox-review.json).
До создания группы релевантных открытых заявок не обнаружено.
Завершённая/отклонённая/заменённая история не использована как источник требований.

- Заявка 2: [comm-commit-task-stages](../2026-11-14-02-git-work-and-message-safety/request.md). Перед будущим исполнением подтвердить наличие нужной опубликованной версии; наличие кандидата не равно установке.
- Заявка 3: [comm-verify-project-facts](../2026-11-14-03-verify-git-facts/request.md). Перед будущим исполнением подтвердить наличие нужной опубликованной версии; наличие кандидата не равно установке.

Связанные новые заявки, уже согласованные как разные владельцы:
- [comm-check-publication-data](../2026-11-14-01-check-publication-data/request.md): общая проверка данных до публикации
- [comm-commit-task-stages](../2026-11-14-02-git-work-and-message-safety/request.md): единственный владелец сохранности Git и передачи текста
- [comm-verify-project-facts](../2026-11-14-03-verify-git-facts/request.md): единственный владелец фактических Git-проверок
- [comm-create-git-branch](../2026-11-14-04-create-git-branch/request.md): самостоятельная процедура с отдельным результатом
- [comm-update-git-branch](../2026-11-14-05-update-git-branch/request.md): самостоятельная процедура с отдельным результатом
- [comm-process-pull-request](../2026-11-14-06-process-pull-request/request.md): самостоятельная процедура с отдельным результатом
- [comm-recover-git-state](../2026-11-14-07-recover-git-state/request.md): самостоятельная процедура с отдельным результатом

## Форма и отсутствие дублей

- Rule-only: недостаточен для входов, условных действий и наблюдаемого результата; общий алгоритм не переносится в always loaded.
- Lazy-only: выбран. Явный task trigger и when-read ресурсы должны обеспечивать загрузку в нужном действии; фактическая discovery пока не проверена.
- Rule + lazy: новый ранний guard не добавляется без подтверждённого провала до выбора процедуры. При таком провале сначала проверить/уточнить metadata, затем отдельно согласовать форму.
- Reuse-only: общие факты, разрешения, тесты, evidence и конфигурация остаются существующим владельцам. Здесь сохраняется только адресованный пробел.

Результат проверки формы сейчас — обоснованный кандидат, не доказанная работоспособность.
Согласованные исторические и технические уточнения сохранены в общей карте:
никакого универсального origin/main, Linear или автоматического PR→merge;
нет универсального диагноза squash, неверной трактовки git cherry или фильтра diff.

## Полный кандидат

- [candidate/comm-migrate-git-repository/SKILL.md](candidate/comm-migrate-git-repository/SKILL.md)
- [candidate/comm-migrate-git-repository/references/inventory.md](candidate/comm-migrate-git-repository/references/inventory.md)
- [candidate/comm-migrate-git-repository/references/platform.md](candidate/comm-migrate-git-repository/references/platform.md)

Human guides находятся в каждой новой папке; их тела исключены из агентских инструкций и оценки.
Кандидат не установлен в .agents/.claude и не заменяет canonical.

## Источники и происхождение

Источник: /home/octadim/MyProjects/bts-transenergo-epl-server; ветка octadim/after-disconnect-branch; SHA a4eb35bf52cce0c304bff5db000330673a9d6526.
- .claude/rules/git-pr.md:84-104
- .claude/skills/git-pr-history/references/git-pr.md:5-45

Исходные файлы сохранены как неизменяемые данные:
[source manifest](../2026-11-14-01-check-publication-data/preparation/2026-11-14-source-manifest.json).
Снимки источника не являются требованиями Team_Workflow_Harness.
Уточнения пользователя и действующий canonical имеют приоритет.

## Подготовка и объём

Финальный кандидат: 184 слов, 1639 Unicode-символов,
1639 UTF-16 units, 410 stock static tokens в полном SKILL.md.
Stock estimated-static: trigger=43 (good),
invoke=410 (moderate),
deferred=346 (moderate),
total=799 (moderate).
Категория слов always-loaded rules: N/A — выбран lazy skill, новое правило не создаётся.
Нет оценки score/grade, native reads и прохождения formal tests.

Полный [отчёт подготовки](../2026-11-14-01-check-publication-data/preparation/2026-11-14-group5-preparation-report.md)
содержит per-file/refs, baselines, условные зависимости, ограничения и неизменяемые старые редакции.
Raw финальной оценки: [stdout](../2026-11-14-01-check-publication-data/preparation/final-budget/candidate-comm-migrate-git-repository.stdout.json).
Внешние зависимости учитываются отдельно: собственный total не равен полному рабочему контексту.


Актуальное [дополнение подготовки](../2026-11-14-01-check-publication-data/preparation/2026-11-14-preparation-addendum.md) сохраняет оригинальный отчёт и уточняет последнюю recovery-редакцию.

## Приёмка будущего разрешённого исполнения

- Сверить текущие canonical и только релевантные актуальные открытые заявки; новую коллизию согласовать.
- Проверить все договорённости по карте требований; сохранить исходные raw/snapshots и staged/unstaged пользователя.
- Выбирать оба режима common-only/common+project; Codex/Claude отдельно.
- Проверить явный вызов, неявный выбор, собственные/общие when-read ресурсы и unrelated non-loading.
- Выполнить обязательные проверки по comm-validate-harness-instructions на итоговой компактной версии; изменение сбрасывает статусы.
- Сохранить оба агента/режима, реальные ограничения, показатели plugin-eval и полный доступный контекст отдельно. Проверить все внешние зависимости.
- При превышении согласованного бюджета предложить сжатие/разделение и дождаться решения; не менять thresholds или утаивать ресурсы.

Адресованные сценарии (план, не выполненные тесты):
- Native transfer против copy/import/mirror и сохраняемых свойств.
- Неоднозначная идентичность, ограничения получателя/protections/permissions.
- SSH/API/raw/PR ссылки и правильное старое имя runner-service.
- Redirect reuse, LFS/metadata и интеграция не переносятся по одному git diff.
- Mirror не разрешает запрещённое удаление/перезапись или production-проверку.

## Постоянный результат будущего исполнения

После отдельного разрешения исполнения/публикации разместить процедуру у указанного
canonical-владельца, rationale/решения и свидетельства — в постоянных категориях
common вне inbox по действующим маршрутам и фактическим датам создания.
Сохранить provenance и ссылки; запись только здесь не считается постоянным результатом.
Нативные копии публикуются отдельно после требуемых проверок и разрешения.

## Execution

Status: new
Result: not executed; создание полного кандидата и stock static-оценки завершено, formal/native проверки не запускались.
Reason: пользователь не разрешал исполнение, formal/native/behavior tests, benchmarks или публикацию.
Updated: 2026-11-14T12:32:12.477617+03:00
Codex/common-only: not run — стадия создания; отдельное разрешение на исполнение отсутствует.
Codex/common+project: not run — стадия создания; отдельное разрешение на исполнение отсутствует.
Claude/common-only: not run — стадия создания; отдельное разрешение на исполнение отсутствует.
Claude/common+project: not run — стадия создания; отдельное разрешение на исполнение отсутствует.
Score/grade: not evaluated — start/analyze не запускались.

## Execution — текущая обработка

Status: in progress
Result: начата status-first сверка, baseline и проверка текущих владельцев/подготовленного кандидата.
Updated: 2026-11-16T05:58:16.555133+03:00

## Текущая обработка

- Result: локальные проверки и сверка текущих владельцев.
- Updated: 2026-11-16T06:13:06.140352+03:00

## Execution — результат текущего исполнения

Status: completed
Result: candidate-v2 полного comm-migrate-git-repository опубликован в canonical/.agents/.claude;15 файлов равны. Codex20/20, A100, оба режима195/195, рабочий набор195 passed.
Reason: договор/текущие обязательные проверки выполнены; исходный when-read gap исправлен и повторно проверен, неудачные/невалидные исходные raw сохранены.
Report: ../../testing/evidence/2026-11-16-execute-migrate-git-repository-v2/2026-11-16-report.md
Updated: 2026-11-16T06:36:52.737086+03:00
Codex/common-only: verified (documented current scope)
Codex/common+project: verified (documented current scope)
Claude/common-only: not run; unverified
Claude/common+project: not run; unverified
Overall: unverified
