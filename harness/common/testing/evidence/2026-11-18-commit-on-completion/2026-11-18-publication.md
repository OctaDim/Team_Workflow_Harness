# Публикация правила о коммите при завершении работы

Дата — 2026-11-18. Опубликована версия 1
[канонического правила](../../../rules/comm-task-commit-on-completion.md)
и его [нативная копия](../../../../../.claude/rules/comm-task-commit-on-completion.md).
Оба файла обычные, побайтно совпадают и имеют SHA-256 `a15e372a37b16c7c440eaed5fcffae55e8b898155137d76fc836b65834893477`.

После публикации `python3 -B harness/common/checks/ensure_entrypoint_links.py`
подтвердил полный установленный комплект правил и целостность стартовых ссылок.
Полный прогон `python -B -m pytest -q -p no:cacheprovider .`
на pytest 8.4.2 завершился с кодом 0, прошли 195 тестов.

Codex проверен в common-only и common+project. Claude и итоговый статус
версии — **не проверено**. [Нативные сценарии и бюджет](2026-11-18-always-loaded-rule-v1.md).
