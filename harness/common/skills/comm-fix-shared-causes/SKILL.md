---
name: comm-fix-shared-causes
description: Use when correcting a defect or shared factual error whose cause may affect multiple callers, consumers or current documents.
---

# Correct the shared cause

Inputs: symptom, intended contract, revision/environment and authorized scope.

1. Reproduce or inspect the failure and trace evidence to cause.
   Separate confirmed causes from hypotheses. If intent or causality is unresolved,
   clarify it before making changes.
2. Find the responsible owner and all relevant callers, consumers, tests,
   configuration and current documents stating the same contract. Identify repeated
   causal mistakes beyond the reported location.
3. Correct the cause once in the shared owner where appropriate. Reuse existing
   mechanisms; preserve validation, error handling, security, accessibility and
   unaffected behavior. Avoid unrelated features or cleanup.
4. Update affected sites within authority, or report each remaining inconsistency
   and required decision. Use existing harness/evidence routes for protected or
   historical material; do not rewrite raw evidence or silently alter contracts.
5. Verify the original scenario and affected contracts with appropriate checks.
   Report actual evidence, changed scope, unresolved cases and unverified behavior.
   Recurrence may justify a proposed structural safeguard, not automatic new rules.

Done: the causal repair and relevant uses are verified, or remaining gaps are explicit.
