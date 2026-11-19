---
name: comm-retry-external-operations
description: Use when designing API errors, client timeouts, retries or recovery after losing the response to an external operation.
---

# Retry external operations safely

Define API errors and when the operation can safely be repeated. Map request timeout, network failure, cancellation and API errors to caller-visible outcomes and retry eligibility. Stop on cancellation and non-retryable errors.

If the service may have acted before the response was lost, preserve the unknown outcome and reconcile by a stable operation identifier. Inconclusive reconciliation leaves it unknown. Retry automatically only within the API's idempotency guarantees or after reliable confirmation that the original attempt did not execute.

Set a per-request timeout, attempt limit, exhaustion outcome and overall deadline covering all attempts and waits, including SDK retries. Default to increasing delays with jitter. Honor the service's earliest retry time. Stop without another request if the wait would exceed the deadline.

Verify that losing the response after the service acted produces no duplicate. Use controlled time to verify request timeout, transient recovery, cancellation, non-retryable failure, budget exhaustion and no further request when the service's delay exceeds the deadline.
