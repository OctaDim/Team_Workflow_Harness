# Placement

Shared sources: harness/common/skills/comm-name/, harness/project/skills/proj-name/;
rules: harness/common/rules/comm-name.md, harness/project/rules/proj-name.md.
Common is portable across projects; project material travels with its project contracts.

Native copies: full skill folders in .agents/skills and .claude/skills;
same-name ordinary rules directly in .claude/rules. Update source then copy; verify regular files, equal bytes/resources and all Git exclusions. No symlinks.

Personal skills: .agents/skills/name -> full .claude/skills/name; prefix optional.
Automatically .gitignore exact paths; preserve entries, never ignore whole native roots.
Ignoring tracked files does not erase history. Rule placement in octadim/ is revoked.

Rules share skills' gate ([validation](validation-and-publication.md)): complete rule file in dated inbox;
Confirmed explicit canonical instruction permits direct creation after gate.
Approved transfer automatically copies the canonical rule to .claude/rules in the same operation.
Codex reads recursively via AGENTS.md link/instruction; Claude loads natively.
Exclude README.human.md. Codex link is not a native import.

Canonical requirements outrank personal guidance; common/project conflicts need user decision,
not prefix precedence. Protected entrypoints: agreed bootstrap/link repair or approved inbox processing.
