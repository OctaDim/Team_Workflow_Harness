---
name: comm-manage-production-rollout
description: Use when an action may deploy to production, including a tag push, auto-deploy push or merge, workflow dispatch, live migration or rollback, or when verifying or recovering a rollout.
---

# Manage a production rollout

Inputs: authorized scope, environment, exact release artifact and trigger.

1. Before triggering a rollout, require an explicit deploy instruction. Perform
   only authorized read-only preflight. Show environment, exact SHA or immutable
   artifact ID, included changes, trigger, prerequisites and material risks.
   Ask for affirmative confirmation in a later message. Plan, PR and tool
   approvals retain their own scope. Wait before triggering deployment or
   performing prerequisites that change production.
2. Recheck approved parameters and prerequisites before proceeding. A changed
   environment, artifact, trigger or material risk needs fresh confirmation.
   Execute within the confirmed scope.
3. Match the exact run and live artifacts on affected targets to the approved
   release. Verify the affected function at its normal entry point. For a schema
   change, check the actual revision and exercise a scenario using it. Report run,
   delivery and behavior separately. Mark unavailable checks unverified.
4. For a failed or partially applied rollout, read
   [partial rollout recovery](references/partial-rollout.md).
