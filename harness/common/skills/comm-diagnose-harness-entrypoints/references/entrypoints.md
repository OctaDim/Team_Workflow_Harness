# Safe entrypoint diagnosis

Run from root `python3 -B harness/common/checks/ensure_entrypoint_links.py` with
Python3.9+. Agent starts it; no required Git/hooks/hooksPath/registration or
machine config. It does not change Git settings or block writes/commits.
Protected AGENTS/CLAUDE edits are forbidden by agreement, not technically blocked;
propose changes through harness/<package>/inbox, whose existence is not permission.

Use only the trusted ordinary common Python file, directly, without a project
wrapper/launcher. Symlinks in the checker path (including ancestors), target root
and input paths are forbidden; the checker refuses before repair. An arbitrary
substituted Python file cannot authenticate itself: executing the installed
trusted code is a launch prerequisite, not a guarantee about attacker code.

Check nonempty UTF-8 START/INDEX and the entire ordinary canonical/native
comm-/proj- rule set for names and equal bytes. Missing/extra/different copies,
empty canonical content, unreadable paths and symlinks refuse BEFORE repair.
Never automatically publish missing copies. Personal nested rules and human
guides do not count as extra canonical copies; human bodies are not loaded.
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

Connection detection and Git comparison share a line classifier for top-level
fences and fences in nested quotes or one list item, including quoted lists.
Markers: at least3 backticks/tildes; closer same character, length>=opener,
trailing spaces/tabs only. Quote depth and space indentation of a list must
remain consistent; ambiguous container exits refuse. Inline and indented code
examples are excluded. CURRENT unclosed fences refuse before writes; historical
unclosed code remains an example through EOF. This is a bounded classifier,
not a complete Markdown parser; recursive list-item containers are unsupported.

Each generated startup block is checked independently, including a separate
rules-reading line. Complete wrong-order blocks refuse without reordering;
partial blocks require at least3 distinct canonical labels/targets in valid
relative order. Smaller/custom partial lists refuse. Complete global connections
distributed outside full blocks are preserved; a complete block elsewhere makes
each damaged repeated block independently repairable. Relative/angle/anchor
links are recognized; arbitrary user lists are not extended by guessing.
Expected order: START common, START project, rules, INDEX common, INDEX project.

Before writing compare original input bytes and identity/metadata, then use a
temporary regular file in the same directory and atomic replace, preserving
existing POSIX ownership/mode, supported extended attributes/ACL and untouched
EOL bytes; metadata-copy failure refuses replacement. A detected parallel edit refuses.
Errors report completed changes and still-pending inputs; no rollback of foreign
edits or multi-file transaction. A concurrent editor between final comparison
and rename cannot be excluded without a shared locking protocol. Power-loss durability of a directory rename and native Windows ACL preservation
are not established by the Linux checks.

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
