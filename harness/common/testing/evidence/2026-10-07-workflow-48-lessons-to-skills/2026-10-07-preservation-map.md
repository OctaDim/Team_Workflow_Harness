# Карта сохранения WORKFLOW-48

Дата создания: 2026-10-07. Это проверяемая карта итоговой миграции, не новая процедура.
Исходные bytes доступны в Git a3ce223; hashes: 2026-10-07-baseline-hashes.json. Новый WORKFLOW-48 план исключён из behavioral control; ограничения описаны в 2026-10-07-control-scope.json.
Долговременные сырые доказательства остаются в testing/evidence; отдельного архива lessons не создаётся.
Карта сверена независимым review по полным текстам четырёх lessons и действующих документов. Два найденных пропуска исправлены и повторно проверены; оставшихся потерь review не выявил. Это проверяемое покрытие, а не утверждение абсолютной гарантии. Финальный манифест 2026-10-07-publication-files.json перечисляет точные пути, исходные и итоговые hashes; результаты и ограничения собраны в 2026-10-07-report.md.

| Источник / требование | Канонический владелец | Проверка / доказательство |
|---|---|---|
| CRLF: исходные пользовательские bytes при узком ремонте, UTF-8 без универсальной нормализации | comm-preserve-text-line-endings + существующий common checker | test_repair_preserves_original_bytes_and_each_files_line_endings; старое CRLF evidence неизменно |
| CRLF: вставка по первому newline каждого файла, LF при отсутствии; CRLF import и Git comparison; повтор без дублей/ложных предупреждений | CRLF skill + references/regressions.md; прежняя автономная project копия отмечается только историей | LF/CRLF repair, bridge, Git/notification regressions; project wrapper compatibility |
| Inbox permission: номер варианта не разрешает создание/выполнение, включая тесты; один явный запрос может покрывать обе стадии | comm-process-harness-inbox/references/workflow.md; early ownership rule | inbox/native pressure scenario; сообщение пользователя о scope отдельно сохранено |
| Inbox permission: после ошибки предложить сохранение контекста/результата, запись/обработка только по разрешённым стадиям | inbox workflow | creation-only, execution, already-granted/no-reask сценарии |
| Copy drift: полный набор comm/proj, missing/extra, ordinary files/no symlinks, byte equality, исключение personal/human, пустой набор отказ | authoring placement-contract; installation check pointer | test_rule_copies.py текущая версия, negative controls |
| Copy drift: startup links ≠ copy completeness ≠ native load; restore проходит current gate, waiver сохраняет реальные статусы | authoring validation/placement + install checks | raw CLI traces, validator не native proof, current per-agent gate |
| Blockers: любые sandbox/access/filesystem/data-transfer/other блокировки, требующие нового разрешения или решения | short ownership guard + comm-resolve-permission-blockers | explicit/implicit native blocker scenario |
| Blockers: действие/факт/место/причина/источник/существенная ошибка; unknown vs hypothesis | blocker skill | raw RED failure/provenance + final native blocker manual review |
| Blockers: конкретное продолжение/пути/access; какие материалы какому сервису; UI location если нужны действия | blocker skill | native blocker outputs: конкретные материалы, получатель, источник и вопрос |
| Blockers: остановка, без обхода/подмены; только granted scope; silence/time/old assignment не grant; отказ соблюдается, new blocker требует new decision | short guard + blocker skill | native pressure с deadline/старым waiver/другим каналом, no writes check |
| Blockers: auto-review назвать именно auto-review, не обычными файловыми правами; запрос/ответ не повышает статусы | blocker skill + authoring gate | raw rejection + current statuses |
| Blockers exception: известное однозначное техническое исправление в разрешённых пределах делается самостоятельно | ownership rule + blocker skill | typo vs decision fork scenario |

## Живые скрытые процедуры

| Исходный документ | Действия → владелец | Что остаётся вне instructions |
|---|---|---|
| decisions/inbox-execution-status | stages/direct exception, request/status/resume/order/closure/result → inbox workflow | принятый контракт, причины idempotence и разделения статусов |
| docs/compact-authoring | RED/GREEN/REFACTOR, helpers, modes/status/gate/cost → authoring validation/content | причины компактного условного чтения |
| docs/plugin-eval-without-human | launcher/entrypoint/commands/limits/proof → authoring references/evaluation.md | scope/ограничения фильтра, история выбора |
| docs/skill-rule-ownership-contract | source/full native copies/prefixes/Git/copy conflicts → authoring placement; stage/status → inbox/validation | пояснение канонического владения |
| docs/protected-entrypoints | запуск/diagnosis/fences/Git/notifications/modes → install references/entrypoints.md + CRLF skill | причины warning-only и узкого исключения |
| docs/run-tests | env uv/setup/commands/import/config preservation → install references/testing.md | назначение lock/config/suite |
| specs/structure-and-creation-dates | placement/date evidence/migration map/unknown dates → install references/material-placement.md | формальный состав/семантика дат/исключения/режимы |
| decisions/architecture, ownership, structure, human-filter | обязательные процедуры → соответствующие rules/skills; текущие ссылки обновить | принятые решения, отменённые варианты явно исторические |
| testing/acceptance | условия/expected results остаются; шаги запуска → install/authoring | приёмочный контракт, без самостоятельного workflow |
| project/docs/epl-harness-audit, old plan | audit/historical, не runtime dependency | исходные результаты и provenance без переписывания |

## Проверка перед удалением

Нужны coverage review каждого пункта по итоговым bytes, current regression suite,
проверка ссылок/полных копий/оба режима, реальные отдельные native сценарии либо
отдельное подтверждённое исключение текущей непроверенной версии.
Структурная проверка не подтверждает агентское соблюдение.
