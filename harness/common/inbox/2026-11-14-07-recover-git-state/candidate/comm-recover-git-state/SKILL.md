---
name: comm-recover-git-state
description: Use when a Git operation is interrupted, a branch or commit appears lost, or an erroneous local/published result needs a recovery decision.
---

# Recover Git state

Inputs: intended recovery, repository/worktree, known SHAs and authority.

1. Inspect operation, refs/SHAs, files/index, publication and collaborators
   without changes. Use comm-verify-project-facts for uncertain results and
   harness/common/skills/comm-commit-task-stages/references/work-safety.md
   before any authorized mutation.
2. Before choosing read [recovery modes](references/modes.md).
   Show consequences and obtain missing decisions/permissions; retain existing
   scoped approvals. No automatic destructive reset, published-history rewrite,
   foreign-work cleanup or branch deletion.
3. During PR operations the local branch remains read only. If recovery needs
   its mutation, stop and await the user's preparation/recovery decision;
   never silently change scope or restore it.
4. Carry out only the agreed recovery. Local commits use comm-commit-task-stages;
   publishing/PR retain their own gates. Never delete remote main/master or
   any primary, integration or protected branch.
5. Verify expected refs and preserved files/staging, then affected behavior
   through the application or harness check owner. On discrepancy report and wait.

Done: actual recovered state and checks, or explicit unrecovered data/limitations.
This is Git recovery, not authority for production/data rollback.
