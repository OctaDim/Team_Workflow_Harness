# Дополнение скилла: предложение uv-подготовки при запуске

Создано: 2026-10-16T12:02:02+03:00, Europe/Minsk.
Основание: дополнение пользователя и выбор маршрута 1 в side conversation.
Заявка: `harness/common/inbox/2026-10-16-application-startup-readiness/request.md`.
Предыдущий отчёт: [validation.md](validation.md); результаты v1 не изменены.

## Версия и область

Изменён только кандидат `comm-verify-application-startup/SKILL.md` в заявке:
предлагать автоматическую проверку и uv-установку отсутствующих Python-зависимостей
в выбранном пользователем стартовом файле, реализовывать после согласия.
Существующие ограничения зависимостей, версий, окружения и полномочий сохраняются.
Соседние формулировки сокращены без изменения исходных контрактов.
Правила, опубликованные инструкции, приложение и старые свидетельства не менялись.

SHA-256 финального скилла: `5e07e5d9a20bc3b7e4fcb68424d0db1d425009f703022c6dc425d6a00ba4a704`.
Тело: 199 слов; статические trigger/invoke/deferred: 40/468/0 estimated tokens.
Суммарная статическая доступность: 508 estimated tokens, без дополнительных ресурсов.
Это не расход токенов и не измерение реальных чтений агента.

## Проверки

Quick_validate системного skill-creator через python3: passed.
Plugin-eval 0.1.0, установленный entry plugin-eval 0.1.2, через human-filter:
start и analyze passed; A/100, warn/fail/error = 0.
Исходные результаты команд: `v2-uv-proposal-compact-quick-validate.json`,
`v2-uv-proposal-compact-start.json`, `v2-uv-proposal-compact-analyze.json`.
Предыдущие попытки с warning invoke-budget сохранены отдельно под префиксами
`v2-uv-proposal-` и `v2-uv-proposal-final-`; пороги не менялись.
Объём сократился с 515 до 468 estimated invoke tokens, без переноса условий в ресурсы.
Проверки полного приложения не применимы: изменён текст кандидата, не код запуска.

## Непроверенные условия

Codex common-only: native discovery/loading/behavior v2 — not run.
Codex common+project: native discovery/loading/behavior v2 — not run.
Claude common-only: native discovery/loading/behavior v2 — not run.
Claude common+project: native discovery/loading/behavior v2 — not run.
Установочные проверки текущей v2, реальные сопоставимые чтения и RED/GREEN поведения
не выполнялись в этом узком дополнении; субагенты не запускались.
Ограничения авторизации Claude из v1 не проверялись заново.

Общий статус v2: не проверено. Публикация не выполнялась и отдельно не разрешена.
Оставшаяся стадия — обязательная валидация текущей версии и публикация с применимыми
согласованиями; дополнение кандидата завершено, вся заявка остаётся in progress.
