## Repository Research Summary

### Implementation Patterns

Scope: patterns. Planning only. The approved purpose-based split is workable within existing owners/categories; no new router, category, dependency, entrypoint edit, or template edit is necessary. Routing must run before skills-first selection, because an application decision/spec/report is not itself a request to improve an agent procedure.

#### Active instruction coverage: must change or explicitly scope

| Owner / evidence | Current effect and required planning reach |
|---|---|
| `harness/common/rules/comm-skill-rule-ownership.md:6–21` | Blanket prohibition and mandatory inbox skill for **any** harness write. Introduce early purpose distinction: all common and project mechanism use inbox; ordinary APP create/update uses existing project permanent categories. Keep separate confirmation for genuine mechanism bypass. |
| `harness/common/rules/comm-skill-rule-ownership.md:23–30` | Blanket evidence guard names both packages and all operations. Permit ordinary application project evidence create/update only; keep mechanism/common evidence guard and dependent-link/data preservation. |
| `harness/common/rules/comm-skill-rule-ownership.md:39–44` | “Save decision/memory” triggers future-behavior/skills-first and inbox before any memory record. Scope to reusable agent/harness behavior; application materials should choose their factual category directly. |
| `harness/common/skills/comm-process-harness-inbox/references/workflow.md:3–19` | Explicitly includes all reports/memory and says existing project changes need authorization. Replace blanket applicability, retain four permission stages and direct mechanism bypass order. Startup exception remains an exception to mechanism routing, not sole permission to save APP artifacts. |
| `harness/common/skills/comm-process-harness-inbox/SKILL.md:21–24` | Unqualified direct bypass question. Clarify that normal APP create/update is outside bypass; otherwise an explicit skill call can restore obsolete questioning. SKILL description lines 2–3 may clarify request scope without expanding metadata. |
| `harness/common/skills/comm-preserve-harness-knowledge/SKILL.md:8–20` | Future-behavior choice precedes material classification; “Before any write” always loads inbox. Classify APP versus mechanism/common first, then future-behavior owner for the latter. |
| `harness/common/skills/comm-preserve-harness-knowledge/references/experience-routing.md:3–20` | Shared category map is already useful (decisions/results/specs/research/plans/handoffs). Explicitly separate APP output from reusable agent procedure; path alone must not promote a hidden mechanism document to APP. |
| `harness/common/skills/comm-preserve-harness-knowledge/references/material-placement.md:3–7,23–27` | Categories/dates and migration guard already work. Clarify APP normal placement vs mechanism migration if needed; preserve unknown dates, dependent links, no mass conversion, no shared-template scope expansion. |
| `harness/common/skills/comm-protect-harness-evidence/SKILL.md:8–34` | Most direct counterexample: forbids all project evidence creation and requires a new question after “save result” or authorized tool/test. Scope by purpose and ordinary APP create/update; retain destructive-operation safety (`:36–40`) and truth of verification. |
| `harness/common/INDEX.md:22–28` | Global skills-first and “any harness change” point back to blanket owner. Both need aligned compact wording. |
| `harness/project/INDEX.md:22–26` | Skills-first for all saved experience; needs APP/material routing pointer. Preserve RAG continuation links and no per-file map growth. |
| `harness/common/decisions/2026-10-05-inbox-execution-status.md:11–16` | Formal accepted invariant describes all direct routing as named bypass with confirmation. Add dated superseding scope/decision pointer; do not leave this as current APP requirement. Historical reason/status invariants remain factual. |

#### Formal contracts and historic sources

