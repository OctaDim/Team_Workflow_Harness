---
name: comm-install-harness
description: Use when installing, moving or diagnosing harness packages or entrypoints, placing harness materials, or changing the shared project skeleton.
---

# Install or migrate harness

Before an installation change read [checks](references/checks.md): two modes,
existing-project preservation, isolation and shared-template approvals.
Common is mandatory. Identify the destination; chat cwd does not establish it.

For entrypoint diagnosis read [entrypoints](references/entrypoints.md).
For byte/CRLF damage during narrow text repair use from the project root
`harness/common/skills/comm-preserve-text-line-endings/SKILL.md`.
Do not directly edit protected entrypoints or rewrite an existing startup command.

Before material placement/date migration read [placement](references/material-placement.md).
For running/installing the harness suite read [testing](references/testing.md).
Only open resources for the current action. Skill/rule authoring and native
installation require `harness/common/skills/comm-create-lazy-claude-codex-skills/SKILL.md`
from the target root. Copy equality does not prove native agent behavior.
