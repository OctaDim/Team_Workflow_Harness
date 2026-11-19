# Preserve unfinished work

A: new branch from fresh integration plus controlled transfer of necessary work.
Useful for partial/mixed old work; inspect dependencies, already integrated
changes and omissions. Use comm-create-git-branch; preserve the source.
B: update the existing task branch by the project's authorized method.
Useful for cohesive continuing work/PR identity; assess conflicts and collaborators.
Never prescribe merge, rebase or cherry-pick universally. Published-history
restrictions remain; do not rewrite others' base or force-publish automatically.
Keep deliberate feature dependencies distinct from stale ancestry.

Do not stash/commit foreign work to clean the tree. Local commits use
comm-commit-task-stages and compound-engineering:ce-commit, including commits produced by integration;
choose an operation mode that preserves this gate or stop. During PR operations
the local branch stays read only; necessary preparation requires an agreed
separate scope, never an automatic context switch.
