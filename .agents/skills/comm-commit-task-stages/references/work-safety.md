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

For a protected-entrypoint migration, commit only the explicitly owned stage and exact files. Stage the approved templates and their working copies only at the authorized publication stage. Never generate a canonical template from the working AGENTS.md or a retired START.md. Verify the installed checker and fresh starts in isolated installations.
