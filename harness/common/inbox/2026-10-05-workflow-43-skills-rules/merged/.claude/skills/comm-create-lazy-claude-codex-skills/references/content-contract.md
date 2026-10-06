# Content contract

Use when authoring or reviewing skills/rules.

Express applicability, required action/restriction/invariant and observable compliance unambiguously. Always applicable within a scope suffices; clear skill metadata need not be repeated. Content matters; headings/count/order are optional, one sentence can suffice. Do not restate requirements.

Preserve relevant limits/approvals/stops/handling of insufficient data; no speculative unrelated constraints. Fix step order only for correctness. Every fragment improves decisions: short instructions, deferred details, examples/reasons preventing concrete errors. Compression preserves applicability/behavior/boundaries/resource access completely.

Necessary tools/resources remain available after installation; specify how/when to access. All links portable; no symlinks. Platform actions separately.

The old four sections are optional: infer violations, explaining separately only if ambiguous; keep history in inbox/lessons/reports; keep correction as required behavior in instructions; keep a short reason only when useful, detailed rationale separately.

## Skills

A folder with SKILL.md: YAML frontmatter with explicit nonempty name/description, then Markdown instructions.

- name: 1–64 characters inclusive; a-z, digits, hyphens; no leading/trailing/consecutive hyphens; matches folder. Shared prefixes: comm-/proj-.
- description: 1–1024 characters, capability plus precise activation conditions; algorithms/constraints in body.
- Minimal agent bundle: SKILL.md. Resources only as needed. Recommended names: references/ (guidance), scripts/ (executable actions), assets/ (output materials). SKILL.md defines use; these directories are optional.
- Optional agents/openai.yaml: UI name/description/icons, invocation policy, dependencies. Separate harness README.human.md requirements remain; never load its body.

## Rules

Markdown with applicability/behavior in body; no paths in this harness. Justify always-loaded placement by a requirement needed before skill selection. Claude Code reads only paths, ignores description/other frontmatter and removes frontmatter before loading context. Metadata alone cannot express scope. Check Codex loading separately.
