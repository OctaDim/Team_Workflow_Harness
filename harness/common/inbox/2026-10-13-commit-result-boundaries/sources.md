# Источники политики частоты коммитов

Исследование для оформления заявки: 2026-10-13, Europe/Minsk.
Исходная ветка: `octadim/brainstorm`, HEAD `5d2762b`; рабочее дерево чистое.

## Канонические источники

| Источник | Найденное требование / изменение |
|---|---|
| `harness/common/skills/comm-commit-task-stages/SKILL.md`, строки 11–13 | Перед набором/каждой задачей, после каждого этапа, итог. Заменить полным кандидатом; определить самостоятельный проверенный результат. |
| `.agents/skills/comm-commit-task-stages/SKILL.md` | Полная Codex native-копия; синхронизировать при разрешённой публикации. |
| `.claude/skills/comm-commit-task-stages/SKILL.md` | Полная Claude native-копия; синхронизировать при разрешённой публикации. |
| `harness/common/rules/comm-skill-rule-ownership.md` | Canonical comm/proj приоритетнее индивидуальных навыков. Контракт сохраняется; новый guard конкретизирует частоту. |
| `harness/common/rules/comm-confirm-development-workflow.md` | Выбор маршрута/фазы сохраняется. Частоты коммитов не задаёт; название фазы не означает завершение результата. |

Копии commit-навыка побайтно совпадают с canonical. SHA-256 всех трёх исходников: `c808f8caf1fbb347b4963d457a8202674bcf7450f47a09e42179128797e1da06`. Машинный каталог навыка
содержит только SKILL.md, ресурсов нет. Новый guard
`harness/common/rules/comm-commit-result-boundaries.md` предлагается впервые;
его native-копия `.claude/rules/comm-commit-result-boundaries.md` ещё отсутствует.

Все восемь common rules прочитаны при старте; project/rules machine-файлов
не содержит. Поиск `commit|коммит` выполнен по текущим common/project
rules/skills/base, остальным машинным материалам вне исторических inbox/evidence
и native-копиям `.agents/skills`, `.claude/rules`, `.claude/skills`, исключая
README.human.md. Другого canonical владельца частоты нет. Упоминания hooks,
дат Git, исторических планов и тестовых fixture-коммитов не задают частоту.

Историческая заявка `harness/common/inbox/2026-10-10-task-stage-commits/request.md`
имеет completed и объясняет происхождение прежнего требования. Её исходные
поручения и evidence не переписываются. Новая заявка supersedes только будущую
политику после разрешённой обработки, не исторические результаты проверки.

## Внешние требования и согласованные адаптации

Это исходники установленных зависимостей, а не дополнительные canonical owners
harness. Их cache сейчас не меняется. Адаптации применяются общим canonical
guard/навыком; если позднее разрешено менять пакеты, те же формулировки меняют
у их владельцев с полной проверкой ресурсов. Ссылка на внешний навык не даёт
разрешения исполнять его, делегировать или публиковать изменения.

Корни текущих версий:

- **SP**: `/home/octadim/.codex/plugins/cache/openai-curated-remote/superpowers/6.4.2/skills`.
- **CE**: `/home/octadim/.codex/plugins/cache/compound-engineering-plugin/compound-engineering/3.30.5/skills`.
- **AS**: `/home/octadim/.codex/plugins/cache/agent-skills/agent-skills/0.6.12/skills`.

Пути таблицы разрешаются относительно этих корней; номера строк проверены
по текущим исходникам при поиске. Таблица — карта затрагиваемых требований,
не утверждение, что каждому внешнему файлу нужна отдельная локальная правка.

