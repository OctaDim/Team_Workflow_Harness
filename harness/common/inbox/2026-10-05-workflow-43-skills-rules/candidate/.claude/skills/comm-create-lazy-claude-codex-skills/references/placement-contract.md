# Placement

Read when saving/installing; complete ordinary copies, no symlinks.

| Material | Source | Native copies |
|---|---|---|
| Shared skill | harness/common/skills/comm-name or harness/project/skills/proj-name | identical complete same-name folders in .agents/skills and .claude/skills |
| Shared rule | harness/common/rules/comm-name.md or harness/project/rules/proj-name.md | one ordinary file under .claude/rules/ (current subfolder octadim/); no Codex mirror |
| Explicit personal skill | .agents/skills/name | complete copy in .claude/skills/name |

Common is portable, project dependent. Personal names may omit prefixes; canonical requirements prevail; common/project conflicts need user decision.

Edit shared source or personal .agents once. Check regular files/equal sets/bytes/Git visibility. Shared source/copies visible; personal exact paths automatically .gitignored. Preserve entries; never ignore whole native roots. Ignoring does not untrack.
