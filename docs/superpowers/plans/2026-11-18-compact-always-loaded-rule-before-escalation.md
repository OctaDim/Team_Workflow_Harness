# Rule budget compaction before escalation

**Execution:** The user approved the short Superpowers route and asked for a real compaction attempt before escalation when edits are authorized.

**Goal:** Try to bring an authorized candidate within the word and token budgets while retaining its behavior. Obtain a decision for a remaining overage or an unconfirmed equivalence.

**Architecture:** Update the existing rule budget resource in `comm-validate-harness-instructions`. The rule evaluator, verification statuses, and publication gate retain their responsibilities.

**Spec:** [INBOX request and acceptance criteria](../../../harness/common/inbox/2026-11-18-compact-always-loaded-rule-before-escalation/request.md).

## Task 1. Establish the baseline and candidate

- [x] Verify the existing stop order with actual Codex traces and exact stock plugin-eval measurements on the fixtures.
- [x] Reconcile the full candidate against the current lazy skill. Keep the word and token thresholds, early triggers, obligations, exceptions, and stop points.

## Task 2. Verify and report

- [x] Exercise each threshold alone, equality, authorized compaction, a remaining overage, failed behavior preservation, an amendment, an unauthorized edit, and unrelated work in both Codex installation modes.
- [x] Verify the candidate structure, budget, portability, and repository suite. Save actual edits, measurements, retention checks, and limits in the [candidate report](../../../harness/common/testing/evidence/2026-11-18-execute-compact-rule-before-escalation/2026-11-18-candidate-report.md).
- [x] Report the remaining verification gap and keep the request in progress.
- [x] Publish the authorized version and close the request. See the [publication report](../../../harness/common/testing/evidence/2026-11-18-publish-compact-rule-before-escalation/2026-11-18-publication.md).
