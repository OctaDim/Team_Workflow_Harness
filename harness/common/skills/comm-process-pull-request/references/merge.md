# Merge the checked PR

Complete the publication-data owner check of the supplied outgoing scope and
proposed squash message before merging. Prior feature checks or merely reading
the owner are not clearance for these materials.
Any unchecked material or incomplete/uncertain publication review blocks the
merge call. Resolve it through that owner first; a guarded call is still an
attempt to publish.

Recheck repository/PR, head/base names/SHAs, open/non-draft state and mandatory
checks/reviews for the head or tested combined result. Match expected head;
GitHub --match-head-commit guards head, not base. Read
harness/common/skills/comm-verify-project-facts/references/git-base-state.md
for target races and the project's checked-integration mechanism. Never bypass gates.

Queued/requested is not merged. Confirm MERGED, result SHA on intended integration
and actual delta from its real base; inspect unexpected loss/change.
After target advancement require no universal tree equality or patch-id/file-list
proof. Mismatch: stop later actions, report and await the user; no automatic
repair, local mutation or remote cleanup.
