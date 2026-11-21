# WORKFLOW-48: единые владельцы рабочего поведения

Дата создания: 2026-10-07.

Пользователь выбрал убрать lessons и отдельно подтвердил пользу изменения
общего каркаса всем проектам. Планы остаются docs/plans; вариант новой top-level
категории plans не принят. Новый каркас содержит 11 root categories.

Rules/skills с условными ресурсами — единственные источники переиспользуемых
рабочих инструкций и опыта. Skills-first означает сначала нужное будущее
поведение и существующий владелец, а не отдельный skill для каждой ошибки.
Существенные основания/принятые контракты и доказательства сохраняют отдельные
роли. Причина: старый workflow направлял опыт в lessons, а guard требовал читать
там blocker procedure; lazy-first авторство не исправляло сохранение опыта.

Подробный общий blocker workflow нужен для любого permission/decision blocker,
а не только inbox; поэтому у него отдельный lazy skill, guard до выбора остаётся
коротким. Copy drift/permissions развивают существующих владельцев. CRLF
получает отдельный skill по явному scope; исправление и тесты уже существуют.
Процедуры docs/decisions/specs перенесены владельцам; принятые инварианты и
исторические основания сохранены. Архив lessons не создаётся.

Новые проекты используют явный JSON. Текущий project меняется адресно этой
миграцией; ordinary startup сохраняет legacy project и не очищает его сам.
Границы стадий, публикации, защищённых входов, common/project, uv и human
exclusion сохраняются; прежние статусы не приёмка новой версии.

Working owners: [inbox](../skills/comm-process-harness-inbox/SKILL.md),
[authoring](../skills/comm-create-lazy-claude-codex-skills/SKILL.md),
[installation](../skills/comm-install-harness/SKILL.md).
Карта требований/проверки: testing/evidence/2026-10-07-workflow-48-lessons-to-skills.
