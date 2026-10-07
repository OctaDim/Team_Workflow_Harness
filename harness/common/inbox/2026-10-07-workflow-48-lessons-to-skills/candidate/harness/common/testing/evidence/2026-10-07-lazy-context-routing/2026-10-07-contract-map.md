# Карта сохранения требований

Дата: 2026-10-07. Это проверяемая карта миграции, не новый источник политики.

| Исходное требование | Постоянная граница | Процедура/ресурс после разделения |
|---|---|---|
| Порядок/закрытие inbox, молчание, технические поправки | ownership: до действия открыть inbox, соблюдать последовательность | inbox SKILL + workflow; существующее решение о статусах |
| Разрешения создания/выполнения/публикации, прямое исключение | ownership: отдельные стадии, явный подтверждённый bypass | inbox workflow, author validation |
| Пять полей контекста, датированная папка, статусы | ownership: обязательная процедура до записи | inbox workflow |
| Полный кандидат/ресурсы, временный inbox, постоянная память | ownership: путь через inbox | inbox workflow + author validation |
| Блокировка: действие/причина/источник/получатель/разрешение | ownership: остановка зависимых действий | inbox workflow + существующий урок |
| skill-creator/внешние инструменты, установка ≠ проверка | ownership: обязательные текущие проверки | author validation |
| Два агента/два режима, правка сбрасывает статусы, исключение версии | ownership: gate до публикации | author validation + placement |
| Канонические префиксы, обычные source/native копии, Git | ownership: применимый canonical приоритет | author placement + существующий контракт владения |
| RED/компактность/повтор проверок | ownership: выбирать lazy-first | author content + validation + compact-authoring |
| Common обязателен, project зависит, нет project-only | package-independence | install SKILL + checks |
| Common-only создаёт нейтральный project; combined сохраняет байты | package-independence: без перезаписи project | install checks |
| Явный общий шаблон, отдельная заявка/решение/подтверждение пользы | package-independence: два подтверждения | install checks |
| Изоляция, идемпотентность, оба режима, стартовая стоимость | package-independence: открыть install перед переносом | install checks |
| Старый project-wrapper, стартовую команду не менять | entrypoint-links/user-owned | install checks + protected-entrypoints |
| Структура/даты/создание категорий | package-independence: ресурс до размещения | install checks + structure-and-creation-dates |
| README.human создавать/исключать, отдельные проверки | human-folder-guides: исключить до чтения/поиска | author validation + placement; существующие specs |
| Plugin-eval human-фильтр и отдельный Node.js процесс | human-folder-guides: применять исключение | author validation + plugin-eval-without-human |
| Защищённые входы, CLAUDE bridge, предупреждение, no hooks | user-owned/entrypoint-links | существующая диагностика protected-entrypoints |
| uv/нет fallback/сохранить ограничения/другие типы согласовать | dependencies-through-uv | короткое правило без нового скилла |

Контракты decisions/docs/specs сохранены; исторические отчёты не переписываются.
Постоянная граница остаётся до ошибочного действия; детали читаются после
распознавания задачи. Успех структурной проверки не означает нативный успех.
