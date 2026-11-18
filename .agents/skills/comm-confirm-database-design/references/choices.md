# Database design choices

## Any database

- Agree whether each affected field can store `NULL` or its equivalent and
  whether omission is allowed if supported. If the application uses `None` or
  `nil`, agree its representation on write.
- For empty-value searches separately agree whether to return records with
  `NULL`, a missing field, `""`, `0`, `False`, or an unset date or time.
  Encode and test each applicable case using the database's query semantics.
  Zero and false can be explicit answers. Follow the field and query contracts.

## SQL decisions

Compare three distinct alternatives for each open block. Recommend one with
project-specific reasons and get explicit approval.

| Block | Alternatives |
| --- | --- |
| Schema and initialization | Explicit evolution via parameterized SQL `.execute()`. SQLAlchemy models/queries with Alembic. A justified distinct mechanism. |
| Queries | Direct parameterized SQL via `.execute()`. SQLAlchemy Core and/or ORM expressions, naming the API. Another suitable query builder, ORM or approach. |
| Resource ownership | Functions/context managers. A class owning engine and session factory. Another owner, such as framework-owned injected connections. |

Show each schema alternative in its own row with mechanism, migration executor
and project fit/tradeoff. Check mechanism and owner for real differences.
SQL files and `user_version` are variants of explicit SQL. Core and ORM are
SQLAlchemy subchoices. Connection duration alone leaves ownership unchanged.
If a distinct third approach is missing, explain the gap and ask. Use
stack-appropriate tools, explain inapplicable ORM sessions and handle DDL
identifiers separately from bound values.

- Separate provisioning from schema/table creation. Agree empty/existing,
  first/repeated/concurrent startup, DDL owner and startup/deploy migrations.
- Agree model modules, metadata, relationships, constraints and indexes.
  Agree migration tooling, legacy history, preservation, failures and recovery.
  Decide `create_all()` and startup migration generation separately.
- Agree sync/async use, engine ownership per process, creation/closure,
  connection/session scope and passing, pools/timeouts, background tasks
  and concurrent isolation.
- Agree transaction boundaries, commit/rollback, locks, retries, cancellation
  and query organization, composition, helpers and style mixing.
- Scope third-party SQL exceptions to their tables/migrations and agreed callers.

## Migration and transaction checks

- Verify the affected contract on a temporary database built by the project's
  migrations. For existing data start at a supported earlier version with
  representative records. Test permitted and prohibited operations for affected
  constraints or triggers. Cover applicable startup and recovery paths.
- When the caller owns commit, test on an isolated database with the production
  database system and driver. After caller `ROLLBACK`, verify the original
  affected data in a new session.
- For supported schema rollback agree data compatibility. Incompatible data
  must stop rollback before schema or data changes. Test success and rejection
  in isolation. After rejection check unchanged schema, data and revision.
- Before applying migrations verify the command's actual target using the
  tool's configuration precedence. Match the designated test or agreed working
  database. If unclear, stop before applying. Explain in detail which settings
  determine the target, what is unknown, and which data or schema objects the
  command could change on a wrong target. Ask for an explicit decision and wait.
  Recheck the resolved target before applying. Respect access permissions.
- After integrating branches that both changed migrations, check order,
  dependencies and expected target revisions with project tooling. In isolation run
  the normal upgrade from the integration branch's schema to the agreed target
  and verify all expected steps applied.
