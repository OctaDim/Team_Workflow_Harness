# Route menu

До выбора используй только запрос, контекст и описания. Пп. 1–3 дословно:

1. **Superpowers + Compound Engineering:** `superpowers:using-superpowers + compound-engineering:ce-brainstorm → compound-engineering:ce-plan → compound-engineering:ce-work` - одновременное выполнение `superpowers:using-superpowers и ce-`этапов
2. **Compound Engineering:**  `compound-engineering:ce-brainstorm → compound-engineering:ce-plan → compound-engineering:ce-work`  - нативный ce-маршрут
3. Без специального маршрута: текущая модель c effort самостоятельно выполняет задачу.

Рекомендуй маршрут, связав главный риск с этапом или проверкой. Учти известные предпочтения. Порядок вопросов сам по себе маршрут не определяет. Если важна запись решений, проверь соглашения в `decisions/` пакета задачи. При неизвестном решающем предпочтении покажи варианты условно и спроси о предпочтении.
Ведущий смешанного маршрута применяет superpowers:using-superpowers перед цепочкой CE и соблюдает согласования CE. Делегируй только на подходящем этапе при доступности и разрешении. Субагент пропускает superpowers:using-superpowers. Самостоятельно — та же модель и effort без делегирования и цепочек.

Покажи все рекомендации, короткую рядом с CE. При неясной применимости назови пробелы, покажи все варианты условно без рекомендации. Пункты дословно, меняй номера:

1. Обязательного плагина нет: **эксперимент → исследование → выводы**. Инструменты выбираются под согласованный эксперимент.
2. **Superpowers**, скилл `superpowers:brainstorming`: **короткий дизайн → согласование → реализация и проверка.**
3. **Superpowers**, скилл `superpowers:systematic-debugging`: **Диагностика → первопричина → исправление и проверка.**

Согласуй эксперимент, добавь применимые короткие маршруты. Нет имени в каталоге — «доступность не проверена». Недоступность требует свидетельства. Оба полных пункта дословно, меняй номера:

1. **Superpowers, через одного агента:** `superpowers:brainstorming → superpowers:writing-plans → superpowers:executing-plans`.
2. Superpowers, через субагентов: `superpowers:brainstorming → superpowers:writing-plans → superpowers:subagent-driven-development`.

После списка дословно:

Оба полных варианта включают: superpowers:using-superpowers → superpowers:brainstorming →
согласование спецификации → superpowers:writing-plans → согласование плана с сохранением
выбранного исполнителя → выбранное исполнение → его проверки и review →
superpowers:verification-before-completion → superpowers:finishing-a-development-branch.
Разрешения при выборе исполнителя остаются отдельными.

Затем дословно:

```markdown
> **Самостоятельная реализация не означает полного отсутствия субагентов**.
> В `superpowers:executing-plans` основной агент пишет весь код сам, но скилл предусматривает
> отдельного субагента для итогового ревью, когда он доступен.
> В `superpowers:subagent-driven-development` отдельные исполнители и ревьюеры участвуют
> в каждой задаче плана.
```

Цепочку и исполнителя выбирает пользователь. Короткий маршрут ограничен своими этапами. Сверь шаблоны, включая п. 1.
