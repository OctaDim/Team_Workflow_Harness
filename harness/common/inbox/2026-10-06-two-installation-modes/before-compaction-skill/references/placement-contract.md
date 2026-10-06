# Placement

Read when saving/installing; complete ordinary copies, no symlinks.

| Material | Source | Native copies |
|---|---|---|
| Shared skill | harness/common/skills/comm-name or harness/project/skills/proj-name | identical complete same-name folders in .agents/skills and .claude/skills |
| Shared rule | harness/common/rules/comm-name.md or harness/project/rules/proj-name.md | one ordinary same-name file directly in .claude/rules/; no Codex mirror |
| Explicit personal skill | .agents/skills/name | complete copy in .claude/skills/name |

Common is portable, project dependent. Personal names may omit prefixes; canonical requirements prevail; common/project conflicts need user decision.

Edit shared source or personal .agents once. Check regular files/equal sets/bytes/Git visibility. Shared source/copies visible; personal exact paths automatically .gitignored. Preserve entries; never ignore whole native roots. Ignoring does not untrack.

Rules: the former octadim/personal scheme is revoked. Classify common/project by content; after authorized gate save source and copy together, no extra copy approval. Stop on a differing other-owner file. Claude loads rules natively; Codex reads recursively by AGENTS.md instruction, not a native import. The entrypoint check restores that instruction, never publishes rules.
