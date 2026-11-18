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

## Skill findings

Review all errors, warnings and informational findings, including on grade A.
Fix errors and required findings within authorized scope. For each applicable
warning, try a minimal edit. For `description-trigger-weak`, try “Use when…”
while preserving every trigger. Re-run static Plugin-eval first after each
trial and compare findings. If a trial does not help, restore the working
revision and record the attempt and why the finding remains.

For executable code, check whether a real test run can produce a coverage
artifact. Record coverage as N/A for Markdown-only instructions. Assess other
informational findings for applicability and fix them when needed.

Repeat mandatory checks on the final revision. If the description changed,
verify intended discovery and unrelated non-loading. Report resolved and
remaining findings, reasons, and final check results. Follow the existing
publication procedure.
