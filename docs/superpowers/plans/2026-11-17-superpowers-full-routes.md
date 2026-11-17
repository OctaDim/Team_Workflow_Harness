# Full Superpowers routes implementation plan

**Execution:** The user selected the short Superpowers route and approved its design. The primary agent prepares and checks the first INBOX result before starting the second request.

**Goal:** Bind both full menu choices to their native lifecycles while preserving harness controls and using each workflow's own storage.

**Architecture:** The existing menu and selector own choice and routing. A conditionally read resource covers the selected executor. The existing entrypoint rules own the narrow storage exception. The bootstrap refers to the canonical boundary when generating a new entrypoint.

**Tech stack:** Markdown instructions, Python startup checks, Codex and Claude Code, Superpowers 7.0.1.

**Spec:** [INBOX requirements and execution agreement](../../../harness/common/inbox/2026-11-17-superpowers-full-routes/request.md).

## Constraints

- Use the native paths and lifecycle for Superpowers artifacts. Continue to apply harness instructions, authorization, and evidence protections. Save harness artifacts in their existing categories. Create a harness handoff only on explicit user instruction.
- Keep both executors and existing menu choices. Keep the chosen executor on resume. Preserve actual RED/GREEN, review, and the finish decision.
- Work in the authorized candidate. Publish only with separate authorization. Preserve existing AGENTS.md and CLAUDE.md and the shared skeleton.

## Task 1. Capture baseline and prepare the candidate

- [x] Run the baseline in disposable common-only and combined roots. Test whether selection establishes the full workflow and whether harness gives a coherent answer for native Superpowers storage, resume and cleanup.
- [x] Prepare a new full candidate for `harness/common/skills/comm-select-development-workflow`, including its complete references and the agreed native storage procedure.
- [x] Prepare candidate versions of `harness/common/rules/comm-user-owned-entrypoints.md`, `harness/common/START.md`, and `harness/common/checks/ensure_entrypoint_links.py`. Keep the new entrypoint template consistent with the rule and preserve existing user files.

## Task 2. Verify and prepare the publication decision

- [x] In separate test installations, check startup twice, verify the pre-existing project and entrypoint bytes, and cover native plan identity, resume and output placement.
- [x] Check Codex behavior in both modes, including explicit and implicit selection, unrelated routes, review and recovery. Record the Claude status and the limits of the verification in the report.
- [x] Run skill-creator, plugin-eval, and affected startup tests on the final candidate. Record budgets, hashes, results and publication scope in permanent evidence.
- [x] Obtain separate authorization and publish the checked version. See the [publication report](../../../harness/common/testing/evidence/2026-11-18-publish-superpowers-full-routes/2026-11-18-publication.md).
