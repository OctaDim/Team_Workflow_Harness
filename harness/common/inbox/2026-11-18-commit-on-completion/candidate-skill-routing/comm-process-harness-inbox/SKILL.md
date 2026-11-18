---
name: comm-process-harness-inbox
description: Use when creating, executing, resuming or closing harness inbox requests, or reporting candidate readiness.
---

# Process one request

Identify the request, status, chronology, contents and authorized stages. Before
recording, executing or changing status read [workflow](references/workflow.md).
Creation alone grants no execution.

1. Reconcile results and resume remaining work. Process oldest first. Skip
   completed requests unless asked to repeat.
2. Retain the full dated request and candidate. Stop for missing permission
   or conflict. Execute only authorized work.
3. Before reporting readiness, check all mandatory scenarios for this version.
   If incomplete, report gaps and actual statuses. Propose a specific fix or
   check, ask for a decision on that step, and wait. Offer publication only
   after all pass. When the user explicitly authorizes an exception after
   disclosure, follow comm-publish-harness-instructions.
4. Publish the required result, preserve permanent evidence outside inbox, then
   record status, result, reason and update time. A candidate alone cannot close
   required publication. For a closed request that changed repository files,
   find and apply the installed skill named `comm-commit-task-stages` before
   moving to another request or reporting completion. Record the commit, skip,
   or blocker. If that skill has no unique installed owner, stop the dependent
   step and report the reason. Report completed and remaining requests.

Direct bypass requires named paths and operations, then a separate question
and unequivocal positive answer. Wait without writes. Known technical errors
within existing authorization can be corrected.
