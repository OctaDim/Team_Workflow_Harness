---
name: comm-confirm-database-design
description: Use when designing SQL schemas, startup, migrations, queries, transactions or sessions, or agreeing field storage and empty-value searches in any database.
---

# Agree database design

1. Inspect the stack, schema, migration history, startup, ownership and prior
   approvals read-only. Respect read-only references.
2. Прочитай файл `harness/common/skills/comm-confirm-database-design/references/choices.md` для применимой задачи. For SQL,
   check schema/initialization, queries and resource ownership independently.
   For any database, check applicable field-storage and empty-value decisions.
   Identify each specific approval and its source, or mark the choice OPEN.
   Preserve scoped approvals and delegated details.
3. For an OPEN choice recommend an approach and obtain explicit agreement.
   Compare all three alternatives for each applicable OPEN SQL block. A request
   to choose autonomously calls for a recommendation. Until approval, keep work
   read-only and defer dependent plans, specifications, code and decision records.
4. Follow the applicable checks in the resource. Save decisions, scope, reasons,
   exceptions, delegations and open questions in the project harness where
   authorized. If recording is blocked, flag it as pending and honor approvals
   for other authorized work.
5. Reopen material changes or new decisions only. Clarify ambiguous answers.
   Elapsed time, urgency, UI defaults and code do not establish approval.

Done when applicable decisions cover the work, checks are accounted for and
records are saved or pending permission. Deployment, production access and
protected-harness writes require their own authorization.
