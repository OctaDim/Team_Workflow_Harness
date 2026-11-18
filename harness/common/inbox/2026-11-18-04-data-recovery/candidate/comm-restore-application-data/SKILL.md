---
name: comm-restore-application-data
description: Use when planning, rehearsing or performing data recovery from a backup or snapshot, including selective restoration and application data rollback.
---

# Restore application data

1. Identify the recovery source and point, target, affected records or stores,
   and later writes that could be lost. Propose targeted restoration when it
   covers the required scope and preserves other changes.
2. Rehearse from a consistent copy in an authorized isolated environment.
   Verify required records and dependencies, integrity, expected schema and
   relevant constraints or triggers. Exercise the affected application paths.
   Report unavailable checks as unverified.
3. Show the exact action, scope, effects on newer writes and rehearsal results.
   Obtain applicable authorization before changing the target. For production,
   follow [rollout confirmation](../comm-manage-production-rollout/SKILL.md).
   Protect newer writes using the project's concurrency controls and recheck
   target revisions before applying. Stop for changed scope, missing evidence
   or authorization.
4. Verify the same integrity and behavior after recovery. Report the scope
   actually restored, preserved or lost writes and any unresolved gaps.
