---
name: comm-manage-local-models
description: Use when preparing, provisioning, replacing or validating local inference model files and their reproducible deployment.
---

# Manage local model artifacts

Inputs: project root, model roles/sources, current profiles, configuration,
tests and authorized installation or replacement scope.

Перед подготовкой или заменой моделей, проектированием или проверкой их установки прочитай файл `harness/common/skills/comm-manage-local-models/references/lifecycle.md`.

Keep model files under project-root `rag/local_models/`, outside Python
environments. Track its scaffold; exclude downloaded contents. Keep the manifest,
preparation code, compatible profiles and tests outside that excluded subtree.

При изменении конфигурации или её видимости в Git прочитай файл `harness/common/skills/comm-separate-application-config/SKILL.md`.
Перед подтверждением готовности к обычному запуску прочитай файл `harness/common/skills/comm-verify-application-startup/SKILL.md`.

Result: a reproducible, integrity-checked model set bound to compatible code
and evidence, with explicit preparation and a tested replacement/rollback path.
Report Git visibility, manifest identity, actual checks and remaining gaps.
Missing source, revision, checksum, compatibility evidence or authorization
remains unresolved; this skill grants no download, migration or production access.
