# Route menu

До выбора используй запрос, контекст и описания. Описания не заменяют процедуры; не открывай их для меню. Начни с 1, копируй пп. 1–3 дословно:

1. **Superpowers + Compound Engineering:** `superpowers:using-superpowers + compound-engineering:ce-brainstorm → compound-engineering:ce-plan → compound-engineering:ce-work` - одновременное выполнение `superpowers:using-superpowers и ce-`этапов
2. **Compound Engineering:**  `compound-engineering:ce-brainstorm → compound-engineering:ce-plan → compound-engineering:ce-work`  - нативный ce-маршрут
3. Без специального маршрута: текущая модель c effort самостоятельно выполняет задачу.

После списка поясни этапы и основания рекомендаций. В смешанном маршруте ведущий применяет superpowers:using-superpowers перед CE и соблюдает согласования CE. CE следует своей цепочке. Делегирование требует подходящего этапа, доступности и разрешения; субагент пропускает superpowers:using-superpowers.
Самостоятельно — та же модель и effort, без делегирования и цепочек.

Покажи все рекомендации, короткую рядом с CE. При неясной применимости укажи недостающие данные/скиллы и покажи все короткие и полные варианты условно без рекомендации. Короткие пункты копируй посимвольно по порядку, меняя только номера:

1. Обязательного плагина нет: **эксперимент → исследование → выводы**. Инструменты выбираются под согласованный эксперимент.
2. **Superpowers**, скилл `superpowers:brainstorming`: **короткий дизайн → согласование → реализация и проверка.**
3. **Superpowers**, скилл `superpowers:systematic-debugging`: **Диагностика → первопричина → исправление и проверка.**

Эксперимент требует согласования. Добавь другие применимые короткие маршруты, отметь недоступные скиллы. Заверши обоими полными пунктами дословно, меняя только номера:

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

superpowers:using-superpowers и superpowers:brainstorming оставляют выбор цепочки/исполнителя пользователю. Короткий маршрут ограничен своими этапами.

Сверь все шаблоны, включая «одновременное выполнение» в п. 1.
