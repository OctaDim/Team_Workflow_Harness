---
name: comm-commit-task-stages
description: Use when starting authorized repository work or reaching a task or stage boundary in a Git repository.
---

# Commit task boundaries

Required: read and apply `compound-engineering:ce-commit` before the first
boundary; use it for every commit.

1. Before a task set and each task, commit authorized pending changes.
2. After every completed stage, commit its owned changes.
3. At task/set completion, commit any remaining owned changes.

Take stages from the selected workflow or approved plan and preserve its gates.
The orchestrator owns canonical commits.

At boundaries with no owned changes, report “nothing to commit”; no empty or
duplicate commits. Before touching overlapping pre-existing changes, resolve
unclear ownership. Preserve unrelated staged files and `exclude:` paths through
ce-commit’s explicit file lists.

A missing Git/ce-commit or failed commit stops the boundary; preserve changes
and report the blocker.

Done: each boundary records hash/subject or a clean skip; owned changes are
committed. These local commits do not authorize push, PR, merge or history
rewriting, choose a route, or upgrade verification.
