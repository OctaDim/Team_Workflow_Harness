# Дополнение к подготовке группы 5

Дата создания: 2026-11-14. Время: 2026-11-14T12:32:12.477617+03:00.
Оригинал: [2026-11-14-group5-preparation-report.md](2026-11-14-group5-preparation-report.md).

Завершающая редакционная сверка выявила неявное переиспользование имени recovery-ветки.
В modes.md добавлена точная when-read ссылка на ресурс naming.md владельца
comm-create-git-branch; восстановление по явно согласованному SHA остаётся отдельной
процедурой, не самостоятельной feature-веткой от произвольного старого HEAD.
Логика именования не продублирована, scope Git/PR-разрешений не расширен.
Для будущего исполнения заявки 7 уточнён prerequisite 4.

Изменён только текущий неопубликованный кандидат recovery. Старые снимки,
финальные stdout/register, отчёт и integrity не перезаписаны. Повторён только
explain-budget изменённого кандидата, остальные семь не переоценивались.
Recovery: слова SKILL=184, Unicode=1529,
stock SKILL=383, trigger=41,
deferred=294 (moderate),
total=718 (moderate).

Актуальные данные всех восьми:
[2026-11-14-latest-budget-register.json](2026-11-14-latest-budget-register.json).
Raw recovery: [stdout](final-budget-recovery-v2/candidate-comm-recover-git-state.stdout.json).
Это static preparation, не formal/native/behavior validation.