- `harness/common/specs/2026-10-06-structure-and-creation-dates.md:13–20` already distinguishes categories and prohibits documents from becoming independent agent-procedure owners; augment purpose boundary only if needed, retain category/date semantics (`:22–38`). No root-category change required.
- `harness/common/docs/2026-10-05-skill-rule-ownership-contract.md:18–23` defers working behavior to rules/skills; pointer to new accepted boundary suffices, no duplicate algorithm.
- `harness/common/decisions/2026-10-05-harness-architecture.md:3–6,20–21` and `harness/common/decisions/2026-10-05-skill-rule-ownership.md:3–6,16` contain dated old inbox/experience statements with explicit historical disclaimers. Preserve old statements; add current boundary/decision reference rather than rewrite their historical meaning.
- `harness/common/decisions/2026-10-07-skills-first-knowledge.md:9–14,20–26` applies reusable instructions and experience ownership; distinguish APP artifacts without reversing removal of lessons or changing verification statuses.
- `harness/common/START.md:3–7,13–15` loads ownership rule and identifies lazy details; `harness/project/START.md:3–11` only startup/install route. Neither states blanket APP inbox; no compulsory body change.
- `harness/common/checks/ensure_entrypoint_links.py:10–28,147–159` generates protected entrypoint warning and neutral project map/start. Generated texts do not impose APP blanket routing. No checker/template change needed; avoid requiring separate all-project template authorization.
- `harness/common/skills/comm-create-lazy-claude-codex-skills/SKILL.md:16–17`, `comm-publish-harness-instructions/references/gate.md:4–18`, `comm-validate-harness-instructions/SKILL.md:25–28` concern instruction authorship/validation/publication, so their inbox language correctly remains mechanism-scoped. `comm-normalize-text-line-endings/SKILL.md:9–10` refers to protected harness files: optional purpose clarity, not a new APP permission gate. Entrypoint diagnosis remains mechanism-only.

#### Native copies and existing tests

- `.claude/rules/comm-skill-rule-ownership.md` is byte-identical to canonical rule on this read-only inspection. Changed rule must be published there.
- Full machine files/resources for `comm-process-harness-inbox`, `comm-preserve-harness-knowledge`, `comm-protect-harness-evidence` are byte-identical in both `.agents/skills/<name>/` and `.claude/skills/<name>/`. Preserve complete ordinary copies, not symlinks; changed resources reach both natives. Existing map includes 3 knowledge resources and 1 workflow resource.
- `harness/common/testing/tests/test_skills_first_knowledge.py:9–32` requires canonical/native full file sets and bytes, no symlinks, valid links, no lessons pointers. `:35–49` requires current maps/template categories. Reuse these integrity checks after publication; do not treat them as native behavior proof.
- `harness/common/testing/tests/test_rule_copies.py` covers rule source/native inventory and bytes; portability/startup tests `test_entrypoint_portability.py`, `test_ensure_entrypoint_links.py` cover common-only/combined/protected inputs and preservation. Their inbox assertions are protected-entrypoint notifications, not APP blanket-inbox checks; no caller break expected.
- Existing relevant behavioral probe: `harness/common/inbox/2026-10-07-harness-direct-change-confirmation/run_codex_checks.py:18–23,43–49,58–96`. It tests a **common/docs** direct bypass, which must still ask/wait under the approved new split. It creates temporary installs in both modes and checks before-skill rule reads. Do not rewrite this old experiment or reuse its fixed evidence paths for new results; a current small probe can follow its fixture approach and preserve historic results.
- No active permanent test currently asserts APP direct-create/update vs mechanism/common stop behavior. New behavioral matrix should cover APP decision/spec/plan/handoff/evidence, mechanism control file disguised in docs/project evidence, common material, mixed request, truthful idea/accepted and planned/performed statuses; paired agents and installation modes. Existing structural checks alone cannot establish compliance.

#### Scope and risks for implementation

Ordinary APP create/update approval does not imply deletion/cleanup, bulk migration, template modification, native instruction publication, or elevating tentative ideas/tests to accepted/passed. A document containing instructions that control future agent behavior is mechanism regardless of category; an app interface/data specification can set application contracts without becoming an agent procedure. Existing project APP inbox records stay historical; no bulk cleanup or retrofit is needed. All common changes in this task remain under this authorized common inbox execution and publication gate. Current separate Codex/Claude/mode verification statuses must reset for changed instructions.

No tests or native probes run during research. Only mandatory startup check and read-only source/copy inspection were performed; no live harness/native files changed. The settled split has no discovered feasibility blocker, but purpose classification requires native behavioral verification.
