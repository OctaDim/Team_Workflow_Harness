---
name: comm-verify-browser-ui
description: Use when verifying application UI behavior or assessing browser-specific test fidelity; excludes harness validation.
---

# Verify browser behavior

Inputs: contract/reference, target, supported conditions, scenario and authority.
General test quality/TDD/check execution retain their existing owners.

1. Use a real browser for contracts depending on rendering, events, visibility,
   interaction, scrolling or responsiveness. Suitable lightweight tests can verify
   pure logic, not establish browser-dependent claims.
2. Establish needed conditions through comm-prepare-browser-check when unverified;
   reuse valid existing setup. Before choosing coverage read
   [browser coverage](references/coverage.md); before designing/reviewing relevant
   scenarios read [fidelity cases](references/fidelity.md).
3. Exercise the intended user path and assert its observable contract. Apply
   comm-assess-project-tests for general quality and comm-run-project-checks for
   general scope/execution; do not substitute passing narrow tests for coverage.
4. Compare appearance against approved intent through comm-preserve-visual-design.
   Tool choice remains with comm-choose-effective-solution; no fixed vendor or
   assumed installation.

Done: report actual contract evidence, environment/coverage and unverified cases.
Keep harness validation separate and use existing recording/evidence procedures.
