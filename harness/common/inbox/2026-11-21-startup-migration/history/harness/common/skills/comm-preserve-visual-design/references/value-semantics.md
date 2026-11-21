# Bind values by visual intent

Before replacing a literal or binding a shared token, establish its semantic role
and approved reference/version. Equal current values do not establish a shared
contract. History helps identify changes, not decide which design is correct.

Compare suitable choices within project design-system constraints:
- Reuse a token when its role and intended future variation match the element.
- Propose a separate semantic token when an independent role justifies maintenance.
- A fixed value may preserve a versioned approved prototype when project rules
  allow it; it is not automatically an error or an exemption from those rules.

Choose by intended behavior and evidence, not literal/token quotas or a blanket
"token changed, so literal is right" rule. Apply the skill's existing approval
and delegation conditions for material deviations; verify affected renders/states.
Reference provenance belongs to the existing reference record; browser artifact
identity and prototype serving use comm-prepare-browser-check. Do not duplicate
those algorithms or automatically update the reference to latest.
