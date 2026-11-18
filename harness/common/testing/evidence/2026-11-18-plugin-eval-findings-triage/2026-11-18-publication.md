# Публикация инструкции по разбору замечаний Plugin-eval

Дата — 2026-11-18. Опубликована проверенная версия 2 ресурса
`references/evaluation.md` скилла `comm-validate-harness-instructions`.
SHA-256 ресурса —
`defa78b1ff25e047a0991e3fd151bac5750252dc5fa01d0c283ffcccb4920550`.

Каноническая папка находится в `harness/common/skills`. Сверены полные наборы,
байты и обычные типы файлов в ней и в нативных копиях `.agents/skills` и
`.claude/skills`. В Git отслеживаются все файлы трёх папок. Проверка
`ensure_entrypoint_links.py` прошла и подтвердила актуальные канонические
правила. Шесть тестов `test_rule_copies.py` и `test_skills_first_knowledge.py`
прошли после записи. [Оценка опубликованного ресурса](2026-11-18-published-plugin-eval.json) —
A (95), 1200 статических токенов условных ресурсов. [Нативный каталог Codex](2026-11-18-published-codex-catalogue.json)
вернул скилл по пути `.agents/skills`.

Codex прошёл сценарии в обоих режимах. Claude и общий статус версии —
**не проверено**. Публикация этой версии с указанным статусом согласована
отдельно. [Статические проверки](2026-11-18-report.md) ·
[Нативные сценарии](2026-11-18-native-verification-addendum.md)
