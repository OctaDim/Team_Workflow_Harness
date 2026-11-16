# Ambiguous Git/PR outcome

Record mutation completion/output/status separately from later observation;
filters/chains must not hide it. Error/timeout may follow success or partial
success. Before retry independently read the exact repository/ref/PR and expected
effect: saved field, published SHA, merge or deletion.
Classify complete/partial/not done/unknown; failed observation proves no rollback.
Never repeat completed parts. Continue only authorized remaining work.
Changed/conflicting state or unresolved safety: explain, propose and await
the user. CLI/API changes never bypass permissions; use the blocker owner when
needed. Report observed effects and gaps separately.
