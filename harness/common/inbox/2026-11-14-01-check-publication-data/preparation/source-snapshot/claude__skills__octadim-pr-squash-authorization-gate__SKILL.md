---
name: octadim-pr-squash-authorization-gate
description: Use when an Octadim request or plan mentions a PR, squash merge, or branch deletion, or when the agent is about to create or merge a pull request.
---

# PR and Squash Authorization Gate

Task or plan approval is **not** permission to create a PR or merge. An explicit instruction to make a PR authorizes the normal PR **and squash-merge** workflow after checks; the user need not say “squash” separately. Do not ask for another confirmation.

## Decision

| User instruction | Authorized action |
|---|---|
| “Выполни задачу” / “подтверждаю план” | Prepare reviewable work; no PR or merge. |
| “Сделай PR”, “сделай PR и squash”, or “PR, squash, remote-delete, local - read only” | Create the PR and squash-merge it after normal checks. |

Respect an explicit limit such as “PR без merge”. If the target is ambiguous, clarify which PR or repository; this is not a second approval. A PR/merge step in a plan, green tests, or tool approval grants neither action.

Delete a remote branch only if `remote-delete` or an equivalent is explicit. `local - read only` forbids local worktree/ref mutations; use remote tools or report the blocker.

**Red flags:** “The plan approved the PR”; “green code means I can open a PR”; “remote-delete is routine cleanup.” If an authorized action triggers production deployment, also apply `octadim-production-deploy-confirmation-gate`.
