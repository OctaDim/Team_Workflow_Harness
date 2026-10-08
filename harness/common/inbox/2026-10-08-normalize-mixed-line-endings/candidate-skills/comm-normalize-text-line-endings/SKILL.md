---
name: comm-normalize-text-line-endings
description: Use when explicitly normalizing LF/CRLF text files for cross-platform use, including mixed endings and Windows batch exceptions.
---

# Normalize the authorized files

Establish exact files and permission for whole-file EOL conversion. Mixed endings
alone do not authorize normalization during a narrow repair. Protected harness
files still require their authorized inbox route.

1. Confirm text format and UTF-8 bytes; retain the original. Unknown encoding,
   binary data or lone CR: stop without rewriting. Preserve encoding, BOM and
   terminal-newline presence; do not change other content.
2. Honor explicit format requirements. Otherwise select CRLF for `.bat`/`.cmd`
   case-insensitively, LF for ordinary text and `.sh`. LF is the default for new
   ordinary text. Do not infer safe batch execution from editor support for LF.
3. Within the approved scope, replace CRLF with LF; for a CRLF target then replace
   LF with CRLF. Write only changed files. Compare content excluding these EOL
   replacements and verify a second conversion is byte-identical.

Use temporary mixed/LF/CRLF fixtures, including batch labels/subroutine calls.
Actual batch execution needs Windows cmd.exe; unavailable runtime remains unverified.

Done: named files have the required EOL, other bytes and unapproved files remain
unchanged, and actual checks or missing prerequisites are reported.
