---
name: comm-process-harness-inbox
description: Use when creating, executing, closing or resuming harness inbox requests.
---

# Process one request

Identify the request, current status, chronology, full contents and explicitly
authorized stages. Before recording, executing or changing status read
[workflow](references/workflow.md). Do not infer execution from creation.

1. Reconcile existing results/status; resume remaining work, do not repeat completed
   requests without instruction. Process one from earliest to latest.
2. Create/retain the full dated request and candidate/resources; execute only the
   authorized scope. Missing permission/conflict: ask and wait, no next request.
3. Publish the required result and preserve permanent evidence independently of
   inbox. A ready candidate does not close a request requiring publication.
4. Update each request's status, result, reason and actual update time. Finish with
   completed/skipped/remaining requests and reasons.

For a direct bypass of the protected scope defined in workflow, require explicit named paths/operations and a separate
question → unequivocal positive answer after it. Preliminary confirmation is
not that answer; keep waiting without writes. Known technical errors within
existing authorization can be corrected.
