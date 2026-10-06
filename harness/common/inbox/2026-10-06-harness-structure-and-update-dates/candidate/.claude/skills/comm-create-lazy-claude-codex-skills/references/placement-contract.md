# Placement

Full ordinary copies; no symlinks.

Shared skill: harness/{common/skills/comm-name,project/skills/proj-name} → identical same-name .agents/skills and .claude/skills folders.
Shared rule: harness/{common/rules/comm-name.md,project/rules/proj-name.md} → same-name file directly in .claude/rules; no Codex mirror.
Explicit personal skill: .agents/skills/name → .claude/skills/name.

Common required/portable; project depends on it. Personal prefixes optional; canonical requirements prevail; conflicts need user decision. Edit source; verify file types/sets/bytes/Git visibility. Shared source/copies visible; auto-ignore personal paths exactly, preserve entries, never roots; ignoring ≠ untracking.

Rules: octadim/personal scheme revoked; classify common/project by content. After gate source/copy together, no extra approval; stop on differing other-owner file. Claude loads natively; Codex reads recursively via AGENTS.md, not native import. Entrypoint check restores instruction, never publishes rules.
