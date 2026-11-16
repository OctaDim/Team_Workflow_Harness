# Prepare the PR

Verify repository/head/base and intended commits; ambiguity needs the user.
Before describing PR changes read
harness/common/skills/comm-verify-project-facts/references/git-integration.md.
Separate task changes since the merge base from target advancement.
A head lacking target-only additions is not deleting them in the PR;
judge post-merge effects against the merge-time integration base.
Necessary ordinary publication to the agreed remote is included, not a new fork,
forced rewrite or local branch changes.
Use the project's template: problem/result, actual checks with revision/
environment and evidence links, failed/unrun checks and limits/reasons.
Use comm-run-project-checks for application reports and comm-validate-harness-instructions for harness reports; retain full evidence with comm-protect-harness-evidence.
Update changed scope/version and verify saved text; templates/CLI do not
automatically supply truthful verification content.
