---
name: comm-check-publication-data
description: Use when preparing a commit, push, or PR text or attachment for publication, or checking staged/outgoing material for credentials or sensitive data.
---

# Check publication data

Inputs: staged changes, proposed message, outgoing range and PR materials.

1. Inspect staged content/message before committing and all outgoing commits/materials
   before publishing, including intermediate history.
2. Agent/tools must never include credentials, secret or sensitive data in committed
   files/messages or PR titles, descriptions, comments or attachments. Use placeholders
   or anonymized examples. Public configuration and Git identity are not inherently
   secret; clarify uncertain classification before publication.
3. Inspect potentially sensitive files, diffs, messages and helper sources in-process;
   emit only locations/types and allowlisted safe metadata, including tool output.
   A scanner's silence or partial redaction does not prove safety. Never upload values
   for analysis. For configuration placement use comm-separate-application-config.
4. On detection, stop the dependent commit/publication and report location/type without
   values. Remediate only within existing authority; otherwise ask and wait. Never
   automatically rewrite history, rotate/revoke credentials or delete evidence.

Done: bounded publication decision with checked scope and unresolved gaps.
This grants no commit, push, PR, installation or incident-response authority.
