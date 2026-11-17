# Apply a full Superpowers route

Read after either full route is selected, before applying it. Use installed
Superpowers skills, not a copied workflow. Preserve the selected executor.

1. Load using-superpowers, then brainstorming. Agree the specification before
   writing-plans; obtain plan approval before implementation. The plan cites
   its specification and maps requirements to tasks and verification.
2. Invoke only the selected executing-plans OR subagent-driven-development.
   Carry test-driven-development into implementation: observed expected RED
   before behavior changes, GREEN afterward; exceptions require applicable
   approval. Evidence, not an implementer's claim, establishes completion.
3. Follow that executor's task/final reviews, fix loops and verification;
   do not add a duplicate review chain. Load debugging/isolation helpers only
   when their conditions apply. Unavailable or forbidden tools stop dependent
   work; never silently switch executor, omit review or substitute CE.
4. Preserve recovery state: specification/plan identity, executor, phase,
   completed steps with commits/checks, rulings, review/fix-loop state,
   blockers, pending permissions and next step. Resume the same plan from
   recorded evidence; never replay completed tasks or adopt another plan's ledger.
5. Apply verification-before-completion throughout completion claims, then
   finishing-a-development-branch. Automatically advance only within authorized
   work; retain specification/plan, INBOX and integration/publication decisions.

Before records, read from project root
`harness/common/skills/comm-preserve-harness-knowledge/SKILL.md` and
`references/material-placement.md` within that skill. Classify purpose and
permission first: specification → package specs/, plan → docs/plans/,
recovery → handoffs/, evidence → its governed category. Keep memory inside
harness and preserve protected records; route selection grants no write/delete
permission. Before evidence use comm-protect-harness-evidence.

Inspect bundled workspace scripts before invocation: a fixed `.superpowers/sdd`
path is not relocated by putting the plan in harness. If relocation is unsupported,
stop dependent writes and agree an adaptation preserving the executor's recovery
protocol. Never patch the plugin, use symlinks, duplicate the ledger outside
harness, or delete required recovery/evidence records as an implicit workaround.
