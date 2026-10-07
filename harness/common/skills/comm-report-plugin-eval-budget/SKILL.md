---
name: comm-report-plugin-eval-budget
description: Use when plugin-eval deferred budgets exceed 1200 for skills or 1600 for directories, or per-reference token details are requested.
---

# Разбивка бюджета plugin-eval

Перед оценкой прочитай из корня проекта
`harness/common/skills/comm-create-lazy-claude-codex-skills/references/evaluation.md`.
Используй свежий JSON установленного plugin-eval через human-фильтр;
отчёт сохраняй вне оцениваемой папки. Новый tokenizer не нужен.

1. Покажи штатные target.kind/path, score/grade, findings, бюджеты,
   bands, фактические thresholds и рекомендации без изменений.
2. Добавляй детализацию автоматически при deferred >1200 для skill,
   >1600 для generic directory; равенство не превышение. Явный запрос
   работает ниже порога. Отличие baseline объясни, сохрани исходные checks/bands.
3. Для каждого скилла: S=invoke_cost_tokens.value (весь SKILL.md);
   Rᵢ=каждый deferred-компонент внутри references/, включая вложенные
   и несвязанные ссылками; T=все остальные учитываемые deferred-файлы
   (scripts/assets/config), кроме SKILL.md и всех references.
   README.human.md исключён до оценки; бинарные/неучитываемые файлы не добавляй.
4. Выведи строку с полным относительным путём каждого reference:
   `SKILL.md=150/references/example.md=350 /Texts=500 --> 1000 (heavy-warn)`.
   Сумма=S+один Rᵢ+T. Категория только одна:
   ≤180 good; 181–520 moderate; 521–1200 heavy-warn; >1200 excessive-fail.
   Это дополнительная шкала строки, не замена оценок/статусов анализатора.
5. Покажи Texts по файлам/tokens убыванию и полный deferred=sum(Rᵢ)+T.
   Другие references не включай в Texts/строку; строки не складывай.
   Без references: `SKILL.md=S/references=нет /Texts=T --> S+T (категория)`.
   Полностью известный пустой Texts: 0 с объяснением. Недоступные данные
   или несовпадение суммы — ошибка/недостающие данные, не ноль.
6. Generic: сохрани общий результат/1600-порог; каждый skill root оцени
   отдельно. Без скиллов — компоненты по файлам, SKILL.md=N/A,
   references не назначай. Внешние linked-файлы не локальные ресурсы.

Единицы — статическая оценка, не расход сессии/полный стартовый контекст.
Назови крупнейшие ресурсы для сжатия/разделения с сохранением поведения;
отчёт не разрешает правки и не повышает статусы.
