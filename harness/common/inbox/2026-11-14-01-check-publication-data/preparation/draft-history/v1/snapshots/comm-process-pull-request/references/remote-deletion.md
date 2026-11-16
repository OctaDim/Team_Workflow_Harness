# Delete only the agreed remote task ref

Use option 3's permission after confirmed merge of the agreed PR version.
Recheck exact head repository/ref, including forks; remote ambiguity needs the
user's answer. Categorically never delete remote main, master, or any primary,
integration or protected branch. Do not bypass this through helpers or mirroring.
New commits, continuing work or dependent open PRs require explanation and
the user's decision. Account for update races; prefer an expected-SHA condition
at deletion, checking the mechanism's availability/limits beforehand.

Obey the PR owner's local read-only boundary. Use an operation affecting only
the agreed remote ref. Verify remote absence and preservation of the existing
local branch. On discrepancy stop, report facts and wait for the user's answer;
no autonomous restoration or other changes. Unavailable checks remain uncertain.
Already absent: report observation, never recreate/redelete to manufacture success.
