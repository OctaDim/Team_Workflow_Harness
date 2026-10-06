# Validation and publication

## Request packet

Each request: own `inbox/YYYY-MM-DD-purpose/` in the selected packet; creation date,
meaningful name (e.g. `2026-12-31-create-some-skill`), meaningful suffix on collision.

Required request context, for **every** request:
1. When the need arose: date, development stage or triggering event, distinct from filing date.
2. Circumstances: task, actions, environment and material constraints.
3. Why it became necessary: error, repeated action, conflict or unmet need.
4. What execution will solve: problem removed and expected benefit.
5. Required result: specific behavior/artifact and its acceptance criterion.

Mark unknowns explicitly and ask for missing information; never invent dates or causes.
Unknown fields do not prove completeness.

Without explicit instruction to create in harness/common/skills or harness/project/skills,
save request.md, validation.md and **the full skill/resources** in `skill/name/SKILL.md`.
A description/private-copy link is insufficient. Save on the user's explicit request;
otherwise propose capture and obtain confirmation. No secrets or session transcript.
Each new harness folder has human-only README.human.md with explanation/example.
Exclude its body from search, context, imports and machine evaluation.

## Required tools in every project

Use skill-creator and its validator; superpowers:writing-skills RED–GREEN–REFACTOR;
plugin-eval:plugin-eval and plugin-eval:evaluate-skill. Review findings and next-step recommendations; resolve correctness/discovery/behavior findings.
Use plugin-eval:evaluate-plugin for an actual plugin manifest only; otherwise record N/A.
Use plugin-management:plugin-management when an integration/installation is needed.

Actually invoke tools locally; no author-home, EPL or sibling-packet dependency. If missing, warn with the tool name and offer
installation; obtain installation authorization before changing the environment.
After installation run checks. Failed/unperformed checks leave an **unverified** inbox
candidate and warning; draft capture works without the tools.

## Repeat gate and report

Process inbox in a separate user-requested session. Choose necessity, common/project,
final name and compression, then rerun applicable validation of final body/resources.
Check frontmatter, local resources, real helper behavior, RED–GREEN–REFACTOR and evaluation.
Separately test native listing, explicit own-resource use and implicit selection; record
agent versions/scope. File equality is not native proof.

validation.md: status, separate Codex/Claude checked/not-checked marks, version/files, date, tools, commands, results
(passed/failed/not run/N/A + reason), findings, missing tools, next steps.
**Verified** requires every applicable mandatory check passed for current body/resources
and no unresolved correctness/discovery/behavior findings. Edits invalidate the mark.
Static token estimates are not live session usage.

Missing/failed repeat checks: retain inbox; request explicit permission for **this unverified
version** at named canonical/native paths. A transfer request, old green, deadline or manual
example is not a waiver. Do not move first.
A permitted exception preserves the unverified mark and all remaining constraints.

After gate/exception: canonical source, full native copies, file/resource/equality/Git checks,
then native checks in the claimed scope. New failures remain unverified; further publication
needs a current gate or exception. Current report goes in the packet's checks; inbox retains
its earlier-version evidence.
