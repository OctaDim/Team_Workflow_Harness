---
name: comm-protect-harness-evidence
description: Use when saving or changing harness evidence, distinguishing application results from protected mechanism evidence and parent operations.
---

# Preserve evidence by purpose and operation

Before classifying any evidence operation read [operations](references/operations.md)
and from root `harness/common/skills/comm-process-harness-inbox/SKILL.md` plus its
`references/workflow.md` for the authorized route. Reading within project access is allowed.

Application/task evidence belongs in `harness/project/testing/evidence/work/`;
project mechanism evidence in `harness/project/testing/evidence/harness/`;
portable common evidence stays `harness/common/testing/evidence/`.
Existing evidence keeps paths until an addressed migration. Purpose, not
folder/name, governs; mechanism in work remains protected. Inspect all contents
before parent operations; mixed mechanism stays protected, unknown purpose/state
requires clarification before mutation. Explicit invocation changes no boundary.

Apply operations to new/current/completed reports and raw runs; record actual
written or blocked files and preserve statuses. Completion: permitted results
saved, original raw/completed evidence preserved, provenance/dates/links intact.
No automatic migration or technical filesystem enforcement.
