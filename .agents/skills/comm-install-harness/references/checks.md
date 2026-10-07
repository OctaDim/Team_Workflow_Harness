# Installation contract

Identify the destination and existing files before copying. Common is portable
and independent of the old application/project; project requires common.

- Common-only: copy common; the common entrypoint check creates a missing
  project from `harness/common/base/project-skeleton.json`. It creates the
  agreed categories, neutral INDEX/START and human guides, never old work.
- Common+project: preserve existing project files byte-for-byte; do not replace
  it or add categories merely because the template changed. Missing/unsafe
  mandatory resources fail the check.
- Project-only is unsupported; refusal is a negative control, not a third mode.

Run `python3 -B harness/common/checks/ensure_entrypoint_links.py` from the target
root. It restores startup links and the recursive rules-reading instruction,
not publications/copies; notify before repairs. Keep an existing AGENTS startup
command. The old project check may delegate to common for compatibility; do
not create an independent implementation or add this wrapper to the neutral
template. Direct AGENTS/CLAUDE edits remain forbidden; no hooks/blocking or
machine-specific setup. For warning/error diagnosis read [entrypoints](entrypoints.md).

The shared template is explicit: never infer it from current project folders.
Changing its contents requires a separate common inbox request, a separate
explicit user decision and separate explicit confirmation of usefulness to all
projects. Await both; a proposal or silence supplies neither. New projects use
the approved revision; existing projects change only by an authorized migration.
Before placement read [material placement](material-placement.md):
keep agreed categories, creation dates and human guides; do not invent old dates.

Check two clean temporary installations with no source-project or global-author
access: neutral complete project creation; existing project hashes preserved;
repeated startup unchanged; damaged resources rejected; common absence refused
before writes. Verify links, resources, commands and ordinary native copies.
Do not duplicate common/project knowledge; stop conflicting actions for the user.

Measure startup separately for both modes: pointers/guards + skill metadata,
then only the selected body and necessary resources. Exclude human-guide bodies;
total package size is not startup cost. Structural success does not prove native
Codex/Claude behavior. Record each agent/mode/version, commands, results and
limits; changes reset prior instruction statuses and preserve publication gates.

New approved projects have no lessons category; plans remain docs/plans.
Existing legacy folders survive ordinary startup; remove them only through an
authorized addressed migration after requirement mapping and current checks.
