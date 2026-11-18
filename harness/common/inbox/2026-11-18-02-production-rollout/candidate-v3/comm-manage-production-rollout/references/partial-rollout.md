# Recover from a partial rollout

1. Inspect the exact run and live state within authorized access. Record which
   steps applied, partially applied or remain unknown. Identify serving and
   failed instances, artifact versions, traffic routes, schema and configuration.
2. Preserve healthy instances serving traffic. Target cleanup or replacement
   at identified affected instances. When identity or serving status is unclear,
   resolve it before changing capacity.
3. Compare rollback and forward repair against the actual schema, configuration
   and completed writes. Require demonstrated compatibility before choosing
   rollback. Show the proposed action, affected scope and risks, then use the
   rollout confirmation procedure. Scope any data restoration separately.
4. After the agreed action, verify live artifacts and affected behavior through
   the rollout verification step.
