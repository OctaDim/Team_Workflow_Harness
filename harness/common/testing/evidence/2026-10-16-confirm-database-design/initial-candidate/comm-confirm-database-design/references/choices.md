# Decisions before SQL work

Read before presenting questions. Ground every comparison and recommendation
in the inspected project. If evidence is missing, say what is unknown and ask;
do not choose an architecture by assumption. Existing code is evidence, not consent.

## Three independent choices

For each block present these alternatives, explain differences, recommend one
with project-specific reasons and obtain an explicit decision:

| Block | Required alternatives |
|---|---|
| Schema creation and initialization | Parameterized SQL via `.execute()` with explicit schema evolution; SQLAlchemy models/queries plus Alembic for schema creation and migrations; another suitable approach with project-specific justification. |
| Queries | Direct parameterized SQL via `.execute()`; SQLAlchemy Core and/or ORM query expressions, specifying the chosen API; another suitable approach with justification. |
| Resource ownership | Separate functions/context managers; a dedicated class owning engine and session factory; another suitable approach with justification. |

The schema choice does not settle queries or lifecycle. SQLAlchemy also executes
expressions through `.execute()`; distinguish expressions from handwritten SQL.
Do not force Python tools into another stack. If ORM sessions are inapplicable,
state that explicitly rather than introducing them. Values and DDL identifiers
need different safe handling; do not promise bind parameters cover identifiers.

## Applicable scope to resolve

- Separate provisioning the database from creating schemas/tables. Agree empty
  and existing database behavior, first/repeated/concurrent startup, DDL owner
  and migration application during startup versus deployment.
- Agree model modules, metadata, relationships, constraints and indexes at the
  level needed by this task; capture explicitly delegated implementation details.
- Agree migration tooling, legacy-history adoption, data preservation, failure
  and recovery behavior. Ask separately about `create_all()` and startup
  migration generation; neither follows automatically from ORM/Alembic selection.
- Agree sync/async use, per-process engine ownership, creation/closure,
  connection/session scope and passing, pool/timeouts where applicable,
  background tasks and isolation of concurrent operations.
- Agree transaction boundaries, commit/rollback, locks, retries and cancellation;
  query-layer organization, composable expressions and partial-query helpers;
  whether mixing query styles is allowed and its boundaries.
- Agree third-party internal SQL exceptions and ownership of their tables and
  migrations. A narrow exception is not permission for application-wide raw SQL.
- Agree verification of empty/existing schemas, upgrades/data preservation,
  repeated/concurrent startup and failure recovery; respect actual database
  access permissions. Do not silently run against production.

## Approval and record

Questions may be grouped if the reply unambiguously covers each open choice.
Do not silently omit a material issue as inapplicable: explain applicability or
obtain explicit delegation. Compare options before asking, not after selecting.

Capture accepted decisions, scope, reasons, exceptions, delegated details and
unresolved questions in the project's harness using existing placement rules.
Current-conversation approvals remain valid while a permitted durable save is
pending. Missing saving permission is not permission to change protected files.

Unchanged approvals need no repeat. Ask again when new material choices arise,
the proposed approach changes or scope expands. An approved direct-SQL library
exception, for example, does not authorize converting application queries to SQL.
Do not require separate approval for each query inside the agreed architecture.

No dependent plan, specification or code changes before the necessary explicit
decisions. Preliminary inspection and discussion remain permitted. This common
procedure contains no project-specific database policy.
