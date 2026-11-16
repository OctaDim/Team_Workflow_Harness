# Evaluation

Requires Node + trusted ordinary installed plugin-eval JS entry in entry;
check ancestors. Reject symlinks/shell shims; never resolve to bypass rejection.
Set skill_dir to selected root:

```sh
node harness/common/scripts/plugin_eval_without_human.mjs "$entry" start "$skill_dir" --format json
```

Then analyze. Target a skill folder or bounded generic directory for plain
instructions, not single Markdown. Review structural/budget/code findings,
JSON improvementBrief/compare. Save stdout outside target; no --output,
--brief-out/benchmark writes, external metric-packs or author-home/cache paths.
Human-filter rejects nested/alias README.human.md reads before content/cost;
source/tool unchanged. Checks inputs/ancestors and whole harness tree;
interpreter/analyzer code stay trusted. API filter, not OS/concurrent-substitution
isolation. After updates rerun via project venv Python:
harness/common/testing/tests/test_plugin_eval_without_human.py.
