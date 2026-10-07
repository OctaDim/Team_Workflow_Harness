# Plugin Eval Start Here: comm-process-harness-inbox

## At a Glance
- Recommended path: Evaluate Skill
- Benchmark config present: no
- Usage log present: no
- Quick local entrypoint: `plugin-eval start ~/MyProjects/GLOBAL_HARNESS_ENVIRONMENT/harness/common/inbox/2026-10-07-workflow-48-lessons-to-skills/candidate/harness/common/skills/comm-process-harness-inbox --request 'Evaluate this skill.' --format markdown`
- First local command: `plugin-eval analyze ~/MyProjects/GLOBAL_HARNESS_ENVIRONMENT/harness/common/inbox/2026-10-07-workflow-48-lessons-to-skills/candidate/harness/common/skills/comm-process-harness-inbox --format markdown`

## Why It Matters
- Start with a natural chat request, then let plugin-eval show the exact local command sequence behind it.
- Plugin Eval routed "Evaluate this skill." to Evaluate Skill because it asks for the overall evaluation report or prioritized findings from it.

## Fix First
- Start with the recommended path before branching into secondary workflows.

## Recommended Next Step
- Evaluate Skill
- Why: Plugin Eval routed "Evaluate this skill." to Evaluate Skill because it asks for the overall evaluation report or prioritized findings from it.
- Chat request: "Evaluate this skill."
- Local command: `plugin-eval analyze ~/MyProjects/GLOBAL_HARNESS_ENVIRONMENT/harness/common/inbox/2026-10-07-workflow-48-lessons-to-skills/candidate/harness/common/skills/comm-process-harness-inbox --format markdown`

## Details
<details>
<summary>Full local sequence</summary>

- plugin-eval analyze ~/MyProjects/GLOBAL_HARNESS_ENVIRONMENT/harness/common/inbox/2026-10-07-workflow-48-lessons-to-skills/candidate/harness/common/skills/comm-process-harness-inbox --format markdown
</details>
<details>
<summary>Other chat requests</summary>

- Full Skill Analysis: "Give me a full analysis of this skill, including benchmark setup." -> plugin-eval analyze ~/MyProjects/GLOBAL_HARNESS_ENVIRONMENT/harness/common/inbox/2026-10-07-workflow-48-lessons-to-skills/candidate/harness/common/skills/comm-process-harness-inbox --format markdown
- Evaluate Skill: "Evaluate this skill." -> plugin-eval analyze ~/MyProjects/GLOBAL_HARNESS_ENVIRONMENT/harness/common/inbox/2026-10-07-workflow-48-lessons-to-skills/candidate/harness/common/skills/comm-process-harness-inbox --format markdown
- Explain Token Budget: "Explain the token budget for this skill." -> plugin-eval explain-budget ~/MyProjects/GLOBAL_HARNESS_ENVIRONMENT/harness/common/inbox/2026-10-07-workflow-48-lessons-to-skills/candidate/harness/common/skills/comm-process-harness-inbox --format markdown
- Measure Real Token Usage: "Measure the real token usage of this skill." -> plugin-eval init-benchmark ~/MyProjects/GLOBAL_HARNESS_ENVIRONMENT/harness/common/inbox/2026-10-07-workflow-48-lessons-to-skills/candidate/harness/common/skills/comm-process-harness-inbox
- Benchmark With Starter Scenarios: "Help me benchmark this skill." -> plugin-eval init-benchmark ~/MyProjects/GLOBAL_HARNESS_ENVIRONMENT/harness/common/inbox/2026-10-07-workflow-48-lessons-to-skills/candidate/harness/common/skills/comm-process-harness-inbox
- Start Here: "What should I run next?" -> plugin-eval analyze ~/MyProjects/GLOBAL_HARNESS_ENVIRONMENT/harness/common/inbox/2026-10-07-workflow-48-lessons-to-skills/candidate/harness/common/skills/comm-process-harness-inbox --format markdown
</details>
