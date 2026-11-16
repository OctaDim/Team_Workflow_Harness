---
name: comm-commit-task-stages
description: Use when deciding when to commit repository work, including ideation, brainstorming, planning, implementation, verification, fixes and documentation.
---

# Commit completed results

Use `compound-engineering:ce-commit` for every local commit.

Commit a completed task or substantive substage with an independently useful,
verified result. A workflow label, user answer, question, dialogue turn, small
edit or passing check alone is not a boundary. Task/set entry is not a trigger.

Accumulate related small changes until their result is complete. Update
documents, decisions and harness memory promptly without committing every save.
A short task usually needs one final commit; long work may preserve independent
completed results separately. Set no question/file/line/time thresholds.

Exceptions: an explicit user command to commit now, or a justified checkpoint
before a risky operation. Explain the command or concrete risk. Preserve workflow
gates, isolation and recovery; group related steps before dispatch, never bypass
a safety transaction.

Before committing, run change-appropriate checks and inspect current ownership.
The orchestrator commits only authorized owned changes through explicit file
lists; preserve unrelated work and `exclude:` paths. No empty/duplicate commits.
Missing Git/ce-commit or failed checks/commit: preserve changes, report the blocker.

Done: completed owned results have hash/subject, or a clean skip. Commits grant
no push, PR, merge, history rewriting, route choice or verification upgrade.
