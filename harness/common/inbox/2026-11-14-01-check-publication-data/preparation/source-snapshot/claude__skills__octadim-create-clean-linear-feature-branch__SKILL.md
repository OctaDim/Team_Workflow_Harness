---
name: octadim-create-clean-linear-feature-branch
description: >-
  Use when asked to create or start a new feature, task, or work branch tied to Linear, especially when the current branch is another unfinished feature or prototype.
---

# Create a Clean Linear Feature Branch

Create every feature branch from freshly fetched remote `main`, never from the current branch.

## Required user confirmation first

Before any Git command, use the host's blocking question tool, or chat when unavailable, to obtain:

1. The feature to implement: a short statement of its intended outcome.
2. The Linear task: its identifier, such as `TE-337`.

Even when supplied, confirm both. Never infer or postpone the Linear identifier.

## Trigger vocabulary / Синонимы

- English: create/start/open a feature branch, new task/work branch, branch from main, start Linear issue, prepare a clean branch.
- Русский: создай/сделай новую ветку, начни фичу, ветка под задачу Linear, рабочая ветка от main, чистая ветка под фичу, ответвись под задачу.

## Branch contract

- Format: `octadim/<linear-id-lowercase>-<english-feature-slug>`.
- Translate the feature into concise lowercase ASCII English kebab-case, preferably two to five words.
- Example: Linear `TE-337`, “расписание водителей” → `octadim/te-337-drivers-schedule`.
- Validate with `git check-ref-format --branch`. On a local or remote collision, stop; never invent a suffix.

## Fail-closed workflow

1. Confirm the repository and require a clean worktree. Do not stash, commit, or move unrelated changes.
2. Resolve the remote owning `main`; use `origin` when configured. Fetch `main` and require its remote-tracking ref.
3. Verify the proposed branch is absent from both local and fetched remote refs.
4. Create and switch directly from remote `main`, without checking out local `main` or using the previous `HEAD`:

   ```bash
   git switch --no-track -c octadim/te-337-drivers-schedule origin/main
   ```

5. Verify the branch name and that `HEAD` equals fetched remote `main`. Report its name, feature, Linear issue, and source SHA.

Create only the local branch. Commit, push, and PR creation require separate explicit requests.

## Isolation rule

Useful code elsewhere never changes the start point. Do not branch from, merge, or wholesale cherry-pick an unfinished branch. If explicitly needed, first create the clean branch; then inspect the other branch and port only required code under the implementation task.

Deadlines, sunk work, authority, and reversibility do not relax these requirements. If the host prevents switching, stop with the proposed name and source SHA; do not claim creation.

## Common mistakes

- “Linear can be added before PR”: the identifier is required before naming or creating the branch.
- `git switch -c <name>` from the current feature: this inherits every unfinished ancestor change.
- Updating local `main` first: unnecessary; create directly from the fetched remote-tracking `main`.
- Copying a dependency branch wholesale: it destroys feature isolation and contaminates the future PR.
