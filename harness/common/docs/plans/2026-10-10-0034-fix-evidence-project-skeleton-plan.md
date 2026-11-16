---
title: Evidence and neutral project skeleton - Plan
type: fix
date: 2026-10-10
artifact_contract: ce-unified-plan/v1
product_contract_source: inbox-requirements
origin: harness/common/inbox/2026-10-09-evidence-permissions-and-project-skeleton/request.md
execution: code
---
# Evidence and neutral project skeleton - Plan

## Goal Capsule

Objective: агенты сохраняют результаты порученной работы без лишней заявки, а история проверок и существующие материалы проекта остаются доступны.
Means: матрица прав в существующих владельцах и нейтральные ветки evidence в шаблоне (KTD1, KTD2).
Authority: требования исходной заявки и действующие канонические ограничения.
Stop conditions: изменение существующих данных вне указанного состава или конфликт назначения материала.

## Product Contract

### Summary

Рабочие отчёты размещаются в work/, проектные свидетельства механизма — в harness/.
Состояние отчёта и операция определяют допустимое изменение.
Шаблон создаёт обе ветки в новом project.

### Problem Frame

Общий запрет изменения evidence мешает сохранять результаты приложения.
Отсутствующие категории и завершённые отчёты требуют разных действий; создание пустого каркаса не восстанавливает историю.

### Requirements

**Evidence lifecycle**

- R1. Матрица операций исходной заявки обязательна для work и harness.
- R2. Исходные логи и снимки неизменны; новый прогон получает новый файл.
- R3. Завершение отчёта определяется завершением порученной работы и фактическим состоянием результата; неизвестное состояние требует уточнения.
- R4. Исправление завершённого отчёта создаёт датированное дополнение со ссылкой на оригинал.
- R5. Классификация учитывает назначение и потомков; work/ не снимает защиту смешанного материала.
- R6. Перенос, удаление и переименование требуют адресного состава и зависимых ссылок; доказанные даты создания сохраняются.

**Creation and compatibility**

- R7. Полностью отсутствующий project, в том числе после удаления, создаётся нейтрально с work/harness, человеческими пояснениями и INDEX.
- R8. Существующий project сохраняется побайтно при startup; удалённая история не восстанавливается.
- R9. Частичный каркас не дополняется startup автоматически; отсутствие START/INDEX даёт отказ до записи.
- R10. Установка, правила и ресурсы согласованы с матрицей; публикация не повышает статусы проверок.

### Scope Boundaries

Текущий проект получает только две отсутствующие пустые ветки и строки INDEX при адресной публикации.
Старые evidence остаются на прежних путях и классифицируются по назначению.
Перенос семи рабочих inbox-заявок — отдельная последующая работа.
Автоматическое дополнение частичного project не строится: существующий контракт сохранности достаточен; оно потребует отдельно адресного состава.
ACL/chmod, sandbox-настройки, новые hooks, роутер и замена Python-генератора не нужны.

## Planning Contract

- KTD1. Использовать comm-protect-harness-evidence как владельца lifecycle (R1–R6); раннее правило ownership ссылается на него, workflow и preservation согласуют размещение.
- KTD2. Добавить категории JSON в существующий генератор без нового алгоритма восстановления (R7–R9); Python уже создаёт nested human guides и INDEX и проверяет небезопасные пути до записи.
- KTD3. Публиковать новые пустые категории текущего project явно, проверяя хеши остальных файлов (R8, R10); прежние свидетельства остаются на месте.

### High-Level Technical Design

| Состояние project | Startup |
|---|---|
| Отсутствует целиком | Нейтральный шаблон, включая work/harness |
| Есть START/INDEX, категории частично отсутствуют | Сохранить существующие файлы и состав |
| Нет START либо INDEX | Ошибка, без создания/подмены project |
| Небезопасный путь либо повреждён шаблон | Ошибка до записи |

## Implementation Units

### U1. Align evidence owners

Goal: применить R1–R6, R10 без отдельного владельца поведения.
Dependencies: завершённая предыдущая публикация границ project inbox.
Files: harness/common/skills/comm-protect-harness-evidence/SKILL.md; harness/common/skills/comm-process-harness-inbox/references/workflow.md; harness/common/skills/comm-preserve-harness-knowledge/references/experience-routing.md; harness/common/skills/comm-preserve-harness-knowledge/references/material-placement.md; harness/common/rules/comm-skill-rule-ownership.md; полные соответствующие native skill folders и .claude rule.
Approach: применить KTD1, сохранить прежние gate и фактические статусы.
Test scenarios: native Codex в обоих режимах создаёт/дополняет текущий work-отчёт; исправляет завершённый только новым дополнением; не переписывает raw; останавливает неавторизованную запись механизма и mixed-parent cleanup.
Verification: текущие полные skill folders валидны, источники и native равны, сценарии имеют реальные наблюдения.

### U2. Extend the neutral template

Goal: выполнить R7–R9 и KTD2–KTD3.
Dependencies: U1.
Files: harness/common/base/project-skeleton.json; harness/common/testing/tests/test_ensure_entrypoint_links.py; harness/common/skills/comm-install-harness/references/checks.md; harness/common/specs/2026-10-06-structure-and-creation-dates.md; harness/common/decisions/2026-10-10-evidence-project-skeleton.md; harness/project/testing/evidence/work/README.human.md; harness/project/testing/evidence/harness/README.human.md; harness/project/INDEX.md; harness/common/INDEX.md.
Approach: сохранить существующий Python-контракт; шаблон нейтрален для любого приложения.
Execution note: сначала проверить, что прежний шаблон не создаёт новые ветки, затем использовать имеющийся генератор.
Test scenarios: отсутствие project и повторное создание после удаления дают одинаковый нейтральный состав без старой истории; combined и повторный startup сохраняют байты; частично отсутствующие категории не добавляются; отсутствие START/INDEX и unsafe/invalid-template отказ без порчи.
Verification: pytest конкретного startup-набора и полного основного набора, две изолированные установки и project-only отказ.

### U3. Publish one complete revision

Goal: завершить R10.
Dependencies: U1, U2.
Files: полные материалы текущей заявки; harness/common/testing/evidence/2026-10-10-evidence-permissions-project-skeleton/; источники/native из U1–U2.
Approach: публикация точного manifest и проверка сохранности прежних project bytes.
Test scenarios: повторная startup-проверка, source/native equality и отсутствие изменений старых evidence после публикации.
Verification: актуальный ce-code-review receipt, результаты native отдельно от структурных проверок, индивидуальный Execution заявки.

## Verification Contract

Тесты: harness/common/testing/tests/test_ensure_entrypoint_links.py и полный harness/common/testing/tests через pytest.
Quick_validate и plugin-eval start/analyze/compare применяются к каждому изменённому skill; generic анализ — к изменённым правилам.
Нативные проверки выполняют реальные операции в изолированных common-only/common+project fixtures.
Непроведённые/неуспешные проверки записываются как непроверенные.
Человеческие guide bodies не читаются как инструкции.

## Definition of Done

Все R1–R10 покрыты владельцем и проверкой либо явно указанным ограничением.
Постоянный результат доступен вне inbox, исходные ресурсы заявки сохранены.
Публикация одной ревизии имеет отдельный локальный коммит; экспериментальных изменений в production нет.
