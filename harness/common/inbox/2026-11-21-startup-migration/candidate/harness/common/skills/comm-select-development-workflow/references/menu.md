# Route menu

Меню, рекомендацию и вопрос дай на языке запроса. Для русского вставь блок ниже дословно от «1.» до последней строки цитаты. Сохрани каждый символ, включая двойные пробелы и переносы. Рекомендации и вопрос добавь вне блока. Для английского переведи только прозу: пункты 1–8 по порядку, затем оба пояснения. В каждом пункте и пояснении копируй каждое имя `плагин:скилл` целиком с префиксом. Сверь с образцом перед ответом.

До выбора используй запрос, контекст и описания. Поясни этапы и основания всех рекомендаций, короткую укажи рядом с CE. Если данных мало, перечисли пробелы и представь все маршруты условно, без рекомендации. Согласуй эксперимент. Добавляй применимые короткие маршруты. Отсутствие имени в каталоге оставляет доступность непроверенной. Для вывода о недоступности нужно отдельное свидетельство.

В смешанном маршруте ведущий применяет superpowers:using-superpowers перед CE и соблюдает согласования CE. Делегирование требует подходящего этапа, доступности и разрешения. Субагент пропускает superpowers:using-superpowers. Самостоятельный маршрут сохраняет модель и effort, без делегирования и цепочек. Короткий маршрут ограничен своими этапами. Выбор цепочки и исполнителя остаётся за пользователем.

```markdown
1. **Superpowers + Compound Engineering:** `superpowers:using-superpowers + compound-engineering:ce-brainstorm → compound-engineering:ce-plan → compound-engineering:ce-work` - одновременное выполнение `superpowers:using-superpowers и ce-`этапов
2. **Compound Engineering:**  `compound-engineering:ce-brainstorm → compound-engineering:ce-plan → compound-engineering:ce-work`  - нативный ce-маршрут
3. Без специального маршрута: текущая модель c effort самостоятельно выполняет задачу.
4. Обязательного плагина нет: **эксперимент → исследование → выводы**. Инструменты выбираются под согласованный эксперимент.
5. **Superpowers**, скилл `superpowers:brainstorming`: **короткий дизайн → согласование → реализация и проверка.**
6. **Superpowers**, скилл `superpowers:systematic-debugging`: **Диагностика → первопричина → исправление и проверка.**
7. **Superpowers, через одного агента:** `superpowers:brainstorming → superpowers:writing-plans → superpowers:executing-plans`.
8. Superpowers, через субагентов: `superpowers:brainstorming → superpowers:writing-plans → superpowers:subagent-driven-development`.

Оба полных варианта включают: superpowers:using-superpowers → superpowers:brainstorming →
согласование спецификации → superpowers:writing-plans → согласование плана с сохранением
выбранного исполнителя → выбранное исполнение → его проверки и review →
superpowers:verification-before-completion → superpowers:finishing-a-development-branch.
Разрешения при выборе исполнителя остаются отдельными.

> **Самостоятельная реализация не означает полного отсутствия субагентов**.
> В `superpowers:executing-plans` основной агент пишет весь код сам, но скилл предусматривает
> отдельного субагента для итогового ревью, когда он доступен.
> В `superpowers:subagent-driven-development` отдельные исполнители и ревьюеры участвуют
> в каждой задаче плана.
```
