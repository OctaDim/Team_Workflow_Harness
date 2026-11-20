# Before a Git mutation

Identify repository/worktree, branch/HEAD, intended operation and relevant
staged, unstaged and untracked changes; distinguish owned, foreign and unknown.
Preserve foreign edits and their exact staging, including shared files.
Never stash, commit, reset, clean or move unrelated work to make a clean tree.
Checkpoints retain the commit owner's gates.

Do not overlap an unsafe operation with an active writer to affected files,
index or shared refs. Coordinate completion or authorized isolation; never
stop another writer automatically. Worktrees are optional and share some refs/config.
Unknown ownership or unsafe overlap blocks dependent mutation: explain and wait;
independent reads may continue. Inspect again when relevant state changes.

In the harness author checkout (`harness/AGENTS.bootstrap.md.in` present), when
the layout, the portable startup command in AGENTS.md, or the reading-order
section of harness/common/START.md changes, run the ordinary entrypoint check
after editing and before staging. Include the reported bootstrap template in
the same change. Preserve unrelated edits and existing entrypoint settings.
