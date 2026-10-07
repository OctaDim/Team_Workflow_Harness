# Evaluation

Requires Node + installed plugin-eval JS entry; resolve shell-shims, launcher
resolves entry symlinks. Set skill_dir to selected root before running:

```sh
entry=$(command -v plugin-eval) || exit 1
node harness/common/scripts/plugin_eval_without_human.mjs "$entry" start "$skill_dir" --format json
```

Then analyze. Own skill folder or bounded generic directory for
plain instructions, not single Markdown. Structural/budget/code findings,
JSON improvementBrief/compare. Save stdout outside target; no --output,
--brief-out/benchmark writes or external metric-packs. README.human.md filter rejects nested/alias reads before content/cost;
sources/tool unchanged. Avoid author-home/cache paths.
Promises API, not OS isolation. After updates rerun via .venv Python pytest:
harness/common/testing/tests/test_plugin_eval_without_human.py.