| Источник и строки | Частота / предлагаемое согласование |
|---|---|
| SP `brainstorming/SKILL.md`: 135, 244, 259 | Коммит готового design doc допустим после самостоятельного проверенного результата. Ответы и уточнения внутри дизайна коммитами не становятся. |
| SP `writing-plans/SKILL.md`: 10, 50, 132 | Frequent commits и commit-шаг шаблона: границы результатов независимо от числа шагов плана. |
| SP `executing-plans/SKILL.md`: 204, 229, 314 | Коммиты по шагам плана и ledger: связанные малые шаги группируются; ledger обновляется своевременно без триггера Git. |
| SP `subagent-driven-development/SKILL.md`: 70, 290, 406, 437 | Коммиты реализации/fix round: самостоятельные единицы результата, а не каждое замечание. Review range и восстановление сохраняются. |
| SP `subagent-driven-development/implementer-prompt.md`: 38, 48 | Commit your work: после проверки завершённого назначенного результата, не каждого редактирования. |
| SP `writing-skills/SKILL.md`: 667 | Финальный commit skill как самостоятельный результат авторства; политика частоты не разрешает push. |
| SP `using-git-worktrees/SKILL.md`: 86, 154 | Коммит .gitignore перед worktree: конкретная необходимость безопасной изоляции с объяснением исключения. |
| SP `using-superpowers/references/codex-tools.md`: 101 | Commit all work при завершении: только owned завершённые результаты; ограничения среды и shipping-разрешения сохраняются. |
| SP `finishing-a-development-branch/SKILL.md`: 187, 191 | Сохранение перед удалением worktree: объяснить риск потери; не удалять несохранённое. |
| SP `verification-before-completion/SKILL.md`: 3, 112 | Проверки до коммита/заявления успеха сохраняются; это gate, не частота. |
| AS `git-workflow-and-versioning/SKILL.md`: 34, 36, 98, 109, 113, 317 | Commit early/often, каждый increment и пороги строк: заменить интерпретацию общей политикой; исключить механические пороги. Независимые concerns остаются отдельно. |
| AS `incremental-implementation/SKILL.md`: 41, 139, 141, 181, 219, 241 | Each increment individually committed: малые шаги накапливаются до результата. Удаление/замена одной функции не требуют искусственно отдельных коммитов. |
| AS `spec-driven-development/SKILL.md`: 111, 222 | Commit spec: завершённая проверенная спецификация; промежуточные уточнения обновляются без обязательного коммита. |
| AS `context-engineering/SKILL.md`: 68, 133 | Совместимо: commit completed task по разрешению; не расширять save/update до каждого turn. |
| AS `performance-optimization/SKILL.md`: 153 | Keep → commit: самостоятельный проверенный эксперимент; его связанные малые коррекции объединяются. |
| AS `code-simplification/SKILL.md`: 165, 316 | Tests pass → commit or continue: по завершённому результату, не каждому зелёному тесту. |
| AS `constraint-driven-development/references/floor-guard.md`: 169 | Отдельные коммиты rename/threshold только для независимых смысловых изменений; диагностическое сообщение не дробит одну связанную правку. |
| CE `ce-commit/SKILL.md`: 10, 38, 46, 58 | Исполнитель, не владелец частоты. Передавать завершённый результат и явные файлы; его «2–3 max» для отдельных concerns не становится порогом частоты. |
| CE `ce-ideate/references/post-ideation-workflow.md`: 141, 142 | Offer commit идеационного документа: законченный результат; явный отказ/согласования пользователя сохраняются. |
| CE `ce-work/references/implementation-loop.md`: 59, 61 | Уже допускает valuable complete result и объединение small related units; сохранить смысл и применить ко всем фазам. |
| CE `ce-work/references/execution-strategy.md`: 49, 57, 63, 68–70 | Commit each unit и clean baseline: единицы по самостоятельному результату; baseline перед риском изоляции объяснять, проверки не обходить. |
| CE `ce-work/references/cross-model-execution.md`: 99, 116, 154, 166, 168 | Transaction требует host commit каждого unit: группировать малые связанные шаги до dispatch, не ломать recovery. Plan checkpoint обосновывать риском; transport commit не граница пользовательской истории. |
| CE `ce-work/references/return-to-caller.md`: 5 | Commit каждого completed unit: та же единица результата, не каждый возврат или ответ. |
| CE `ce-work/references/review-findings-followup.md`: 74 | Commit после inline/wave: общий проверенный результат исправлений, не каждый finding. |
| CE `ce-work/references/non-code-execution.md`: 12, 19 | Save deliverable/offer commit: своевременная запись не trigger. Явный отказ и согласования сохраняются. |
| CE `ce-plan/references/structure.md`: 46 | Meaningful logical units совместимы; не назначать отдельный commit каждому checkbox. |
| CE `ce-code-review/references/finish-review.md`: 100, 102, 103 | Один verified review-fix commit совместим для самостоятельного завершённого review; связанные fixes внутри стадии вместе, чужой WIP сохраняется. |
| CE `ce-debug/references/return-to-caller.md`: 3, 15, 52 | Commit verified fix при возврате: самостоятельная проблема, не каждое уточнение, гипотеза или попытка. |
| CE `ce-debug/references/pipeline-mode.md`: 7, 14 | Частота fix commit по результату; push только при отдельно унаследованном разрешении. |
| CE `ce-resolve-pr-feedback/references/full-mode.md`: 150, 158, 167 | Коммит общего проверенного fix batch; связанные findings вместе, самостоятельные batches отдельно. |
| CE `ce-resolve-pr-feedback/references/return-to-caller.md`: 25 | Combined fix commit совместим; не добавлять commit на каждый feedback item/reply. |
| CE `ce-compound-refresh/SKILL.md`: 84, 88 | Refresh и поздняя discoverability правка накапливаются до завершения общего результата; отдельный save не trigger. |
| CE `ce-compound-refresh/references/commit.md`: 3, 5, 7 | Commit завершённого refresh; automatic PR не разрешается политикой частоты. |
| CE `ce-dogfood/references/phases.md`: 151, 165 | Каждый fix и отдельный report commit: связанные fixes одной проблемы объединить; report отдельно только как самостоятельный проверенный результат. |
| CE `ce-optimize/references/loop.md`: 198, 199, 202 | Winning experiment перед merge/cherry-pick: самостоятельный результат/обоснованный риск переноса. Merge отдельно разрешается. |
| CE `ce-retune/references/cut-passes.md`: 15, 127 | Каждый pass отдельно: только самостоятельные проверенные результаты, не каждая малая коррекция. |
| CE `ce-polish/references/live-loop.md`: 73, 93 | Уже накапливает правки до закрытия сессии; каждый ответ/checkpoint не trigger. |
| CE `ce-polish/references/install-riffrec.md`: 31 | Setup commit: самостоятельная готовая установка либо safety checkpoint; dependency/lockfile/mount вместе. |
| CE `ce-sweep/references/run.md`: 12, 41, 120 | State each run и push-gated lease: завершённый sweep; lease — безопасность, не обычная частота. Не обходить mutex и не выдавать новое push-разрешение. |
| CE `lfg/references/review-followup.md`: 13, 56 | Simplify до общего коммита совместимо; review fixes по самостоятельному результату. |
| CE `lfg/references/shipping.md`: 15, 17 | Финальный commit remaining results совместим. Shipping остаётся отдельно разрешённым. |
| CE `ce-commit-push-pr/references/commit-and-push.md`: 7, 9 | Logical concerns при разрешённом shipping: не разделять связанные мелочи; push/PR не следуют из частоты. |

