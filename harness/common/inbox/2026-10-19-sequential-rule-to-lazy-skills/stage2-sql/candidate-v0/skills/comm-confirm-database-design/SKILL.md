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
   approvals and delegated details. When architecture is OPEN, “choose yourself”
   requests a reasonable recommendation, not approval of an unseen design.
3. If anything applicable is OPEN, compare all three alternatives per open block,
   recommend a reasonable architecture and ask for explicit agreement. Proposing
   the recommended architecture is not permission to write a plan without explicit
   agreement with the user. Stop without writing a plan, specification,
   code or an accepted-decision record. Read-only investigation remains allowed.
4. Continue only after explicit decisions cover the work. Clarify ambiguity;
   urgency, silence, UI defaults, code and recommendations are not consent.
5. Save decisions, scope, reasons, exceptions, delegated details and open questions
   in the project's harness under its placement permissions. If recording lacks
   permission, keep it pending; conversation approvals still permit otherwise
   authorized work within their scope.
6. Reopen only material new decisions or changes. No repeat approval for covered
   queries; missing context or permission blocks only dependent work.

Done: decisions cover the work; their record is saved or pending permission.
This grants no deployment, production access or protected-harness write permission.
