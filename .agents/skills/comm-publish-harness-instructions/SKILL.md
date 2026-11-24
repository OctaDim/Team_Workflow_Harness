---
name: comm-publish-harness-instructions
description: Use when publishing or restoring a prepared skill or rule version to canonical sources and native installation copies.
---

# Publish an authorized version

Identify full candidate, exact version/source/native scope, current reports and
stage permissions. Перед переносом прочитай файл `harness/common/skills/comm-publish-harness-instructions/references/gate.md` и перед сверкой размещения и копий прочитай файл `harness/common/skills/comm-publish-harness-instructions/references/placement-contract.md`.

1. Reconcile current mandatory checks and authorization. Changes reset status;
   outdated/missing/failed checks cannot borrow earlier success. Для обязательной проверки прочитай файл `harness/common/skills/comm-validate-harness-instructions/SKILL.md`. Проектирование к этой стадии не относится.
2. Report pass, observed failure or missing check per client and installation mode. Only missing checks may receive an explicit version-specific release exception. Resolve uncovered gaps before copying; preserve real
   statuses and scoped approvals. Other exceptions do not transfer.
3. Publish approved files into canonical sources first. Synchronize working copies from those sources as one approved set. Stop on
   a differing other-owner file; verify full sets/bytes/types/Git visibility,
   the ENTIRE installed canonical rule set, links and native integration.
4. Preserve permanent report/evidence independently of inbox; update the request.

Done: authorized current source/native version and truthful checks/statuses;
equality is not native proof. A candidate alone is not required publication.
Protected entrypoints and personal/canonical boundaries remain mandatory.
