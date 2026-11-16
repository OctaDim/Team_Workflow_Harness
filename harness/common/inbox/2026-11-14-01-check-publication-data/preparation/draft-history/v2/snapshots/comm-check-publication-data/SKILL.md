---
name: comm-check-publication-data
description: Use when preparing a commit, push, or PR text or attachment for publication, or checking staged/outgoing material for credentials or sensitive data.
---

# Check publication data

Inputs: exact staged changes, outgoing commit range, messages and PR materials.

1. Inspect the actual staged content/message before committing and outgoing
   commits/materials before publishing; checking only the latest tree is insufficient.
2. Agent/tools must never include credentials, secret or sensitive data in
   committed files/messages or PR titles, descriptions, comments or attachments.
   Use safe placeholders or anonymized examples. Public configuration and Git
   identity are not inherently secret; clarify uncertain classification before publication.
3. Use existing authorized checks and contextual review. A scanner's silence
   does not prove safety. Do not print values, upload them for analysis, or include
   them in reports. For configuration placement use comm-separate-application-config.
4. On detection, stop the dependent commit/publication and report location/type
   without values. Remediate only within existing authority; otherwise ask and wait.
   Never automatically rewrite history, rotate/revoke credentials or delete evidence.

Done: a bounded publication decision with checked scope and unresolved gaps.
This grants no commit, push, PR, installation or incident-response authority.
