---
name: comm-confirm-database-design
description: Use before planning, specifying or changing SQL database schemas, initialization, migrations, queries, transactions or engine/connection/session lifecycle; obtain explicit project-specific decisions first.
---

# Agree SQL database decisions

1. Inspect the existing stack, schema, migration history, startup, data-access
   ownership and approved decisions without changes. Respect read-only references.
2. Before asking, read [choices](references/choices.md). Identify applicable
   open decisions; preserve settled approvals and explicitly delegated details.
3. Separately agree schema creation/initialization, query method, and
   engine/connection/session ownership. For each explain project-specific
   differences, offer the required alternatives and justify a recommendation.
   Also resolve applicable migration/data-safety, transaction and library exceptions.
4. Wait for explicit unambiguous decisions. Silence, elapsed time, UI defaults,
   existing code and your recommendation are not approval. Clarify ambiguity;
   stop dependent planning, specification and implementation until resolved.
   Read-only inspection and discussion options may continue.
5. Record decisions, scope, exceptions, delegated details and unresolved questions
   in the project's harness under current placement permissions. Then proceed
   within agreed boundaries; no approval per individual covered query is needed.
6. Reopen agreement for material new decisions or changes; do not repeat unchanged
   approvals. Missing context/permission blocks dependent work, not settled work.

Done: applicable choices have explicit decisions and a durable project record;
the plan/specification/code stays within their scope. This grants no deployment,
production access or protected-harness write permission.
