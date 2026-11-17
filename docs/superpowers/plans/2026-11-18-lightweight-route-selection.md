# Lightweight workflow selection implementation plan

**Execution:** The user approved the short Superpowers route and the list of work for this request.

**Goal:** Present the route menu before substantive work on a new independent task. Read the selected workflow after the user chooses it.

**Architecture:** The existing workflow rule owns the early decision. The existing selector and its menu own the choice and its application. Use committed version `2f1c86cc` as the source for the complete skill and carry forward its full Superpowers resource unchanged.

**Spec:** [INBOX request and acceptance criteria](../../../harness/common/inbox/2026-11-17-lightweight-route-selection/request.md).

## Task 1. Establish the baseline and integrate the candidate

- [x] Capture actual Codex reads and responses for new research, a short question, and a mixed request in isolated installations.
- [x] Extend the existing rule and skill to cover any new independent task and ambiguous scope. Use the menu and brief route descriptions before selection. Reuse the prior clear choice within the same task.
- [x] Check the complete candidate against the published sources and preserve both executors, their procedure, and the choice contract.

## Task 2. Verify and prepare publication

- [x] Verify native discovery and exercise both installation modes. Compare reads before choice, after choice, and on continuation. Record the exact menu discrepancy in the report.
- [x] Check skill structure, rule and skill budgets, portability, and the repository suite. Preserve actual results and limits in the [verification report](../../../harness/common/testing/evidence/2026-11-18-execute-lightweight-route-selection/2026-11-18-candidate-report.md).
- [x] Fix reproduction of the mandatory menu wording and rerun all 20 Codex scenarios on the corrected version. See the [retest report](../../../harness/common/testing/evidence/2026-11-18-lightweight-route-selection-verbatim-menu/2026-11-18-candidate-report.md).
- [x] Correct the Russian wording and check all other menu entries for the same error. See the [final verification report](../../../harness/common/testing/evidence/2026-11-18-lightweight-route-selection-menu-grammar/2026-11-18-candidate-report.md).
- [x] Obtain approval for the exact version and publish it. See the [publication report](../../../harness/common/testing/evidence/2026-11-18-publish-lightweight-route-selection/2026-11-18-publication.md).
