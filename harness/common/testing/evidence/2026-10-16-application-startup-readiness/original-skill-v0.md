---
name: comm-verify-application-startup
description: Use when finishing changes affecting entrypoints, configuration loading, external services or resources, or before claiming an application is ready for ordinary startup.
---

# Verify ordinary startup

Inputs: authorized scope, target installation, user command, configuration sources,
required services/resources and test setup. Existing configuration, dependency,
permission and evidence procedures retain ownership.

1. Identify the supported user command, working directory, configuration precedence
   and required resources. Inspect loaders and test launch setup; do not print secrets.
2. Compare ordinary startup with test environment variables, fixtures, temporary files,
   arguments and services. Identify missing working inputs; differences alone are
   not defects. Never copy temporary databases, ports or test credentials blindly.
3. Complete preparation already authorized using known working values and supported
   configuration sources. Missing data/authority: identify the exact gap; do not
   invent secrets, download resources or expand installation changes.
4. Run the user command with its supported working configuration, without hidden
   test assistance, when authorized. Verify readiness of the affected function;
   process creation alone is insufficient. Respect production/cost limits and
   stop only processes owned by this check.
5. Report separately: tests, working configuration, ordinary startup/function check,
   exact command and remaining gaps. An unavailable check stays unverified;
   tests do not upgrade that status. Reuse still-valid evidence; unrelated changes
   do not trigger expensive model suites.

Done: supported startup verified in the agreed installation, or concrete missing
inputs/permissions and unverified behavior reported without a readiness claim.