## Упоминания, не задающие частоту

CE brainstorm (`interaction-rules.md`, `plan-write.md`) не требует Git-коммита
каждого ответа. В CE ideate/universal-ideation, CE plan/synthesis-summary и
AS interview-me/idea-refine commit/commitment также означает принятие решения:
не заменять эту семантику механически по одному совпадению слова.

`comm-process-harness-inbox`, `comm-create-lazy-claude-codex-skills` и
`comm-preserve-harness-knowledge` задают маршруты и своевременное сохранение,
а не коммит каждого обновления. Их назначение не расширяется. Проверки,
безопасность AS, ownership/exclude и все действующие разрешения сохраняются.
CE compound фиксирует знания после завершённой проблемы, не каждый ответ/запись.

Расширенный read-only поиск выполнен по всем machine Markdown пакетов CE 3.30.5,
SP 6.4.2, AS 0.6.12, локальных `/home/octadim/.codex/skills`,
`/home/octadim/.agents/skills` и Ponytail 5.1.0, исключая README.human.md.
820 строк буквального `commit|коммит` включают commitment, примеры, историю и
Git-ссылки. Таблица перечисляет требования частоты/сохранения, gates и точки
согласования; число совпадений не является тестом поведения. Дополнительные
пакетные файлы CE, например dogfood/sweep/retune, включены для полноты исследования:
наличие на диске не означает их применение в выбранном маршруте.

Политика не обходит controlled integration, transport, восстановление и shared
lease. Технические snapshots не разрешают дробить canonical history. Связанные
шаги группируются до запуска механизма; если недостаточно, объясняется конкретное
safety-исключение или согласуется конфликт до зависимой операции.

Поведение кандидата, native loading и оба режима установки пока не проверены.
