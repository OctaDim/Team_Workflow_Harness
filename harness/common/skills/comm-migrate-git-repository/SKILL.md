---
name: comm-migrate-git-repository
description: Use when transferring, renaming, duplicating or moving a repository between owners or hosting platforms and checking its linked integrations.
---

# Migrate a repository

Inputs: source/destination, purpose, retained properties and authorized stages.

1. Establish transfer/rename versus independent copy/cross-platform migration.
   Compare suitable current mechanisms using comm-choose-effective-solution;
   agree unresolved identity, method and scope before mutation.
2. Before planning the concrete move read [inventory](references/inventory.md);
   for host behavior read [platform conditions](references/platform.md).
   Inspect current configuration; private access remains bounded.
3. Before mutation read
   `harness/common/skills/comm-commit-task-stages/references/work-safety.md`;
   preserve evidence/recovery points. Execute only the authorized method; mirroring/import is not automatic authority
   to replace/delete refs, remove the source, change visibility or grants.
   Never delete remote main/master or any primary, integration or protected branch.
4. Update authorized current consumers and test relevant retained properties/
   integrations through existing fact/check owners. Report actual identity,
   revisions, transferred/missing items and remaining decisions.
5. Distinguish current links, correct historical names and immutable evidence.
   No blanket owner-name replacement; no unauthorized historical rewrite.

Done: the intended repository and required links/integrations are verified,
or explicit gaps remain. Production, credentials and protected-harness operations
retain their own permissions and procedures.
