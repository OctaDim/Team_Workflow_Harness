# Controlled sensitivity checks

Use only within authorized test scope.

1. Work in an isolated copy with the intended revision, configuration and data.
   Preserve bytes/EOL through existing text-preservation procedures. Never
   mutate a shared working tree automatically. If isolation is unavailable, report
   the obstacle and obtain an explicit decision before dependent work.
2. Run the selected baseline tests successfully. Establish meaningful assertions,
   target reachability and positive controls. Unrelated failures do not demonstrate sensitivity.
3. Verify intended target sites and expected match count before applying changes.
   Missing/stale/ambiguous anchors are invalid mutations, not survivors or kills.
   Check the mutation actually removes the named behavior and remains executable.
4. Independently establish that the runner executes the modified copy: inspect
   loaded paths/configuration or use a distinguishing probe. Prevent imports,
   caches or child-process settings from silently selecting the original. Preserve
   required environment settings without exposing secrets; hardcoded local paths
   are not portable isolation.
5. Run the same relevant tests on a stable copy; retain actual execution evidence,
   completion, exit code, stdout/stderr and target assertions. Summary words/nonzero exits alone are insufficient.
6. Classify each outcome. A valid detected mutation fails the expected behavioral
   check. Syntax/import/collection/environment errors, unapplied changes and
   unexecuted paths are invalid or inconclusive. Zero executed checks is no
   measurement. A survivor requires investigating test blindness, reachability
   and redundant protection before adding tests or removing safeguards.
7. Confirm original files remain unchanged. Clean up only owned temporary
   artifacts; preserve raw evidence through its existing authorized route.

Report mutation/target, baseline, selected tests, validity, actual execution,
expected/observed failure, result and limitations. Unresolved causality leaves the result unverified.
