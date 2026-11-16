---
name: comm-check-publication-data
description: Use when preparing a commit, push, or PR text or attachment for publication, or checking staged/outgoing material for credentials or sensitive data.
---

# Check publication data

Inputs: staged content/message, outgoing range and PR materials.

1. Inspect staged content/message before commit and every outgoing commit/material
   before publication, including intermediate history. Keyword hits are candidates;
   confirm sensitivity and scope from evidence.
2. Agent/tools must never include credentials, secrets or sensitive data in committed
   files/messages or PR titles, descriptions, comments or attachments. Use placeholders
   or anonymized examples. Public configuration and Git identity are not inherently
   secret; clarify uncertain classification before publication.
3. Process files/diffs/messages/helper sources in-process. Tool output schema:
   location, type, status, count. Locations use path/line/commit identifiers;
   types/statuses are fixed classification labels, counts numeric. Source literals,
   matched text and exception strings are content, never metadata. Scanner silence
   or partial redaction cannot establish safety. Never upload values for analysis.
   For configuration placement use comm-separate-application-config.
4. Confirmed findings stop dependent commit/publication; report location/type without
   values. Remediate only within authority; otherwise ask/wait. Never
   automatically rewrite history, rotate/revoke credentials or delete evidence.

Done: bounded publication decision with checked scope and unresolved gaps.
This grants no commit, push, PR, installation or incident-response authority.
