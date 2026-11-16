# Spec-flow pass: SQL database agreement

Read-only planning review, 2026-10-16. Inputs: the confirmed Product Contract in `harness/common/docs/plans/2026-10-16-0106-feat-confirm-database-design-plan.md`, the request and three instruction candidates in its inbox directory, and applicable installed harness rules. No behavioral tests, publication or project edits were performed. The mandatory entrypoint check passed. README.human.md bodies were not read.

## User flows

1. New SQL-dependent plan/spec/code → inspect read-only context and current approvals → explain required applicable alternatives → ask → explicit scoped approval → work only within those boundaries. Existing implementation supplies evidence, not consent.
2. Partial approval (for example schema SQLAlchemy/Alembic only) → preserve that decision → keep query/lifecycle decisions open → stop only the work dependent on unresolved choices. The schema approval does not authorize all three blocks.
3. Ambiguous answer, silence or UI default → retain the unresolved state and clarify; no dependent changes. Explicit delegation resolves only its named technical details.
4. Existing unchanged approval → reuse it without another question. A material new decision, changed approach or expanded library exception opens only the newly affected choice.
5. Non-Python stack or no ORM sessions → explain applicability; do not force Python/ORM into the project. Required alternatives are comparison content, not mandatory dependencies.
6. Approval in current conversation but no permission to write its durable record → preserve the approval, follow placement/permission owners, do not write protected files. Work already authorized and independent of the missing permission can proceed; the durable-record completion criterion remains pending.
7. Validation → separate Codex/Claude × common-only/common+project observations, including early triggering and unrelated-task nonloading → truthful per-cell status. Tool/auth failure yields unverified status. Publication still requires its separate permission.

## Gaps by severity

No critical product-flow gaps or new user decisions were found. Partial approvals, repeated approvals, ambiguity, applicability and protected writes already have controlling requirements; these should not generate another scope questionnaire.

One important editorial inconsistency should be resolved during the already-authorized candidate refinement: SKILL.md step 5 says “Record ... Then proceed”, which can be read as blocking all implementation on durable recording. Step 6 permits settled work despite missing permission, and choices.md explicitly preserves approvals while a permitted save is pending. Product Contract R6 also preserves current-dialogue consent. State in the owner skill that only work dependent on the missing write permission is blocked, and that the durable-record completion requirement can remain pending without invalidating the approved architecture. This is an alignment of existing requirements, not added functionality or an exception to permission rules.

## Questions

None required. The confirmed Product Contract and installed permission owners provide the answers. No route or scope reapproval is warranted.

## Recommended next steps

- In the implementation plan, explicitly include the candidate wording alignment above.
- Include a multi-turn partial-approval scenario: schema accepted, query/lifecycle unresolved; verify the agent neither repeats schema approval nor treats it as approval for all blocks.
- Include a pending-save scenario: architecture approved in the current dialogue, durable write permission absent; verify no protected write, no lost approval, no unnecessary reapproval, and honest incomplete recording status.
- Keep changed-approach/third-party-exception expansion and non-Python/no-session cases in the already-required behavioral matrix.
- Adapt existing runners for the four agent/mode cells, check present availability at execution time, and record native listing, explicit/implicit loading, conditional resources, unrelated-task nonloading and behavior separately. Historical Claude OAuth failure is not evidence of current failure or success.
