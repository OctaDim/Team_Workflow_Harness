---
name: comm-create-git-branch
description: Use when creating a new independent task or feature branch, especially from another unfinished branch or when its base or name is uncertain.
---

# Create a task branch

Inputs: agreed task/outcome, repository and authorized local operation.

1. Перед изменениями прочитай файл `harness/common/skills/comm-commit-task-stages/references/work-safety.md`.
   Прочитай файл `harness/common/skills/comm-verify-project-facts/references/git-base-state.md`
   for remote/integration identity, freshness and checked SHAs.
2. Independent work starts from that fresh remote integration SHA. Never
   implicitly inherit unfinished HEAD. Do not update/check out local integration
   merely to branch. Deferred/dependent work requires the update procedure first.
3. Перед выбором имени или созданием ветки прочитай файл `harness/common/skills/comm-create-git-branch/references/naming.md`.
   Unknown task/outcome, prefix, remote or collision needs the user's answer.
4. Use an explicit start SHA; create only a new local branch, without replacing
   an existing ref. If state changes or the host prevents creation, stop and report.
   Choose checkout/worktree placement within authority and work-safety limits.
5. Verify exact name, HEAD equals selected SHA, and preserved edits/staging.
   Report task, branch, source SHA and freshness limits; never claim uncreated work.

Done: the intended local branch exists on the verified base.
Commit, push, PR, harness execution and publication retain their own gates.
