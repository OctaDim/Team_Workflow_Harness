# Always show both full Superpowers routes

**Execution:** The user selected the short Superpowers route, agreed to the
tasks and approved the design.

**Goal:** Present both full Superpowers routes whenever a route menu is shown.

**Architecture:** Apply the request's display change to the published
conditional menu resource. Retain the current selector and route procedures.

**Spec:** [INBOX request and acceptance criteria](../../../harness/common/inbox/2026-11-18-always-show-full-superpowers-routes/request.md).

## Task 1. Reproduce the omission and prepare the candidate

- [x] Capture the published menu for an unselected task where plain or short
  execution is recommended. Expect both full routes to be absent in at least
  one scenario per installation mode.
- [x] Rebase the recorded candidate on the published wording. Require both full
  routes in every menu. Keep the exact labels, review note, full-cycle
  description, short-route conditions and experiment approval.
- [x] Check the complete skill using quick_validate and plugin-eval. Compact
  the surrounding guidance to at most 1200 deferred tokens while preserving
  all required behavior.

## Task 2. Verify and report

- [x] In both installation modes exercise plain, short, Compound Engineering
  and full recommendations, the absence of a recommendation, and an INBOX
  task. Check exact labels, numbering, the full-cycle description, the review
  note, and the boundary before route selection.
- [x] Verify the experiment approval gate, direct plain execution, and selected
  short and full routes. Check native discovery, complete copy equality,
  startup and the affected suite.
- [x] Save the results and exact publication scope in permanent harness
  evidence. Record separate verification outcomes and leave publication
  subject to authorization.

## Result

Codex completed 25 of 30 scenarios successfully. Claude
and the overall result are unverified. Publication remains pending.
[Evidence](../../../harness/common/testing/evidence/2026-11-18-execute-always-show-full-superpowers-routes/2026-11-18-candidate-report.md).
