---
name: comm-install-harness
description: Use when installing, moving or diagnosing harness packages or entrypoints, or changing the shared project skeleton.
---

# Install or migrate harness

Before changing an installation read [checks](references/checks.md): the two
supported modes, preservation, isolation and shared-template approvals.
Common is mandatory; never replace an existing project with an empty skeleton.

For entrypoint diagnosis read `harness/common/docs/2026-10-05-protected-entrypoints.md`
from the target project root. A chat cwd does not establish the destination.
Do not edit protected entrypoints or rewrite an existing startup command.

For material placement read `harness/common/specs/2026-10-06-structure-and-creation-dates.md`.
Skill/rule changes and native installation also require
`harness/common/skills/comm-create-lazy-claude-codex-skills/SKILL.md` before action.
Do not treat copy equality as native behavior verification.

Example: common-only creates a missing neutral project; common+project preserves
its working files. Test both without access to the source or global author skills.
