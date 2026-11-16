---
name: octadim-merge-updated-main-into-cur-branch-pr
description: >-
  Use when asked to update, sync, refresh, or bring a PR/task/feature branch up to date with main/master/trunk, or to finish its associated PR, including “merge latest main into the current branch”, “fetch and merge main”, “подтяни/обнови main”, “влей/смерджи main в текущую ветку”, “синхронизируй/актуализируй ветку” or “обнови PR-ветку”; not for direct branch-to-main merges outside an associated PR or for rebasing.
---

# Merge Updated Main Into Current PR Branch

Safely fetch the integration branch and merge it into the current task branch while preserving both sides. Use merge, not rebase, for a published branch.

## Trigger vocabulary / Синонимы

- English: update/sync/refresh from main, merge latest main, bring the branch up to date, catch up with main, merge master/trunk, refresh the PR branch, squash-merge the associated PR into remote main, squash the PR into main, merge the PR with squash.
- Русский: подтяни/обнови main, влей/смерджи main, подтяни изменения из main, синхронизируй/актуализируй текущую ветку, обнови PR-ветку, сделай squash-merge PR в удалённый main, сквош-смерджи PR в main, влей PR в main одним коммитом.

## Required choices before any mutation

Use read-only probes to identify the exact remote, integration branch, current task branch, and associated PR. Then use the host's blocking question tool, or chat when none exists, to ask both questions before any fetch, commit, push, merge, PR mutation, or branch deletion:

1. After the associated PR is confirmed merged, should the exact remote task branch `<remote>/<TASK_BRANCH>` be deleted?
2. After all required checks and reviews pass, should the associated PR be squash-merged into remote `<main>`?

Record both answers. No, missing, or ambiguous means: keep the remote branch and do not merge the PR. These answers authorize only the named post-PR actions; they never authorize deleting a local branch.

## Fail-closed workflow

1. Confirm the requested remote and integration branch. Record the current task branch. Stop on detached HEAD or if the current branch is the integration branch.
2. Require a clean worktree. Commit valuable local changes to the task branch; do not hide them with `git stash`. If another agent/process is writing these files, stop and let that writer resolve them.
3. Before fetching, record the current `HEAD` as `<PRE_MERGE_SHA>` and `git merge-base <remote>/<main> HEAD` as `<MB_OLD>`. Keep the literal SHAs: the post-merge graph cannot reconstruct this test boundary with one command.
4. Run `git fetch <remote> --prune`. Update the local integration branch only with `git merge --ff-only <remote>/<main>`. If fast-forward fails, stop and report the divergent local branch; never repair it with reset. Return to the recorded task branch.
5. Inspect both ranges `<MB_OLD>..<remote>/<main>` and `<MB_OLD>..HEAD`, their file intersection, and `git merge-tree`. Use temporary files when command substitution or process substitution would hide evidence from an isolated shell.
6. Run `git merge --no-edit <remote>/<main>`. `Already up to date` is success with no merge needed. Before the merge commit exists, the safe exit is `git merge --abort`.
7. Resolve conflicts semantically: the result must retain both features. Never blanket-select `--ours`, `--theirs`, `-X ours`, or `-X theirs`. For each conflicted file, inspect both histories from `<MB_OLD>` and use diff3 context. Put edits into renamed destinations; adopt new signatures and update every caller; take generated/lock files from the canonical side and regenerate with the project tool. Treat schema, migration, security, regulatory, and unexplained foreign-code conflicts as stop conditions unless intent is provable.
8. Reread every resolved file before staging it. Search the whole worktree for conflict markers and search each required symbol/behavior in the resolved file. Also inspect silent conflicts Git cannot flag: shared version/cache/build identifiers and renamed APIs with old callers.
9. Test the union of both sides from `<MB_OLD>`, not only the task branch's old diff. Use the repository's diff-aware test selector with `<MB_OLD>` when available; run the full suite when shared foundations require it. Every overlapping code path needs a test that would fail for a broken resolution. Run the repository's lint, type, migration-head, generated-file, and documentation gates that apply. If a failure also exists on clean `<remote>/<main>`, verify it in a separate worktree, stop, and report the baseline failure.
10. Push only when explicitly requested. Do not force-push or pipe network commands. Verify publication by comparing local `HEAD` with the remote branch SHA; a successful command exit alone is not proof.

## Optional PR completion

Apply only the answers recorded before mutation.

- **Squash-merge associated PR into remote main:** immediately re-resolve the associated PR and verify its base is `<main>`, its head is the exact current task branch, its head SHA is unchanged, it is open and non-draft, and all required checks and reviews pass. On GitHub use `gh pr merge <PR> --squash --match-head-commit <HEAD_SHA>` without `--admin`, `--auto`, or `--delete-branch`. Verify the PR is `MERGED` and the reported merge commit is on the remote integration branch. Never follow a merged PR with a local `git merge --squash`; local `main` is not part of this operation.
- **Remote deletion:** only after the PR is confirmed `MERGED`, and only when the user answered yes. Re-verify the exact remote task ref exists and is neither the integration/default branch nor a protected branch, then delete only that remote ref. Verify the remote ref is gone and the local task ref still exists.
- **Local fallback:** never run `gh pr merge --delete-branch`, `git branch -d`, `git branch -D`, `git update-ref -d refs/heads/...`, or any equivalent cleanup of the local task branch. The local task branch is the fallback and only the user may delete it manually.

## Rollback and stopping

| State | Action |
|---|---|
| Merge not committed | `git merge --abort` |
| Merge committed, not published | With an explicitly confirmed clean worktree, restore `<PRE_MERGE_SHA>` only after user authorization for the destructive reset |
| Merge published | `git revert -m 1 <MERGE_SHA>` and publish the revert normally |
| Commit/branch appears lost | Recover from `git reflog` into a new recovery branch |

Stop and report facts when fast-forward fails, conflict intent is ambiguous, a protected domain is involved, tests fail on clean upstream, remote advancement rejects the push, or the same conflict recurs on every sync. A deadline never weakens these stops.

## Common mistakes

- Stashing valuable changes: commit them so three-way merge retains ancestry and `--abort` remains trustworthy.
- Testing only the old task diff: retain `<MB_OLD>` and test the combined change.
- Treating “no conflict markers” as proof: verify required symbols and silent conflict classes.
- Writing commit or PR text inline: when text contains shell-sensitive characters, write it to a file and use `git commit -F` or the hosting tool's body-file option.
- Using `gh pr merge --delete-branch`: it deletes both the local and remote branch, but local branch deletion is forbidden.
