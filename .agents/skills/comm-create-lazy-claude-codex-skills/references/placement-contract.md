# Placement

Full ordinary copies; no symlinks.

Shared skill: harness/{common/skills/comm-name,project/skills/proj-name} → identical same-name .agents/skills and .claude/skills folders.
Shared rule: harness/{common/rules/comm-name.md,project/rules/proj-name.md} → same-name file directly in .claude/rules; no Codex mirror.
Explicit personal skill: .agents/skills/name → .claude/skills/name.

Common required/portable; project depends on it. Personal prefixes optional; canonical requirements prevail; conflicts need user decision. Edit source; verify file types/sets/bytes/Git visibility. Shared source/copies visible; auto-ignore personal paths exactly, preserve entries, never roots; ignoring ≠ untracking.

Rules: octadim/personal scheme revoked; classify common/project by content. After gate source/copy together, no extra approval; stop on differing other-owner file. Claude loads natively; Codex reads recursively via AGENTS.md, not native import. Entrypoint check restores instruction, never publishes rules.


Check the **entire** canonical comm-/proj- rule set of installed packages, not
just changed files: no missing/extra shared copies, ordinary files at every path
component, equal bytes; ignore personal rules and README.human.md. An empty
canonical selection fails, not passes. Run the existing
`harness/common/testing/tests/test_rule_copies.py` via pytest: it exercises
missing/different/symlink/extra controls for both modes. Entrypoint link success
does not prove copy completeness; neither proves native agent loading.
Restore copies only through the current publication gate; an authorized exception
retains actual statuses. Keep the full skill folder resource set equal too.
