"""Build the complete candidate using the existing owners; never publish."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent / 'candidate'
COMMON = ROOT / 'harness/common'


def write(path, content):
    target = COMMON / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.strip() + '\n', encoding='utf-8')


write('skills/comm-process-harness-inbox/SKILL.md', '''
---
name: comm-process-harness-inbox
description: Use when saving reusable experience or a decision in harness, choosing its permanent form, creating or processing inbox requests, or resuming their execution.
---

# Сохранение опыта и обработка inbox

При «сохрани опыт», «зафиксируй решение», «дополни harness» до выбора места
прочитай [выбор результата](references/experience-routing.md): будущее
поведение, существующий владелец, минимальное изменение. Skills-first не
означает отдельный скилл для каждой ошибки. Определи common/project по содержанию.

До записи, выполнения или изменения статуса прочитай
[workflow](references/workflow.md): разрешённые стадии, полный кандидат,
контекст, порядок, продолжение и закрытие. Обычный маршрут — подтверждённый inbox;
готовый кандидат без обязательной публикации заявку не закрывает.

До создания/изменения/проверки/публикации скилла или правила открой из корня
проекта `harness/common/skills/comm-create-lazy-claude-codex-skills/SKILL.md`.
Сохраняй долговременный результат независимо от временной заявки.
''')
write('skills/comm-process-harness-inbox/references/experience-routing.md', '''
# Выбор долговременного результата

До записи опыта сначала определи поведение, необходимое в следующем похожем
случае. Проверь descriptions существующих скиллов, применимые rules, а затем
только подходящие bodies/resources и исполняемые проверки.

- Сценарий уже покрыт: используй или дополни существующую инструкцию/ресурс;
  если всё необходимое уже выражено инструкцией, новой записи не создавай.
- Самостоятельная повторяемая компетенция с распознаваемым trigger: компактный
  lazy skill. Для преобразования опыта открой из корня проекта
  `harness/common/skills/comm-create-lazy-claude-codex-skills/SKILL.md`.
- Rule нужен только для ограничения до выбора процедуры: назови конкретное
  ошибочное действие, возможное до выбора скилла. Обязательность алгоритма
  сама по себе не основание для always-loaded rule.
- Подробности, примеры, объяснения применения: условно читаемый ресурс
  владельца скилла, с точным указателем когда открыть.

Отдельно сохраняй лишь существенные основания/доказательства. Не переносить
рассказ ошибки целиком в SKILL.md и не создавать ещё один маршрутизатор.
Наличие исправления/теста проверяй при выборе; оно само по себе не заменяет
необходимой инструкции будущего поведения.

| Материал | Постоянное место |
|---|---|
| Переиспользуемое рабочее поведение и применимый опыт | skills + ресурсы; ранние границы — rules |
| Принятые решения, контракты, инварианты, ограничения, существенные альтернативы | decisions |
| Результаты, ограничения проверок, исходные свидетельства | testing/evidence |
| Базовые контракты, конфигурации, настройки | base |
| Спецификации | specs |
| Объяснения и исследования | docs |
| Планы | docs/plans |
| Незавершённое состояние | handoffs |

Inbox хранит временную заявку и полный кандидат, не единственный постоянный
результат. Docs/decisions/specs/evidence и отчёты не задают самостоятельных
агентских процедур: действия принадлежат rules/skills, документы — основаниям
или формальному контракту. Для фактического размещения прочитай из корня
проекта `harness/common/skills/comm-install-harness/references/material-placement.md`.
''')
write('skills/comm-process-harness-inbox/references/workflow.md', '''
# Разрешения, выполнение и учёт

До действий различай создание заявки, выполнение (включая добавление тестов),
публикацию и исключение маршрута. Установи явное разрешение каждой нужной стадии
из запроса или ответа на конкретный предложенный состав действий. Не расширяй
«разрешаю» на непредложенное. Одно сообщение может разрешить несколько стадий;
уже полученное разрешение сохраняется, повторного вопроса не требует.

«Сохрани», конечный путь, срок или номер варианта не разрешают недостающие
стадии. Номер определяет решение; при требовании отдельного согласования до
разрешения не создавать заявку и не выполнять её, включая тесты. Создание
не разрешает выполнение. Обычную просьбу сохранить сначала направляй в inbox.
Прямой путь требует явного разрешения и подтверждения записи названного
материала в указанную категорию, минуя inbox; обязательной буквальной фразы
нет. Этот обход не отменяет проверок, gate и защиты AGENTS/CLAUDE.

После ошибки/конфликта/найденного решения предложи сохранение контекста и
требуемого результата в заявку. Запись и обработку выполняй лишь в разрешённых
пределах; не считать ошибку новым разрешением. Выбор постоянной формы —
[experience-routing](experience-routing.md), не автоматическая отдельная история.

Создай отдельную `harness/<пакет>/inbox/YYYY-MM-DD-суть/` с фактической датой
создания. Совпадение имени уточни смыслом. Request содержит когда возникла
потребность, обстоятельства, причину, что решит выполнение, требуемый результат.
Не выдумывай неизвестные даты. Для скилла/правила без подтверждённого прямого
пути приложи полную папку со всеми ресурсами либо полный файл правила.

В «Выполнение» каждой заявки сохраняй Статус, Результат, Причину и дату
обновления; старой одиночной Markdown-заявки — в её собственном файле.
Статусы: новая/в работе/выполнена/заблокирована/отклонена. До начала результат
«не выполнялась», при начале — «в работе». После работы/остановки обновляй
все поля: фактические артефакты и оставшееся, причина состояния. Сохраняй
прежние результаты и ссылки. При групповой обработке учёт отдельный.

До обработки выбранных заявок прочитай их статус/результат/причину:
- Выполнена: пропустить, повторить только по явной просьбе.
- В работе: сверить фактические артефакты и продолжить оставшееся.
- Заблокирована: проверить препятствие; если осталось — обновить причину и
  сообщить, если устранено — продолжить разрешённое.
- Отклонена: учитывать отказ, возобновить только по явному запросу.
- Нет статуса: сверить прежние отчёты и фактический результат; поле отсутствует
  не значит выполнено или нужно повторение. Неясность явно записать.

Выполняй выбранные заявки по одной от ранней к поздней. Не запускать разные
заявки одновременно и не начинать следующую до закрытия предыдущей. Неясный
порядок согласуй до зависимой работы, не придумывая даты. Закрытие — достигнутый
результат и завершённая обязательная работа либо явное решение пользователя.
Готовый неопубликованный кандидат, «в работе», «заблокирована» — не закрытие.

Недостающее разрешение/развилка/конфликт: конкретный вопрос, ожидание ответа,
без следующей заявки и зависимых действий. Молчание/время/старое общее поручение
не ответ. При permission blocker, включая auto-review, до продолжения открой
из корня проекта `harness/common/skills/comm-resolve-permission-blockers/SKILL.md`.
Известную однозначную техническую ошибку исправляй в разрешённых пределах;
это не позволяет выбирать за пользователя или обходить отказ.

Постоянный результат по [experience-routing](experience-routing.md) понятен без
заявки; ссылка на неё лишь provenance. В итоговом ответе перечисли выполненные,
пропущенные завершённые и оставшиеся заявки с причинами. Учёт выполнения не
повышает отдельные статусы Codex/Claude, включая непроверенную публикацию.
''')

p = COMMON / 'skills/comm-create-lazy-claude-codex-skills/SKILL.md'
s = p.read_text().replace('including harness inbox candidates.', 'or turning reusable experience into working instructions, including harness inbox candidates.')
s = s.replace('Keep discovery in name/description;', 'For reusable experience first read from the project root\n`harness/common/skills/comm-process-harness-inbox/references/experience-routing.md`: choose future behavior and an existing owner before creating a new artifact.\n\nKeep discovery in name/description;')
p.write_text(s)
p = COMMON / 'skills/comm-create-lazy-claude-codex-skills/references/content-contract.md'
s = p.read_text().replace('Lazy-first for recognizable tasks; reuse skills/resources.', 'Skills-first for reusable experience and recognizable tasks; reuse existing\nskills/rules/resources/checks. If an instruction already expresses everything\nneeded, do not create another record. Independent repeated competence needs a\nprecise trigger; keep reasons/evidence separate, not a story inside SKILL.md.')
p.write_text(s)
p = COMMON / 'skills/comm-create-lazy-claude-codex-skills/references/validation-and-publication.md'
s = p.read_text().replace('Authoring/testing: read `harness/common/docs/2026-10-05-compact-authoring.md`:', 'Authoring/testing: record applicability, required actions and observable compliance,\nincluding limits/approvals/stops/missing data; name the test scenarios. Follow:')
s = s.replace('Before plugin-eval read `harness/common/docs/2026-10-06-plugin-eval-without-human.md`:', 'Before plugin-eval read [evaluation](evaluation.md):')
s = s.replace('Plain rules:', 'Do not publish/test an artificial long draft merely to shorten it; measure the\ncompact candidate itself. Every moved detail retains a tested when-read pointer.\nPlain rules:')
s = s.replace('Evidence: testing/evidence; history: inbox.', 'Evidence: testing/evidence (not checks); temporary candidate/history: inbox.\nPermanent rationale must survive inbox deletion. For suite commands/configuration\nread `harness/common/skills/comm-install-harness/references/testing.md` only when\nrunning/installing the harness tests.')
p.write_text(s)
p = COMMON / 'skills/comm-create-lazy-claude-codex-skills/references/placement-contract.md'
s = p.read_text() + '''

Check the **entire** canonical comm-/proj- rule set of installed packages, not
just changed files: no missing/extra shared copies, ordinary files at every path
component, equal bytes; ignore personal rules and README.human.md. An empty
canonical selection fails, not passes. Run the existing
`harness/common/testing/tests/test_rule_copies.py` via pytest: it exercises
missing/different/symlink/extra controls for both modes. Entrypoint link success
does not prove copy completeness; neither proves native agent loading.
Restore copies only through the current publication gate; an authorized exception
retains actual statuses. Keep the full skill folder resource set equal too.
'''
p.write_text(s)
old = (COMMON / 'docs/2026-10-06-plugin-eval-without-human.md').read_text()
old = old.split('## Подключение')[0]
write('skills/comm-create-lazy-claude-codex-skills/references/evaluation.md', old)

write('skills/comm-install-harness/SKILL.md', '''
---
name: comm-install-harness
description: Use when installing, moving or diagnosing harness packages or entrypoints, placing harness materials, or changing the shared project skeleton.
---

# Install or migrate harness

Before an installation change read [checks](references/checks.md): two modes,
existing-project preservation, isolation and shared-template approvals.
Common is mandatory. Identify the destination; chat cwd does not establish it.

For entrypoint diagnosis read [entrypoints](references/entrypoints.md).
For byte/CRLF damage during narrow text repair use from the project root
`harness/common/skills/comm-preserve-text-line-endings/SKILL.md`.
Do not directly edit protected entrypoints or rewrite an existing startup command.

Before material placement/date migration read [placement](references/material-placement.md).
For running/installing the harness suite read [testing](references/testing.md).
Only open resources for the current action. Skill/rule authoring and native
installation require `harness/common/skills/comm-create-lazy-claude-codex-skills/SKILL.md`
from the target root. Copy equality does not prove native agent behavior.
''')
p = COMMON / 'skills/comm-install-harness/references/checks.md'
s = p.read_text().replace('Diagnostic warning text is in protected-entrypoints.', 'For warning/error diagnosis read [entrypoints](entrypoints.md).')
s = s.replace('Read structure-and-creation-dates from the target common specs before placement:', 'Before placement read [material placement](material-placement.md):')
s += '\nNew approved projects have no lessons category; plans remain docs/plans.\nExisting legacy folders survive ordinary startup; remove them only through an\nauthorized addressed migration after requirement mapping and current checks.\n'
p.write_text(s)
old = (COMMON / 'docs/2026-10-05-protected-entrypoints.md').read_text()
old = old.split('## Два режима установки')[0]
old = old.replace('[Заявка и проверки исправления](../inbox/2026-10-05-entrypoint-fenced-code/validation.md)', 'Историческое исправление fenced-блоков отражено в Git; текущие регрессии — test_ensure_entrypoint_links.py и test_entrypoint_notifications.py.')
write('skills/comm-install-harness/references/entrypoints.md', old)
write('skills/comm-install-harness/references/testing.md', (COMMON / 'docs/2026-10-06-run-tests.md').read_text())
write('skills/comm-install-harness/references/material-placement.md', '''
# Размещение и миграция материалов

При размещении соблюдай формальный состав и семантику дат в
`harness/common/specs/2026-10-06-structure-and-creation-dates.md` из корня проекта.
Для выбора формы опыта до записи используй
`harness/common/skills/comm-process-harness-inbox/references/experience-routing.md`.
Common — общее переносимое; project — зависящее от проектного контракта.
Не дублировать знания обоих пакетов и массово не преобразовывать старые inbox.

Дата YYYY-MM-DD — доказанная дата создания, не обновления. Правка не меняет имя.
Предметная папка получает собственную дату создания, независимую от новых файлов
внутри. Для старого материала проверь историю создания с rename/move либо явно
записанный факт. Дата проверки/решения/import commit/checkout mtime сама по себе
не доказательство. Неизвестную дату конкретного материала согласуй до rename;
не придумывай её. No watchers/hooks/auto date updates/maintained date manifest.
Нативные skill/rule names и их ресурсы сохраняют технические имена спецификации.
Новой папке сразу нужен human guide; тела исключить из агентского чтения.

Для миграции сохрани карту old/new paths, исходные hashes и raw evidence.
Каждое переносимое требование сопоставь владельцу и проверке. После полного
coverage review и текущих checks исправь рабочие ссылки/команды, затем удаляй
освобождённые источники. Не создавать архив lessons. Исторические команды и
результаты оставить явно прошлой проверкой, не переписывать как новый успех.
Проверить tests, ссылки/ресурсы, обе чистые установки, идемпотентность,
project-only refusal, сохранение существующих файлов, source/native sets/bytes.
Изменения instructions/resources сбрасывают отдельные Codex/Claude статусы;
current gate остаётся. AGENTS/CLAUDE напрямую не редактировать.

Общий шаблон менять только по отдельной common inbox заявке, отдельному решению
и подтверждению пользы всем проектам. Новый project использует шаблон; обычный
старт существующий project не мигрирует. Его изменение — отдельная разрешённая
адресная работа. Plan files остаются docs/plans, не новая root category.
''')

# Early guards retain their owner; details are lazy skill actions.
p = COMMON / 'rules/comm-skill-rule-ownership.md'
s = p.read_text().replace('- До записи/обработки заявки или памяти открой из корня проекта', '- При «сохрани опыт», «зафиксируй решение», «дополни harness» до записи\n  сначала определи будущее поведение и подходящий существующий скилл.\n  Не создавать новый материал, если всё уже выражено инструкцией.\n  До записи/обработки заявки или памяти открой из корня проекта')
s = s.replace('При блокировке любого действия, включая auto-review, до продолжения открой\n`harness/common/lessons/2026-10-06-comm-blockers-explicit-permission.md`:\nобъясни действие/причину/источник/получателя передачи, запроси конкретное\nнедостающее разрешение и жди ответа.', 'Если для устранения блокировки нужно новое разрешение/решение, включая\nauto-review, остановись без обхода/подмены и до ответа открой из корня проекта\n`harness/common/skills/comm-resolve-permission-blockers/SKILL.md`.\nОбъясни действие/причину/источник/получателя, запроси конкретное решение и жди.\nМолчание/время/старое поручение не разрешение. Отказ соблюдай; новая блокировка\nтребует нового решения. Однозначное техническое исправление в разрешённых\nпределах вопроса не требует.')
p.write_text(s)
p = COMMON / 'rules/comm-package-independence.md'
p.write_text(p.read_text().replace('`harness/common/specs/2026-10-06-structure-and-creation-dates.md`.', '`harness/common/skills/comm-install-harness/references/material-placement.md`.'))
for name in ['comm-entrypoint-links-rule.md', 'comm-user-owned-entrypoints.md']:
    p = COMMON / 'rules' / name
    p.write_text(p.read_text().replace('harness/common/docs/2026-10-05-protected-entrypoints.md', 'harness/common/skills/comm-install-harness/references/entrypoints.md'))

if __name__ == '__main__':
    print('Existing skill owners and early guards staged; no publication.')
