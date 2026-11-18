# Evaluation

Check Node, trusted ordinary JS entry and ancestors. Reject symlinks/shims
without resolving. From root:

```sh
node harness/common/scripts/plugin_eval_without_human.mjs "$entry" start "$skill_dir" --format json
```

Then analyze a skill or bounded instruction folder. Save stdout outside it.
No tool writes, external metric packs or author-home/cache paths. The API
filter blocks nested/alias README.human.md reads and checks paths/tree.
Trust interpreter/analyzer. No OS/race isolation. After filter edits run
`harness/common/testing/tests/test_plugin_eval_without_human.py` in the venv.

Review all findings, even A, and JSON improvementBrief/compare. Fix errors
and requirements. Try minimal edits for applicable warnings (e.g. “Use when…”
with triggers intact). First rerun static Plugin-eval and compare each trial.
Revert failed edits; explain residual findings. Check if real code tests can
produce coverage. Markdown-only: N/A. Assess and address other info as needed.

Repeat final mandatory checks. Description edits require relevant discovery
and unrelated non-loading. Report fixes, remaining findings, reasons and checks.
Follow publication gate.
