---
name: comm-process-pull-request
description: Use when creating or completing a PR, selecting squash-merge or remote deletion, or enforcing local-branch read-only limits during PR operations.
---

# Process a PR

Inputs: repository, head/base and authorized scope.

Before creation show and await one explicit choice:

1. Обычный PR (pull request)
2. PR (pull request) + squash-merge
3. PR (pull request) + squash-merge + удаление remote ветки

Bind the choice to this PR/scope; reuse it without repeat approval.
Missing/ambiguous answers require clarification and waiting, never a default.
General task approval or green checks alone grants no PR/merge.

Agent/tools must never modify/delete the local branch during any PR operation,
including helpers/cleanup. User manual deletion remains allowed: install no
technical block and never delete as their proxy. Never use gh pr merge --delete-branch.
If local changes are needed, stop for an agreed preparation scope.

Перед созданием, правкой или слиянием PR прочитай файл `harness/common/skills/comm-check-publication-data/SKILL.md` и файл `harness/common/skills/comm-commit-task-stages/references/message-transfer.md`. Выполни описанные проверки.
Перед созданием PR или правкой его описания прочитай файл `harness/common/skills/comm-process-pull-request/references/preparation.md`;
перед слиянием в вариантах 2 и 3 прочитай файл `harness/common/skills/comm-process-pull-request/references/merge.md`;
перед удалением в варианте 3 прочитай файл `harness/common/skills/comm-process-pull-request/references/remote-deletion.md`.

Done: report the PR URL and actual selected-stage results/SHAs/gaps.
Protected-harness and production permissions remain separate.
