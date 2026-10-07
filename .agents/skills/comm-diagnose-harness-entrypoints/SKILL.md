---
name: comm-diagnose-harness-entrypoints
description: Use when diagnosing harness startup errors, entrypoint warnings, damaged startup links, imports or unsafe input paths.
---

# Diagnose the startup result

Collect target root, actual command/exit/output and input/history availability.
Before diagnosing read [entrypoints](references/entrypoints.md). Use the existing
common checker; it requires Python3.9+, not Git/hooks/machine registration.

1. Distinguish advisory settings differences from unsafe/missing resources or
   read/write errors. No history means comparison unverified, not unchanged.
2. Identify exact path/line/cause and the permitted remedy. Preserve extra CLAUDE
   text, valid existing startup commands and protected non-link settings.
3. Only the agreed checker may restore startup links, with notice before write;
   other changes need the authorized inbox route. Never auto-close damaged fences.
4. For narrow byte/EOL repair read from root
   `harness/common/skills/comm-preserve-text-line-endings/SKILL.md` before implementation.
   For two-mode installation changes select installation only at that stage.

Done: demonstrated cause, allowed next action and factual checks/limitations;
no false native/copy proof or direct protected edits. Error/unsafe path stops
unsafe dependent work; an advisory warning alone does not block the task.
