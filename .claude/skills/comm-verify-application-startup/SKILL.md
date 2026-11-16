---
name: comm-verify-application-startup
description: Use when finishing changes to entrypoints, configuration, services or resources, or before claiming ordinary startup readiness.
---

# Verify ordinary startup

Inputs: authorized scope, installation/command, configuration/resources and tests.
Existing configuration/dependency/permission/evidence procedures retain ownership.

1. Identify command, cwd, configuration precedence and resources;
   inspect loaders/tests without exposing secrets.
2. Compare ordinary startup with test variables, fixtures, temporary files, arguments
   and services. Identify missing inputs; differences alone are not defects.
   Never blindly copy temporary databases, ports or credentials.
3. Complete authorized preparation with known values/supported sources.
   Missing data/authority: report the exact gap; invent/download nothing,
   and do not expand installation scope.
4. Offer automatic checks/uv installation of missing Python dependencies in a
   user-chosen startup file (main.py or another).
   Propose checks before application imports, locked versions/isolated environments,
   rechecking after installation, and stopping on failure.
   Stop and wait for an explicit user decision. Implement only if approved;
   honor prior approval/refusal.
5. Run the user command when authorized; verify the affected function.
   Process creation alone is insufficient. Respect production/cost limits;
   stop only processes owned by this check.
6. Report tests, working configuration and ordinary startup/function results separately,
   with commands and remaining gaps. Unavailable checks stay unverified.
   Reuse valid evidence; unrelated changes do not trigger expensive model suites.

Done: startup/function verified in the agreed installation, or concrete missing
inputs/permissions and unverified behavior reported without claiming readiness.
