# Подробная оценка трёх существующих скиллов

Дата создания отчёта: 2026-10-07. Исходные оценки получены 2026-10-07, 21:11 UTC (23:11 Europe/Berlin).

Это статические оценки установленного plugin-eval, а не измеренный расход сессии. Анализатор оценивает каждый файл как ceil(число UTF-16 code units / 4); суммы составлены из готовых компонентов JSON. README.human.md исключены до чтения.

Все три категории анализатора — `skill`. Порог ресурсов deferred — 1200; generic-порог 1600 к этим трём результатам не применяется. SKILL.md читается при вызове скилла; строка не измеряет весь обязательный стартовый контекст.

Каждая строка включает SKILL.md, только указанный reference и все Texts. Остальные references в неё не входят. Строки нельзя складывать: SKILL.md и Texts повторяются.

Категория в скобках оценивает сумму строки по заданной пользователем шкале:
`good` — небольшой объём ≤180; `moderate` — умеренный 181–520;
`heavy-warn` — большой 521–1200, warn; `excessive-fail` — чрезмерный >1200, fail.
Эти дополнительные категории не меняют штатные checks/bands plugin-eval
и не являются статусами проверки агента.

## Обработка inbox

Источник: `harness/common/skills/comm-process-harness-inbox`.

plugin-eval 0.1.0 (версия из JSON); метод `estimated-static`. Оценка **86/B**, riskLevel=high.

| Показатель | Tokens | Band |
|---|---:|---|
| Discovery: name/description | 44 | good |
| SKILL.md | 439 | moderate |
| Ресурсы скилла | 1922 | excessive |
| Сумма всех бюджетов | 2405 | excessive |

Порог deferred heavyMax=1200; превышение 722. Фактические пороги goodMax/moderateMax/heavyMax: 180/520/1200.

```text
SKILL.md=439/references/experience-routing.md=526 /Texts=0 --> 965 (heavy-warn)
SKILL.md=439/references/workflow.md=1396 /Texts=0 --> 1835 (excessive-fail)
```

Texts=0 (других учитываемых текстовых файлов нет).

Ресурсы: 526 + 1396 = 1922.

Исходные checks: `deferred_cost_tokens-budget-high` — **fail**, категория budget; `coverage-artifacts-unavailable` — info, категория coverage. Рекомендация плагина: уменьшить повторяющийся текст инструкций и вынести подробности в отложенные supporting files. Эта рекомендация сохранена; простое разбиение references само по себе не уменьшает сумму deferred.

[Полный исходный JSON: категории, бюджеты, thresholds, findings и рекомендации](2026-10-07-comm-process-harness-inbox-analyze.json).

## Авторство правил и скиллов

Источник: `harness/common/skills/comm-create-lazy-claude-codex-skills`.

plugin-eval 0.1.0 (версия из JSON); метод `estimated-static`. Оценка **86/B**, riskLevel=high.

| Показатель | Tokens | Band |
|---|---:|---|
| Discovery: name/description | 46 | good |
| SKILL.md | 464 | moderate |
| Ресурсы скилла | 2294 | excessive |
| Сумма всех бюджетов | 2804 | excessive |

Порог deferred heavyMax=1200; превышение 1094. Фактические пороги goodMax/moderateMax/heavyMax: 180/520/1200.

```text
SKILL.md=464/references/content-contract.md=387 /Texts=0 --> 851 (heavy-warn)
SKILL.md=464/references/evaluation.md=683 /Texts=0 --> 1147 (heavy-warn)
SKILL.md=464/references/placement-contract.md=425 /Texts=0 --> 889 (heavy-warn)
SKILL.md=464/references/validation-and-publication.md=799 /Texts=0 --> 1263 (excessive-fail)
```

Texts=0 (других учитываемых текстовых файлов нет).

Ресурсы: 387 + 683 + 425 + 799 = 2294.

Исходные checks: `deferred_cost_tokens-budget-high` — **fail**, категория budget; `coverage-artifacts-unavailable` — info, категория coverage. Рекомендация плагина: уменьшить повторяющийся текст инструкций и вынести подробности в отложенные supporting files. Эта рекомендация сохранена; простое разбиение references само по себе не уменьшает сумму deferred.

[Полный исходный JSON: категории, бюджеты, thresholds, findings и рекомендации](2026-10-07-comm-create-lazy-claude-codex-skills-analyze.json).

## Установка harness

Источник: `harness/common/skills/comm-install-harness`.

plugin-eval 0.1.0 (версия из JSON); метод `estimated-static`. Оценка **86/B**, riskLevel=high.

| Показатель | Tokens | Band |
|---|---:|---|
| Discovery: name/description | 41 | good |
| SKILL.md | 291 | moderate |
| Ресурсы скилла | 2750 | excessive |
| Сумма всех бюджетов | 3082 | excessive |

Порог deferred heavyMax=1200; превышение 1550. Фактические пороги goodMax/moderateMax/heavyMax: 180/520/1200.

```text
SKILL.md=291/references/checks.md=795 /Texts=0 --> 1086 (heavy-warn)
SKILL.md=291/references/entrypoints.md=1121 /Texts=0 --> 1412 (excessive-fail)
SKILL.md=291/references/material-placement.md=521 /Texts=0 --> 812 (heavy-warn)
SKILL.md=291/references/testing.md=313 /Texts=0 --> 604 (heavy-warn)
```

Texts=0 (других учитываемых текстовых файлов нет).

Ресурсы: 795 + 1121 + 521 + 313 = 2750.

Исходные checks: `deferred_cost_tokens-budget-high` — **fail**, категория budget; `coverage-artifacts-unavailable` — info, категория coverage. Рекомендация плагина: уменьшить повторяющийся текст инструкций и вынести подробности в отложенные supporting files. Эта рекомендация сохранена; простое разбиение references само по себе не уменьшает сумму deferred.

[Полный исходный JSON: категории, бюджеты, thresholds, findings и рекомендации](2026-10-07-comm-install-harness-analyze.json).

## Интерпретация

Наибольшие references: inbox/workflow.md=1396; install/entrypoints.md=1121; create/validation-and-publication.md=799; install/checks.md=795. Это места для предметного поиска повторов или условного разделения. Размер не доказывает избыточность: обязательные согласования, остановки и проверки должны сохраниться. Сжатие или изменение этих скиллов не выполнялось.

Наличие большого deferred при небольших отдельных строках означает большой полный набор ресурсов. Ни строки, ни общий статический бюджет не устанавливают, какие файлы реально читаются в одном сценарии. Для этого нужна отдельная проверка поведения/измерение usage. Эти read-only расчёты не проверяют новый кандидат и не меняют статусы его проверки.

Команды для каждого указанного name из корня проекта (stdout вне оцениваемой папки):

```sh
plugin_eval_entry=$(command -v plugin-eval) || exit 1
node harness/common/scripts/plugin_eval_without_human.mjs "$plugin_eval_entry" analyze harness/common/skills/<name> --format json
```
