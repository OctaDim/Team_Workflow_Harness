---
name: comm-confirm-database-design
description: Use when planning, specifying or changing SQL schemas, initialization, migrations, queries, transactions or connection/session ownership.
---

# Agree SQL database decisions

1. Inspect the stack, schema, migration history, startup, ownership and approvals
   without changes. Respect read-only references.
2. Read [choices](references/choices.md). Before any dependent write, check three
   entries: schema/initialization, queries, resource ownership. For each identify
   the user's specific decision and its source, or mark it OPEN. Preserve scoped
   approvals and delegated details; “choose yourself” leaves architecture OPEN.
3. If anything applicable is OPEN, compare all three alternatives per open block,
   justify recommendations and ask. Stop without writing a plan, specification,
   code or an accepted-decision record. Read-only investigation remains allowed.
4. Continue only after explicit decisions cover the work. Clarify ambiguity;
   urgency, silence, UI defaults, code and recommendations are not consent.
5. Save decisions, scope, reasons, exceptions, delegated details and open questions
   in the project's harness under its placement permissions. Pending permission
   to save does not invalidate conversation approvals or block otherwise authorized
   work within them; keep the record pending without changing protected files.
6. Reopen only material new decisions or changes. No repeat approval for covered
   queries; missing context or permission blocks only dependent work.

Done: applicable choices are explicit, work stays within scope, and the record
is saved or explicitly pending permission. This grants no deployment, production
access or protected-harness write permission.
