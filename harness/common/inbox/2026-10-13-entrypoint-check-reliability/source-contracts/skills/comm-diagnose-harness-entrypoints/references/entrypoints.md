# Safe entrypoint diagnosis

Run from root `python3 -B harness/common/checks/ensure_entrypoint_links.py` with
Python3.9+. Agent starts it; no required Git/hooks/hooksPath/registration or
machine config. It does not change Git settings or block writes/commits.
Protected AGENTS/CLAUDE edits are forbidden by agreement, not technically blocked;
propose changes through harness/<package>/inbox, whose existence is not permission.

Check installed START/INDEX and ordinary safe inputs. Missing rule directory
may be created; symlink/path-file errors refuse BEFORE protected input repair.
Checker restores START/INDEX links, .claude/rules link and Codex recursive
Markdown reading except README.human.md; Claude imports relative @AGENTS.md.
Before repair print damaged-and-will-write notice, never when intact. Other
settings and an existing startup command remain unchanged. Startup may create
only an absent neutral project from agreed common skeleton, preserving existing
project; no authority for template/existing-project migration.

CLAUDE must be exactly @AGENTS.md with optional final newline; preserve extra/
different text, warn and route a proposed correction through inbox. If Git/HEAD
has inputs, compare settings excluding generated AGENTS startup links/rule reading.
Without Git/version, arbitrary settings comparison is unverified; structure/
import still checked, never automatically register current text as baseline.

Both connection detection and Git comparison share line-based top-level fence
parsing: at least3 backticks/tildes, indentation≤3spaces; closer same character,
length≥opener, trailing spaces/tabs only. Inside links/instructions are examples.
Unclosed CURRENT fence errors with line number before input writes/rule directory
creation; never auto-close. Unclosed historical fence is code to EOF, cannot
block valid current input. This is not a nested-container Markdown parser.

Settings warnings keep success exit and do not block tasks. Resource damage,
unsafe paths or I/O errors may fail because safe checking is impossible, not
because editing is mechanically prohibited. Notify with exact cause/path/line;
retain actual output and status, not a guessed successful remedy.

For current regression checks use .venv Python pytest with
harness/common/testing/tests/test_ensure_entrypoint_links.py and
harness/common/testing/tests/test_entrypoint_notifications.py. They cover no-Git,
extra/direct text preservation, notice before repair/no false notice, no hooks/
new machine settings and ordinary commits after warning. Historical results
are preserved outside working instructions, never substitute fresh checks.
