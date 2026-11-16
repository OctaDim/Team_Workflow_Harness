# Decisions before SQL work

Read before questions. Ground comparisons and recommendations in the inspected
project. Name missing evidence and ask; existing code is not consent.

## Three independent choices

For each block explain alternatives, recommend with project-specific reasons
and obtain an explicit decision:

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

Group questions only when the reply unambiguously covers every open choice.
Explain applicability or obtain delegation; never silently omit material issues.
Compare before asking, not after selecting.

Follow the skill's approval and recording steps. Library exceptions do not
authorize converting application queries to raw SQL. This common procedure
contains no project-specific database policy.
