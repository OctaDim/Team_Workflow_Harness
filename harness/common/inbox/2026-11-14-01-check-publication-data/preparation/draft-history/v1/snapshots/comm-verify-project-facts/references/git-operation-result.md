# Ambiguous Git/PR outcome

Keep each mutation's completion/output/status separate from later observation;
filters/chains must not hide the relevant result. Error/timeout may follow
success or partial success. Before retry, independently read the exact
repository/ref/PR and expected effect: saved field, published SHA, merge or deletion.
Classify complete/partial/not done/unknown; failed observation proves no rollback.
Never repeat completed parts. Only authorized remaining work may proceed.
Changed/conflicting state or unresolved safety requires explanation, proposal
and the user's answer. Changing CLI/API is no permission bypass; apply the
permission-blocker owner when needed. Report observed effects and gaps separately.
