---
name: comm-run-project-checks
description: Use when running/selecting application checks; excludes harness validation.
---

# Run application checks

Inputs: contracts, revision/environment, authority.

1. Use the project runner/configuration. Include affected callers, fixtures and dependencies.
   Confirm collection; empty/passing narrow sets do not prove coverage.
2. Explicit full-suite requests authorize execution without reconfirmation.
   Otherwise select sufficient checks; explain/agree a necessary full run.
   Preserve mandatory checks and project/access limits; this grants no harness authority.
3. Run the entire relevant set, including existing tests, on a stable revision;
   avoid shared-tree writers/mutations. Check live runs before restarting.
   Collection/dry-run is not execution.
4. Retain completion, exit status and results. Truncated output, wrapper
   success or isolated summary strings are insufficient.
5. Classify behavior/test, collection/import, environment and instability failures.
   When necessary, compare identical failing cases on an isolated baseline.
   Do not change code, dependencies or system settings merely for green.

Done: report commands/revision/environment, executed scope/results, skips and
unrun/uncovered cases with reasons. Assess coverage; passing proves observed
cases only. Evidence retains its owner.
