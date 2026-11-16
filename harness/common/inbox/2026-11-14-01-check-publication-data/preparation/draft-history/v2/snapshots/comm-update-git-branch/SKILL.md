---
name: comm-update-git-branch
description: Use when resuming deferred branch work, synchronizing with integration, or preserving unfinished changes on a fresh base.
---

# Update a working branch

Inputs: task, repository/branch, agreed dependencies and authorized update.

1. Read harness/common/skills/comm-commit-task-stages/references/work-safety.md
   before mutation and
   harness/common/skills/comm-verify-project-facts/references/git-base-state.md
   for identity, fresh target and recorded SHAs. Inspect divergence and both changesets.
2. Before choosing preservation read [methods](references/methods.md).
   Agree unresolved choices; a necessary feature dependency never excuses stale
   integration. Incorporate missing target changes before resumed implementation.
3. For explicit conflicts or relevant semantic overlap read
   [conflicts](references/conflicts.md). Unknown intent/authority blocks dependent edits.
4. Verify saved behavior with the combined affected contracts on the resulting
   stable revision. Use comm-test-project-behavior, comm-assess-project-tests and
   comm-run-project-checks for application changes; harness validation stays separate.
   Old green results do not verify the new version.
5. Recheck the target before final checks/integration under the base-state owner.
   Report old/target/result SHAs, preservation, checks and remaining gaps.

Done: work is compatible with the checked integration version, or a precise stop.
No push/PR/merge/deletion or local mutation within PR operations is granted.
Protected-harness changes retain inbox gates.
