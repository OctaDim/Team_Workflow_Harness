# Plugin Eval Report: rules

## At a Glance
- Score: 86/100
- Grade: B
- Risk: high
- Checks: 1 fail, 0 warn, 4 info
- Active budget: 0 tokens (good)
- Observed usage: not supplied

## Why It Matters
- 1 failing error check are driving the highest-confidence problems.
- budget is the largest source of score loss at -14 points.
- Budget pressure is not the dominant issue right now.
- No observed usage is attached yet, so budget conclusions are still based on static estimates.

## Fix First
- [fail/error] deferred_cost_tokens is excessive relative to the current Codex baseline. Why: Budget pressure matters because always-loaded or frequently-loaded text can make the workflow feel expensive fast. Fix: Reduce repeated instruction text and move detail into deferred supporting files.

## Recommended Next Step
- Fix the top findings and rerun the report
- Why: A short pass on the highest-value findings will improve trust, readability, and the signal quality of future benchmarks.
- Chat request: "What should I fix first?"
- Local command: `plugin-eval start ~/MyProjects/GLOBAL_HARNESS_ENVIRONMENT/harness/common/rules --request 'What should I fix first?' --format markdown`

## Details
<details>
<summary>Watch next</summary>

- No secondary findings queued.
</details>
<details>
<summary>Improvement brief</summary>

- Raise the evaluation from grade B (86/100) with a focus on the highest-signal structural and budget issues first.
- Goal: Reduce repeated instruction text and move detail into deferred supporting files.
- Measure: token-usage-observer
- Measure: task-outcome-scorecard
- Suggested prompt: Use the skill-creator guidance to improve rules. Keep the structure compact and move bulky details into references or scripts. Define success measures with these toolsets: token-usage-observer, task-outcome-scorecard. Address deferred_cost_tokens-budget-high: deferred_cost_tokens is excessive relative to the current Codex baseline.
</details>
<details>
<summary>Budgets and observed usage</summary>

- trigger_cost_tokens: 0 (good)
- invoke_cost_tokens: 0 (good)
- deferred_cost_tokens: 3033 (excessive)
- total_tokens: 3033 (excessive)

- No observed usage supplied.
</details>
<details>
<summary>Measurement plan</summary>

Combine cost, outcome, and trust signals so you can tell whether the skill or plugin is genuinely helping instead of only looking well-structured on paper.

- Token Usage Observer [high] Measure how many tokens the skill or plugin actually burns in representative runs. Signals: observed_usage_sample_count, observed_input_tokens_avg, observed_total_tokens_avg, estimate_vs_observed_input_ratio. Evidence: Responses API usage logs, Codex-like session exports, JSONL traces captured from local benchmarking harnesses.
- Task Outcome Scorecard [high] Measure whether the skill helps users finish the intended job with fewer retries and less cleanup. Signals: task_success_rate, first_pass_success_rate, retry_rate, human_override_rate. Evidence: Task run logs, Structured user acceptance checklist, Before/after comparison runs on the same prompts.
- Tool Call Audit [medium] Check whether the agent uses the right tools, arguments, and sequencing when the skill is active. Signals: tool_call_success_rate, invalid_tool_argument_rate, recoverable_tool_failure_rate. Evidence: Tool invocation traces, Recorded sessions, Golden-path scenario replays.
- Latency And Efficiency [medium] Track whether the skill speeds users up enough to justify its cost. Signals: p50_time_to_first_acceptable_answer_seconds, p95_time_to_task_completion_seconds, tokens_per_successful_run. Evidence: Benchmark harness timings, Manual stopwatch runs on canonical tasks, Responses API timestamps combined with usage logs.
- Human Rubric Review [medium] Capture clarity, trust, and usefulness signals that automated checks will miss. Signals: clarity_score_avg, confidence_score_avg, follow_up_question_rate. Evidence: Reviewer scorecards, Team rubric sheets, Annotated transcripts.
- Regression Suite [medium] Protect the repository behavior that the skill is supposed to improve. Signals: test_pass_rate, lint_pass_rate, regression_escape_count. Evidence: Unit and integration test runs, Coverage deltas, Snapshot or golden-file checks.
</details>
<details>
<summary>Use From Codex Chat</summary>

