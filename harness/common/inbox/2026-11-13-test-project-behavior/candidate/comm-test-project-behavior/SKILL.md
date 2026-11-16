---
name: comm-test-project-behavior
description: Use when adding, fixing or changing application code/files; excludes harness mechanisms.
---

# Test behavior

Inputs: contract, scope, revision/environment, checks.

1. Identify each change's contract/regression risk; size grants no exemption.
   Reuse sufficient tests; add/adapt gaps. For test design use
   `comm-assess-project-tests`.
2. New code, new/changed behavior and defects require TDD: behavioral RED,
   minimal GREEN implementation, refactor with passing checks. Syntax/import/
   environment failures do not establish RED.
3. New functions require unit and integration tests: contract, neighboring
   behavior, boundaries and errors.
4. Behavior-preserving refactors need no artificial RED. Text-only changes need
   link/syntax/rendering checks; add programmatic tests for significant gaps.
   Treat condition/permission/dependency/format/startup edits as behavior changes.
5. Missing infrastructure: create within scope or record an explicit prerequisite;
   never omit testing. Missing authority blocks dependent work.
6. Before finishing run the entire relevant set and assess coverage using
   `comm-run-project-checks`.

Done: evidence supports the contract; disclose gaps. Harness procedures stay separate.
