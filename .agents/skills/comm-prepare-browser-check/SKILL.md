---
name: comm-prepare-browser-check
description: Use when preparing or diagnosing application browser-check conditions, including prototype previews; excludes harness validation.
---

# Establish browser conditions

Inputs: scenario, revision/resources, environment, authority.
Reuse valid evidence; recheck changed/unverified conditions.
Before the relevant actions read:
- Version/serving/preview: [artifacts](references/artifacts.md).
- Cache/storage/theme/viewport: [state](references/state.md).
- Session/process allocation/cleanup: [lifecycle](references/lifecycle.md).
- Navigation/data/API/observation: [preconditions](references/preconditions.md).

Use project tools; choices/gaps use comm-choose-effective-solution. Preserve
startup/check/permission/evidence owners; no implicit installation, repair or
cleanup of others' resources.

Done: actual conditions/evidence or exact gaps. Setup failure alone proves no
product defect. Harness validation stays separate.
