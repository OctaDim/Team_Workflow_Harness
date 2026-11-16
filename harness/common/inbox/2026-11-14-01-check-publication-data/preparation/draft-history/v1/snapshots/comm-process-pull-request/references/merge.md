# Merge the checked PR

Re-resolve repository, PR, head/base names and SHAs; require open/non-draft state
and current mandatory checks/reviews for the head or tested combined result.
Match the expected head during the operation; on GitHub --match-head-commit
guards head, not base. Apply git-base-state.md under comm-verify-project-facts
for target advancement/races and the project's checked-integration mechanism.
Never bypass gates/protections to finish.

Queued/requested is not merged. Confirm MERGED, result SHA on intended integration,
and actual delta from its real base; inspect unexpected loss/change.
Do not require tree equality after target advancement or treat patch-id/file
lists as universal proof. On mismatch stop later actions, report facts and await
the user; no automatic repair, local mutation or remote cleanup.
