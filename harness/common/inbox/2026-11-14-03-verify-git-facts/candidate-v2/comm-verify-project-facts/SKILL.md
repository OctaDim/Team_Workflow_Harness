---
name: comm-verify-project-facts
description: Use when a decision depends on uncertain, historical, negative or availability claims about the current project or tool.
---

# Verify current project facts

Inputs: claim/decision, project/version/environment, authorized evidence.

1. Inspect relevant current code, configuration, research, decisions, requests
   and connected sources. Check applicability before reusing findings.
2. Separate observation, contract and hypothesis. Recheck material dated claims
   against authoritative current evidence; old documents/statuses/successes
   alone do not prove today's state.
3. For absence search relevant locations/naming variants; check coverage, filters
   and available positive controls. Failed/incomplete searches prove uncertainty,
   not absence; qualify conclusions.
4. Probe availability safely within authority when needed. Catalog/health alone
   is insufficient. Missing permission/evidence remains unresolved; never bypass restrictions.
5. Read only applicable Git resources: [base state](references/git-base-state.md)
   for base/revision freshness; [integration](references/git-integration.md)
   for task/PR completion, supersession, current behavior or deployment, not merely
   the integration branch’s freshness; [operation result](references/git-operation-result.md)
   after ambiguous Git/PR outcomes. Other facts need none of these resources.
6. Report sources/version/date, observations, contradictions, limits, conclusions
   and affected current statements. Follow recording/evidence
   routes and preserve history.

Done: current evidence or explicit unresolved facts.
Solution choice, repair and mutation authority remain separate.
