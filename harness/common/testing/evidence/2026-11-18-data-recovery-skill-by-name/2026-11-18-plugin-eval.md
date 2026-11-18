# Plugin-eval для поиска скилла выкладки по имени

Дата — 2026-11-18. [Версия 1](../2026-11-18-execute-data-recovery/2026-11-18-report.md) получила B (86) и broken-relative-links в отдельной папке INBOX. [Версия 2](v2-analyze.json) с указанием имени получила A (100).

В [версии 3](../../../inbox/2026-11-18-04-data-recovery/candidate-v3/comm-restore-application-data/SKILL.md) сохранено указание найти и прочитать установленный comm-manage-production-rollout, применить его процедуру подтверждения и остановиться перед изменением production, если скилл недоступен. SHA-256 SKILL.md — `f667390f680e92b5daf06f8b4afe876665c5c08be869e8a0cce43614f8e4805e`.

Plugin-eval 0.1.2 через фильтр plugin_eval_without_human.mjs выполнил [start](v3-start.json) и [analyze](v3-analyze.json). Результат версии 3 — A (100), предупреждений и ошибок нет. Статическая оценка полного объёма — 392 токена. Нативные проверки версии 3 ещё не проводились.
