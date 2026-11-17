# INBOX publication readiness implementation plan

**Execution:** The user chose the short Superpowers route and approved a change to the existing lazy skill if it fits the current limits.

**Goal:** Report incomplete verification and wait for a decision. Offer ordinary publication after the mandatory scenarios for the exact version pass.

**Architecture:** Add the reporting decision to `comm-process-harness-inbox`. The existing publication gate retains ownership of exceptions, transfer scope, and verification status.

**Spec:** [INBOX request and acceptance criteria](../../../harness/common/inbox/2026-11-18-publication-readiness-after-scenarios/request.md).

## Task 1. Prepare the candidate

- [x] Capture the baseline behavior for failed, missing, and complete scenario results in Codex.
- [x] Extend the existing skill entry to cover readiness reports and implement the decision before any publication offer. Preserve its current resource and the canonical rule set.

## Task 2. Verify the exact version

- [x] Exercise implicit and explicit selection, resume, incomplete checks, a corrected version, a complete version, and an explicit publication exception in both Codex installation modes.
- [x] Verify the skill structure, budgets, and repository suite. Save the actual results and verification limits in the [candidate report](../../../harness/common/testing/evidence/2026-11-18-execute-publication-readiness-after-scenarios/2026-11-18-candidate-report.md).
- [x] Report the remaining Claude verification gap and leave the request in progress.
- [x] Publish the authorized version and close the request. See the [publication report](../../../harness/common/testing/evidence/2026-11-18-publish-publication-readiness-after-scenarios/2026-11-18-publication.md).
