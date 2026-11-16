# Local model lifecycle candidate v1

Created: 2026-10-16. State: final report for candidate preparation and checks;
canonical publication remains pending. Overall status: **unverified**.

## Exact artifact and scope

Candidate: `harness/common/inbox/2026-10-16-local-models/candidate/comm-manage-local-models/`.
Immutable version hashes and full permanent snapshot: [version-v1.json](version-v1.json)
and `candidate-v1/comm-manage-local-models/`.
Both machine files stayed unchanged throughout candidate validation.
The entrypoint body contains 128 words; one lifecycle reference holds conditional detail.

The skill owns model artifact storage, identity, preparation and coordinated
replacement. It reuses existing owners for configuration/Git visibility and
ordinary startup readiness. No new always-loaded rule, protected entrypoint,
shared project skeleton, active service configuration or model file was changed.
`rag/local_models/.gitignore` was created and added to the Git index; the
existing model files were not transferred.

## Results

| Check | Result | Evidence/limits |
|---|---|---|
| skill-creator quick_validate | passed | `quick-validate-v1.json` |
| plugin-eval start and analyze | A, 95/100; no fail/error | `plugin-start-v1.json`, `plugin-analyze-v1.json` |
| Own reference path / loading | passed | Explicit and implicit native runs read lifecycle.md in both modes |
| Main common test suite | 168 passed in 30.47s | `.venv/bin/python -m pytest harness/common/testing/tests -q`, exit 0 |
| Root entrypoint check | passed | `python3 -B harness/common/checks/ensure_entrypoint_links.py`, exit 0 |
| Model/scaffold Git visibility | passed, seven representative paths | `structural-v1.json`; nested files and companion JSON excluded |
| Actual scaffold tracking | passed | `git-staging-v1.json`; only rag/local_models/.gitignore staged |
| Staged whitespace | passed | `git diff --cached --check`, exit 0 |
| Candidate/snapshot hashes | passed | `version-v1.json` independently recomputed after native checks |

Plugin-eval reports one static budget warning: lifecycle.md is estimated at
858 deferred tokens, above its 520-token moderate baseline. This remains below
the common authoring resource target of 1000 and escalation threshold of 1200.
The reference retains the requested artifact identity, scaffold, startup,
embedding/OCR replacement and rollback contracts; no content was removed solely
to erase the warning. Metadata is estimated at 36 tokens and the full SKILL.md
at 337. There are no executable helpers inside the skill; coverage artifacts
are not applicable to this documentation-only candidate. Thresholds were unchanged.

## Native results

Tool: codex-cli 0.161.0, CLI default model, no model/effort override.
Each run used a temporary synthetic project and isolated runtime, with global
skills and the source checkout hidden. The native workspace-write sandbox stayed
enabled. All source/native fixture copies were ordinary complete files.
Common-only startup created a neutral project; combined startup preserved an
existing neutral sentinel project byte-for-byte. Repeated startup was unchanged.

| Agent | Mode | Explicit body/resource | Implicit selection/resource | Unrelated non-loading | Scoped status |
|---|---|---|---|---|---|
| Codex | common-only | passed | passed | passed | verified for these read-only scenarios |
| Codex | common+project | passed | passed | passed | verified for these read-only scenarios |
| Claude | common-only | not run | not run | not run | unverified |
| Claude | common+project | not run | not run | not run | unverified |

All six candidate runs completed with exit 0 and no file changes. Their final
responses were read: model identity, tracked scaffold, explicit preparation,
replacement tests, embedding/index compatibility and missing-input boundaries
were retained. This validates instruction behavior in the tested scenarios,
not actual model provisioning or runtime compatibility.

Two baseline runs were completed before writing the candidate. Both already
recommended pinned artifacts and safe lifecycle/reindexing practices; neither
specified how to retain the directory scaffold in Git. Candidate responses
provided the concrete tracked .gitignore recipe. This is a narrow observed
omission; broad causal improvement has not been demonstrated.

Command traces were reviewed for human-guide reads. One broad regex flag was
a false positive: `cat LAUNCH.md; rg --files ... -g '!README.human.md'` reads the
launch document and excludes human guides during listing. Its output contained
the launch document and filenames only. No human-guide body read was found.
This observation does not turn the instructions into a filesystem access barrier.

Full responses, commands, actual tool-output characters and API usage are in
[native-summary-v1.json](native-summary-v1.json) and the immutable native run JSONs.
Separate source metadata, available resources and dependency-inclusive actual
reads are in [measurements-v1.json](measurements-v1.json). Static estimates are
not API usage or billed cost; there is no agreed startup cap.

## Remaining work

No model downloads, transfer of current weights, production access, model quality
benchmarks, runtime replacement or data reindexing were performed. Those belong
to separately scoped application work. Claude behavior remains unverified;
the overall instruction status remains unverified.

The current exact v1 may be published only after explicit authorization and
confirmation of its unverified status. Future targets are
`harness/common/skills/comm-manage-local-models/`,
`.agents/skills/comm-manage-local-models/` and
`.claude/skills/comm-manage-local-models/`.
The source and installation copies have not been published. No commit was made:
the skill-creation task remains open pending that stage. Unrelated project docs
and pre-existing evidence were preserved.
