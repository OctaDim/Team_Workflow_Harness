---
name: comm-check-publication-data
description: Use when preparing a commit, push, or PR text or attachment for publication, or checking staged/outgoing material for credentials or sensitive data.
---

# Check publication data

1. Bind supplied ranges and material paths verbatim; resolve exact boundaries.
   Missing/ambiguous scope: ask, never guess or substitute wider history.
2. Inspect staged content and the proposed message before commit; inspect every
   outgoing commit, including files/messages, and PR materials before publication.
   Include intermediate history. Confirm keyword candidates against classification evidence.
3. Agent/tools must never include credentials, secrets or sensitive data in committed
   files/messages or PR titles/bodies/comments/attachments. Use placeholders/anonymized
   examples. Public configuration/Git identity are not inherently secret; clarify uncertainty.
4. Inspect content, diffs, messages and helper sources in-process. Output only
   location/type/status/count: exact nonsecret scope identifiers, fixed labels,
   numeric counts. Other source literals, matched text and exception strings stay
   private. Scanner silence/partial redaction cannot establish safety; never upload
   values. For configuration placement use comm-separate-application-config.
5. Confirmed findings stop dependent commit/publication. Remediate only within
   authority; otherwise ask/wait. Never automatically rewrite history, rotate/revoke
   credentials or delete evidence.

Result: checked scope, findings/gaps; no commit/push/PR/installation/incident-response authority.
