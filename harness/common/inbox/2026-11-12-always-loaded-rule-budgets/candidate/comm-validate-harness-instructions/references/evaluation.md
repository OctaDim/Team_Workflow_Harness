# Evaluation

Requires Node + a trusted ordinary installed plugin-eval JS entry in entry.
Do not pass a symlink or resolve a shell shim to bypass rejection; verify the
chosen original entry and ancestors before use. Set skill_dir to selected root:

```sh
node harness/common/scripts/plugin_eval_without_human.mjs "$entry" start "$skill_dir" --format json
```

Then analyze. Own skill folder or bounded generic directory for
plain instructions, not single Markdown. Structural/budget/code findings,
JSON improvementBrief/compare. Save stdout outside target; no --output,
--brief-out/benchmark writes or external metric-packs. README.human.md filter rejects nested/alias reads before content/cost;
sources/tool unchanged. Avoid author-home/cache paths.
Promises API, not OS isolation or protection against concurrent path substitution.
The launcher rejects symlink inputs/ancestors and the whole working harness tree;
interpreter and installed analyzer code remain trusted execution dependencies. After updates rerun via .venv Python pytest:
harness/common/testing/tests/test_plugin_eval_without_human.py.
