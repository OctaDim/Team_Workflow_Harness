---
name: comm-confirm-database-design
description: Use when planning, specifying or changing SQL schemas, initialization, migrations, queries, transactions or connection/session ownership.
---

# Agree SQL database decisions

1. Inspect the stack, schema, migration history, startup, ownership and approvals
   without changes. Respect read-only references.
2. Before asking, read [choices](references/choices.md). Preserve settled approvals
   and delegated details; identify open decisions.
3. Separately agree schema/initialization, queries and resource ownership. Explain
   project-specific differences, required alternatives and recommendations.
   Resolve applicable migration, data-safety, transaction and library questions.
4. Wait for explicit unambiguous decisions. Silence, time, UI defaults, existing
   code and recommendations are not approval. Clarify ambiguity; stop dependent
   plans, specifications and implementation. Read-only investigation may continue.
5. Save decisions, scope, reasons, exceptions, delegated details and open questions
   in the project's harness under its placement permissions. Pending permission
   to save does not invalidate conversation approvals or block otherwise authorized
   work within them; keep the record pending without changing protected files.
6. Reopen only material new decisions or changes. No repeat approval for covered
   queries; missing context or permission blocks only dependent work.

Done: applicable choices are explicit, work stays within scope, and the record
is saved or explicitly pending permission. This grants no deployment, production
access or protected-harness write permission.
