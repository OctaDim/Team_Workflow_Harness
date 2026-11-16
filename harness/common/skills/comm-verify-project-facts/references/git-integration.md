# Remaining integration work

State whether the claim concerns integration, current behavior or deployment.
Check agreed outcomes against frozen target/source SHAs and relevant merge
bases; separate task changes from target advancement. Counts/ancestry,
git cherry and patch-id are evidence with limits, especially after squash.
MERGED proves neither current behavior after later changes nor deployment.
Compare both PRs' content and changes relative to integration before declaring
one superseded; inspect unique hunks, renames, docs and supporting files.
git diff A B describes A-to-B: A-only files are D, not A. File lists, one
symbol or truncated PR search do not prove coverage/absence. Recheck stale
handoff items; report present/missing/replaced/unverified with date/SHA.
Overlap or uncertainty: propose resolution and wait before transfer/closure.
