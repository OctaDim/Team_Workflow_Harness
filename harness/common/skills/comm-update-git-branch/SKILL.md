---
name: comm-update-git-branch
description: Use when resuming deferred branch work, synchronizing with integration, or preserving unfinished changes on a fresh base.
---

# Update a working branch

Inputs: task, repository/branch, agreed dependencies and authorized update.

1. Прочитай файл `harness/common/skills/comm-commit-task-stages/references/work-safety.md`
   перед изменением. Затем прочитай файл `harness/common/skills/comm-verify-project-facts/references/git-base-state.md`
   for identity, fresh target and recorded SHAs. Inspect divergence and both changesets.
2. Перед выбором способа сохранить изменения прочитай файл `harness/common/skills/comm-update-git-branch/references/methods.md`.
   Agree unresolved choices; a necessary feature dependency never excuses stale
   integration. Incorporate missing target changes before resumed implementation.
3. При явном конфликте или пересечении смысла изменений прочитай файл `harness/common/skills/comm-update-git-branch/references/conflicts.md`. Unknown intent/authority blocks dependent edits.
4. Verify saved behavior with the combined affected contracts on the resulting
   stable revision. Use comm-test-project-behavior, comm-assess-project-tests and
   comm-run-project-checks for application changes; harness checks use comm-validate-harness-instructions separately.
   Old green results do not verify the new version.
5. Recheck the target before final checks/integration under the base-state owner.
   Finish with labeled fields `old=<full SHA or unknown>`,
   `target=<full SHA or unknown>`, `result=<full SHA or not created>`,
   preservation, executed checks and gaps.

Done: work is compatible with the checked integration version, or a precise stop.
No push/PR/merge/deletion or local mutation within PR operations is granted.
Protected-harness changes retain inbox gates.