Start with a natural chat request, then let plugin-eval show the exact local command sequence behind it.

Start with this chat request: "Evaluate this target."
Why this path: Plugin Eval recommended Evaluate Skill from the current local state for this target.
Quick local entrypoint: plugin-eval start ~/MyProjects/GLOBAL_HARNESS_ENVIRONMENT/harness/common/rules --request 'Evaluate this target.' --format markdown
Plugin Eval will run first: plugin-eval analyze ~/MyProjects/GLOBAL_HARNESS_ENVIRONMENT/harness/common/rules --format markdown

Other chat requests you can use:
- Full Skill Analysis: say "Give me a full analysis of this target, including benchmark setup." -> plugin-eval analyze ~/MyProjects/GLOBAL_HARNESS_ENVIRONMENT/harness/common/rules --format markdown
- Evaluate Skill: say "Evaluate this target." -> plugin-eval analyze ~/MyProjects/GLOBAL_HARNESS_ENVIRONMENT/harness/common/rules --format markdown
- Explain Token Budget: say "Explain the token budget for this target." -> plugin-eval explain-budget ~/MyProjects/GLOBAL_HARNESS_ENVIRONMENT/harness/common/rules --format markdown
- Measure Real Token Usage: say "Measure the real token usage of this target." -> plugin-eval init-benchmark ~/MyProjects/GLOBAL_HARNESS_ENVIRONMENT/harness/common/rules
- Benchmark With Starter Scenarios: say "Help me benchmark this target." -> plugin-eval init-benchmark ~/MyProjects/GLOBAL_HARNESS_ENVIRONMENT/harness/common/rules
- Start Here: say "What should I run next?" -> plugin-eval analyze ~/MyProjects/GLOBAL_HARNESS_ENVIRONMENT/harness/common/rules --format markdown
</details>
<details>
<summary>Checks</summary>

- [INFO] generic-target-analysis: The target is not a skill or plugin root, so only generic code, coverage, and budget analysis will run. Evidence: /home/octadim/MyProjects/GLOBAL_HARNESS_ENVIRONMENT/harness/common/rules Remediation: Point the analyzer at a skill directory or plugin root for richer structural checks.
- [FAIL] deferred_cost_tokens-budget-high: deferred_cost_tokens is excessive relative to the current Codex baseline. Evidence: Value: 3033 tokens Baseline samples: skills=1, plugins=0 Remediation: Reduce repeated instruction text and move detail into deferred supporting files.
- [INFO] coverage-artifacts-unavailable: No coverage artifacts were found for this target. Evidence: harness/common/rules Remediation: Generate `lcov.info`, `coverage.xml`, or an Istanbul coverage JSON file if you want coverage scoring.
</details>
<details>
<summary>Metrics</summary>

- trigger_cost_tokens: 0 tokens (good)
- invoke_cost_tokens: 0 tokens (good)
- deferred_cost_tokens: 3033 tokens (excessive)
- coverage_artifact_count: 0 files (info)
</details>
<details>
<summary>Score details</summary>

- Starting score: 100
- Total deductions: -14.5
- Final score: 86
- Risk: Contains 1 failing error check (deferred_cost_tokens-budget-high).

- -14 points: deferred_cost_tokens-budget-high [fail/error] deferred_cost_tokens is excessive relative to the current Codex baseline.
- -0.25 points: coverage-artifacts-unavailable [info/info] No coverage artifacts were found for this target.
- -0.25 points: generic-target-analysis [info/info] The target is not a skill or plugin root, so only generic code, coverage, and budget analysis will run.

- budget: -14 points across 1 check
- best-practice: -0.25 points across 1 check
- coverage: -0.25 points across 1 check
</details>
