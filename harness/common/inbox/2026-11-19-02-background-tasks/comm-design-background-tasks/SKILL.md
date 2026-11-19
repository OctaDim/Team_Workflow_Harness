---
name: comm-design-background-tasks
description: Use when designing or changing scheduled work, replayable background handlers, batch processing or polling of external operations.
---

# Design reliable background tasks

Apply the relevant cases.

- Define what happens after delays, downtime, restarts and schedule changes. Align disjoint windows to scheduled times. Persist progress and catch up required work. Make permitted skips distinguishable. On first applying or changing configurable schedules, check actual firing times and frequency against task limits. Follow the project's error contract for required or optional tasks. With controlled time, verify restart, downtime across a boundary, processing a boundary item once, and a scheduler-accepted setting that would fire too often or too rarely.
- Reuse duplicate protection where the effect is recorded, using a stable operation identifier or durable state. Replay input that reaches the same operation again. Verify one retained effect, including competing attempts when concurrency is supported.
- Isolate independent item failures. Expose each outcome to the retry decision. Verify one local failure followed by another item's success. Cancellation, shared failure or required atomicity may stop the batch.
- Define polling start, cadence, observation deadline and stop conditions. Verify a read timeout preserves the last confirmed status. Stop on confirmed terminal status or expiry. Record expiry and its next action. Preserve the deadline and stopped state across restarts.
