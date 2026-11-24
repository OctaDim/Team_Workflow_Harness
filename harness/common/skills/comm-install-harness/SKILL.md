---
name: comm-install-harness
description: Use when installing or moving harness packages, changing their installation, or proposing changes to the shared project skeleton.
---

# Install the chosen package mode

Identify intended target and existing files; cwd is not proof. Перед установкой или правкой шаблона прочитай файл `harness/common/skills/comm-install-harness/references/checks.md`. Common is mandatory;
project-only is unsupported.

1. Choose common-only (create absent neutral project) or combined (preserve
   existing project byte-for-byte). Never replace/extend it from a changed template.
2. Establish authorized transfer scope/current instruction gate. На стадии публикации рабочих копий прочитай файл `harness/common/skills/comm-publish-harness-instructions/SKILL.md` только на этой стадии.
3. Install ordinary full sources/native copies and required resources; run the
   target-root startup check and two isolated-mode/negative checks.
4. Перед установкой или запуском тестов прочитай файл `harness/common/skills/comm-install-harness/references/testing.md`;
   preserve differing target configuration and use uv for Python dependencies.

Done: chosen mode works without source-project/global-author dependencies,
existing project preserved, repeat startup unchanged, resources/links and actual
agent/mode/version results recorded. Structural/copy equality is not native proof.
For startup warnings/errors select the separate diagnosis skill; use the agreed images for protected inputs and the portable common startup command. Template changes require the
separate request/decision/confirmation described in checks.
