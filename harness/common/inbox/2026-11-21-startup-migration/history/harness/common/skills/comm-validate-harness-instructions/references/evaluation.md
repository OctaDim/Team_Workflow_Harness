# Evaluation

Check Node and trusted ordinary JS entry/ancestors. Reject symlinks/shims before resolving. From root:

```sh
node harness/common/scripts/plugin_eval_without_human.mjs "$entry" start "$skill_dir" --format json
```

Analyze bounded targets. Save stdout elsewhere. Avoid tool writes, external packs and author paths. Trust the runtime and analyzer. The wrapper checks paths and blocks nested/alias human guides. It lacks OS/race isolation. Filter edits require venv test `harness/common/testing/tests/test_plugin_eval_without_human.py`.

Review findings and JSON improvementBrief/compare even at A. Fix errors/requirements. Try minimal warning fixes, preserving triggers. Compare static runs first and revert failed trials. Check real coverage when available (Markdown N/A). Assess info. Report fixes and residual reasons. Retest discovery and unrelated non-loading after description edits. Apply publication gate.
