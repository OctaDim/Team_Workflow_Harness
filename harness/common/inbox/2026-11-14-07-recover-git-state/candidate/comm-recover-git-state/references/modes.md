# Select by actual state

Unfinished operation: use its corresponding abort only after checking applicability
and preservation. merge --abort may not reconstruct pre-existing uncommitted work.
Unpublished result: first propose a work-preserving route. Destructive reset needs
explicit exact branch, target SHA and file/index consequences; clean status alone
is not permission.
Published result: prefer a new checked corrective commit via the authorized
publication route. Compare focused repair versus revert by required behavior;
uncertainty needs the user's decision. Inspect merge parents before mainline
selection; revert -m 1 is not universal, especially for squash/rebase results,
and reverting a merge affects later merges.
Lost ref: read existing refs/reflog to locate and inspect a surviving commit.
Reflogs are local and expire; promise no recovery of all data. An authorized
recovery branch needs a stated purpose/source SHA and safe name, without changing
the original branch. Before creating it read
harness/common/skills/comm-create-git-branch/references/naming.md; its source is
the expressly agreed recovery SHA. Never prune/expire logs or overwrite evidence.
