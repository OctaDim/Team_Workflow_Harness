# Tests

Python 3.9+, uv; reuse .venv. From the confirmed root:

```sh
uv venv .venv
uv pip sync --python .venv/bin/python harness/common/testing/requirements.lock
```

Full-run alternatives: `.venv/bin/python -m pytest .` or
`.venv/bin/python harness/common/scripts/run_tests.py`.
Collect all recognized project tests recursively, not just harness.
Exclude only the two trees with `--ignore=harness/common/inbox` and
`--ignore=harness/project/inbox`; retain standard service/venv exclusions.
Active before/candidate/source names elsewhere are not exclusions; extra active
exclusions need a reason. Runner must not enumerate historical editions.

Use a checked FILE/DIR for a target, without adding the root. Explicit inbox
targets remain available; check pytest version/hooks. Mixed root+target may
include neighboring editions: report actual scope, no full/exclusion guarantee.
pytest uses one config, not nested configs; use checked `-c CONFIG TARGET`
when needed, accounting for cwd/rootdir.

Use the common pytest.ini template only without an active config.
Otherwise merge root scope, both ignores and needed import mode into its format;
preserve patterns, markers, plugins/options and project. Never shadow it with
pytest.ini. Common needs no plugins; autoload diagnostics must not mask required app plugins.

Report command/scope/completion/exit/gaps. Empty/collect-only is not a pass;
target success is not full success. Startup needs no test dependencies.
Для проверки зависимостей и покрытия прочитай файл `harness/common/docs/2026-10-06-run-tests.md`.
