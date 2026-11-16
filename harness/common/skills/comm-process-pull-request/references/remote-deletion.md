# Delete the agreed remote task ref

Use option 3 after confirmed merge of the agreed PR version.
Recheck head repository/ref, including forks; remote ambiguity needs the user.
Categorically never delete remote main, master, or any primary, integration or
protected branch, including through helpers/mirroring.
New commits, continuing work or dependent open PRs: explain and await the user.
Account for races; prefer an expected-SHA condition at deletion, checking its
availability/limits first.

Obey PR local read-only limits. Affect only the agreed remote ref. Verify remote
absence and preservation of the existing local branch. Discrepancy: stop, report
facts and wait for the user; no autonomous restoration or other changes.
Unavailable checks remain uncertain. Already absent: report, never recreate/redelete.
