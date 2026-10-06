# Placement contract

| Material | Source | Native files | Git |
|---|---|---|---|
| Shared skill | harness/common/skills/comm-name or harness/project/skills/proj-name | complete same-name direct child of .agents/skills and .claude/skills | source/copies visible |
| Shared rule | harness/common/rules/comm-name.md or harness/project/rules/proj-name.md | ordinary copy in .claude/rules/octadim/ | source/copy visible |
| Explicit personal skill | .agents/skills/name | complete copy in .claude/skills/name | exact paths automatically .gitignored |

Personal names may lack prefixes.
Common knowledge is portable; project knowledge depends on that project's contracts.
Canonical requirements always outrank personal skip/override instructions. Common/project
conflicts require a user decision, not prefix precedence; this is behavior, not host security.

No symlinks. Edit the shared source once and copy whole folders/resources; edit personal
skills in .agents and overwrite .claude. Verify regular files and equal bytes/file sets.
Preserve existing .gitignore; never ignore whole native roots. Check actual Git visibility,
including global/local exclusions. Ignoring a tracked file does not remove history.

Do not edit AGENTS.md/CLAUDE.md directly or store dynamic state there. Agreed bootstrap/link-repair exceptions do not authorize skill-authoring edits.
