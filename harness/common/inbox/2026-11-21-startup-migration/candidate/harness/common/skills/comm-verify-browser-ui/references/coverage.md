# Browser coverage

Use project support commitments and affected risks with the existing general
scope owner; do not invent a universal browser/device matrix.

Consider relevant engines/platforms/input modes; width AND height, responsive
transitions and orientations; supported themes and states such as open overlays,
long content, loading, refusal and restoration. Choose necessary combinations,
preserve mandatory checks, not every possible Cartesian combination. Actual
state verification belongs to comm-prepare-browser-check.

Identify actual browser/version/platform, sizes/states, real devices versus
emulation, and unverified support. Missing support requirements block broad
compatibility claims, not independent authorized checks. Distinguish application
behavior from observed platform-controlled interfaces.
