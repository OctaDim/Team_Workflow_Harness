---
title: "fix: Explain distinct SQL migration alternatives"
date: 2026-10-19
artifact_contract: ce-unified-plan/v1
product_contract_source: harness-inbox
execution: code
origin: harness/common/inbox/2026-10-19-sql-alternative-distinctness/request.md
---

## Goal Capsule

Make the existing SQL lazy skill compare distinct, justified mechanisms before requesting architecture approval. Amend its own resource; preserve scoped decisions and stop before dependent writes. Request scope and canonical harness contracts govern; publication of a new unverified version remains a separate gate.

## Product Contract

### Summary

The published skill loads in time but can present a version marker as a third migration mechanism. Clarify the comparison and require a check before asking for agreement.

### Problem Frame

An observed common+project reply read choices.md and then listed explicit SQL, SQLAlchemy/Alembic and PRAGMA user_version without explaining a distinct third mechanism. Mechanical checks passed despite this semantic defect.

### Requirements

- R1. Preserve all existing SQL decisions, three independent blocks, scoped approvals, delegated details and read-only/recording/access boundaries.
- R2. Each schema alternative identifies mechanism, migration executor and project fit; names, numbering and file placement alone do not establish difference.
- R3. Check distinctness before asking; replace duplicates or explicitly explain the absence of a suitable third option and ask for a decision. Never silently waive comparison or invent tools.
- R4. Preserve the observed negative example without banning legitimate user_version use or prescribing one migration tool.
- R5. Run all six requested scenarios in both installation modes three times, sequentially. Evaluate complete replies and actual writes, not only mechanical signals.
- R6. Preserve all attempts and old evidence; report actual agent/mode outcomes, version, budgets and limitations. Publish only an authorized exact version.

### Scope Boundaries

Only comm-confirm-database-design and this request's candidates/evidence are active. No new rule/router, application/project/entrypoint/configuration/commit-skill changes, delegation, parallel execution, commits, push or PR. Existing unrelated work stays intact.

## Planning Contract

### Key Technical Decisions

- KTD1. Keep lazy-only and current metadata: the observed failure occurs after successful skill/resource reads. Rule-only lacks the procedure; restoring rule+skill has no evidenced preventive effect on this failure.
- KTD2. Amend references/choices.md only, starting from the full request snapshot. Compare mechanism and owner explicitly while retaining the complete old obligations and examples.
- KTD3. Reuse the existing isolated native fixture via a new request-specific adapter, preserving identical six task prompts. Capture the current-version baseline before authoring, add semantic negative/positive probes, then freeze one candidate for all 36 runs. This is a local pattern application; external research adds no needed product or implementation decision.
- KTD4. Author and review inline under the request's no-delegation constraint. Parent review is not independent review. The harness owns final validation and publication; CE supplies planning/execution. Plan/evidence placement follows canonical common ownership rather than the plugin default docs root.

## Implementation Units

### U1. Characterize the failed comparison

**Goal:** Verify the recorded defect and inspect the current behavior without editing the instruction.
**Requirements:** R2, R4, R6.
**Dependencies:** None.
**Files:** request source-snapshot.json; previous published-v1-codex-published-both-plan.json; new testing/evidence/2026-10-19-sql-alternative-distinctness/validate.py and baseline receipts.
**Approach:** Check exact hashes and trace reads to the bad reply; run an unchanged native baseline and a comparison-review probe. Retain both successful and failed attempts.
**Patterns to follow:** testing/evidence/2026-10-19-sequential-rule-to-lazy-skills/stage2-sql/validate_sql.py.
**Test scenarios:** The known three-item schema list must be rejected as unjustified; valid independent mechanisms must remain acceptable.
**Verification:** A saved current-version receipt and an explicit, bounded cause analysis precede the candidate.

### U2. Clarify and freeze the resource

**Goal:** Produce a minimal complete candidate for the demonstrated gap.
**Requirements:** R1–R4.
**Dependencies:** U1.
**Files:** inbox/2026-10-19-sql-alternative-distinctness/candidate-v1/comm-confirm-database-design/references/choices.md and the complete copied skill folder; evidence contract map and manifest.
**Approach:** Add schema mechanism/executor/fit and pre-question self-check; preserve metadata and every earlier obligation. Review alternatives against actual fixture code.
**Test scenarios:** Reject relabeled raw SQL; accept a genuinely distinct justified mechanism even if it uses a version marker; retain approvals and stop on open choices.
**Verification:** Full folder manifest, byte-preserved SKILL.md and mapped existing requirements; no publication yet.

### U3. Validate and prepare publication

**Goal:** Establish actual behavior and a reviewable exact version.
**Requirements:** R5, R6.
**Dependencies:** U2.
**Files:** new request-specific evidence receipts/reports, full candidate and publication manifest; current request Execution.
**Approach:** Run final profile/budget/content checks, two clean installations and negative checks, then the prescribed repeated native matrix. Inspect replies and files after each bounded group. Any content edit starts final-version checks anew.
**Test scenarios:** Implicit plan, explicit call, urgency/autonomous code request, complete approvals, partial approvals and unrelated task; each common-only/common+project repeated three times. Only the approved case writes PLAN.md; no case changes storage.py or protected inputs.
**Verification:** All 36 outcomes retained and semantically reviewed; installation equality/repeated startup/project preservation, applicable existing regression and token measurements recorded separately. Failed or unavailable checks retain unverified status.

## Verification Contract

Use the existing native Codex CLI with its default model/effort inside the established bwrap-isolated temporary fixtures. Three repetitions are coverage, not statistical proof. Run applicable quick_validate, plugin-eval start/analyze plus improvement brief/compare, full content review, human exclusion and both-mode installation checks. Record code-test results separately from native instruction behavior. Preserve raw events, commands, complete responses, real PLAN contents, usage and source hashes. Record separate agent/mode outcomes and actual skipped checks without raising their status. New-version publication requires its own exact-scope gate.

## Definition of Done

Candidate and permanent report identify the full version and preserved contract. The final 36-run matrix and additional checks have actual outcomes; no defect is hidden behind mechanical pass. Required publication is either authorized and checked or explicitly pending; a prepared candidate alone does not close the request. Old raw evidence and completed reports remain byte-identical.
