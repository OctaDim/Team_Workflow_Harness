---
name: comm-assess-project-tests
description: Use when designing/reviewing application tests or investigating misleading results; excludes harness validation.
---

# Assess application tests

Inputs: contract, implementation/tests, authority.

1. Assert behavior/forbidden side effects, not merely no exception or matching
   names/comments. Derive expectations from contracts, not implementation.
2. Confirm meaningful inputs and intended branches execute. Cover positive,
   neighboring, boundary/error cases; disclose gaps.
3. Reuse suitable fixtures/factories. Mock external boundaries, not all tested
   logic; preserve relevant failure/timing semantics and affect the actual callee.
4. Check sensitivity: removing protection without changing results means the test
   does not protect it. Before controlled mutations read
   [isolated checks](references/isolated-mutations.md). Preserve authority;
   insufficient evidence requires proposed additional checks.
5. Never hide unfinished work through skip, xfail or disabled assertions.
   An allowable exception needs justification, a tracked task and deadline;
   disclose its coverage gap. Changing checks requires authority.

Done: report protected behavior, evidence, false-result risks and needed changes.
Harness validation/evidence retain their owners.
