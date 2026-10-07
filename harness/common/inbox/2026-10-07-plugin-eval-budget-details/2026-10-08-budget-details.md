# Подробная оценка трёх существующих скиллов

Дата: 2026-10-08. Свежий analyze установленного plugin-eval с human-фильтром.
Статические оценки; не расход сессии и не полный стартовый контекст. Строка включает целый SKILL.md, один reference и все Texts. Строки не складываются.

## comm-process-harness-inbox

Категория: skill; score/grade: 86/B; riskLevel=high.

| Показатель | Tokens | Band | Пороги |
|---|---:|---|---|
| trigger_cost_tokens | 44 | good | {"goodMax": 48, "moderateMax": 92, "heavyMax": 150} |
| invoke_cost_tokens | 439 | moderate | {"goodMax": 220, "moderateMax": 480, "heavyMax": 900} |
| deferred_cost_tokens | 1922 | excessive | {"goodMax": 180, "moderateMax": 520, "heavyMax": 1200} |
| total_tokens | 2405 | excessive | {} |

```text
SKILL.md=439/references/experience-routing.md=526 /Texts=0 --> 965 (heavy-warn)
SKILL.md=439/references/workflow.md=1396 /Texts=0 --> 1835 (excessive-fail)
```

Texts: 0 — других учитываемых текстовых файлов нет.
Полный deferred: 1922 + 0 = 1922.

Штатные findings: deferred_cost_tokens-budget-high (budget, fail): deferred_cost_tokens is excessive relative to the current Codex baseline.; coverage-artifacts-unavailable (coverage, info): No coverage artifacts were found for this target.
Рекомендации: Reduce repeated instruction text and move detail into deferred supporting files.
[Полный исходный JSON: все категории, budgets, thresholds, findings и рекомендации](2026-10-08-comm-process-harness-inbox-analyze.json).

## comm-create-lazy-claude-codex-skills

Категория: skill; score/grade: 86/B; riskLevel=high.

| Показатель | Tokens | Band | Пороги |
|---|---:|---|---|
| trigger_cost_tokens | 46 | good | {"goodMax": 48, "moderateMax": 92, "heavyMax": 150} |
| invoke_cost_tokens | 464 | moderate | {"goodMax": 220, "moderateMax": 480, "heavyMax": 900} |
| deferred_cost_tokens | 2294 | excessive | {"goodMax": 180, "moderateMax": 520, "heavyMax": 1200} |
| total_tokens | 2804 | excessive | {} |

```text
SKILL.md=464/references/content-contract.md=387 /Texts=0 --> 851 (heavy-warn)
SKILL.md=464/references/evaluation.md=683 /Texts=0 --> 1147 (heavy-warn)
SKILL.md=464/references/placement-contract.md=425 /Texts=0 --> 889 (heavy-warn)
SKILL.md=464/references/validation-and-publication.md=799 /Texts=0 --> 1263 (excessive-fail)
```

Texts: 0 — других учитываемых текстовых файлов нет.
Полный deferred: 2294 + 0 = 2294.

Штатные findings: deferred_cost_tokens-budget-high (budget, fail): deferred_cost_tokens is excessive relative to the current Codex baseline.; coverage-artifacts-unavailable (coverage, info): No coverage artifacts were found for this target.
Рекомендации: Reduce repeated instruction text and move detail into deferred supporting files.
[Полный исходный JSON: все категории, budgets, thresholds, findings и рекомендации](2026-10-08-comm-create-lazy-claude-codex-skills-analyze.json).

## comm-install-harness

Категория: skill; score/grade: 86/B; riskLevel=high.

| Показатель | Tokens | Band | Пороги |
|---|---:|---|---|
| trigger_cost_tokens | 41 | good | {"goodMax": 48, "moderateMax": 92, "heavyMax": 150} |
| invoke_cost_tokens | 291 | moderate | {"goodMax": 220, "moderateMax": 480, "heavyMax": 900} |
| deferred_cost_tokens | 2750 | excessive | {"goodMax": 180, "moderateMax": 520, "heavyMax": 1200} |
| total_tokens | 3082 | excessive | {} |

```text
SKILL.md=291/references/checks.md=795 /Texts=0 --> 1086 (heavy-warn)
SKILL.md=291/references/entrypoints.md=1121 /Texts=0 --> 1412 (excessive-fail)
SKILL.md=291/references/material-placement.md=521 /Texts=0 --> 812 (heavy-warn)
SKILL.md=291/references/testing.md=313 /Texts=0 --> 604 (heavy-warn)
```

Texts: 0 — других учитываемых текстовых файлов нет.
Полный deferred: 2750 + 0 = 2750.

Штатные findings: deferred_cost_tokens-budget-high (budget, fail): deferred_cost_tokens is excessive relative to the current Codex baseline.; coverage-artifacts-unavailable (coverage, info): No coverage artifacts were found for this target.
Рекомендации: Reduce repeated instruction text and move detail into deferred supporting files.
[Полный исходный JSON: все категории, budgets, thresholds, findings и рекомендации](2026-10-08-comm-install-harness-analyze.json).

Крупнейшие references: inbox/workflow.md=1396, install/entrypoints.md=1121, create/validation-and-publication.md=799. Размер не доказывает избыточность. Простое разделение references не уменьшает общий deferred; сохраняй обязательное поведение. Скиллы, thresholds и статусы исходной оценки не изменялись.

## Generic-папка с тремя skill roots

Проверены полные временные копии этих трёх неизменённых скиллов. Общий target.kind=directory, score/grade=86/B, deferred=8160 (excessive), thresholds={"goodMax": 240, "moderateMax": 640, "heavyMax": 1600}. Общий результат не подменён отдельными оценками: выше сохранены все три индивидуальных результата и их собственные строки. SKILL.md всей папке не назначается. Сумма общего deferred совпала с суммой полных SKILL.md и deferred этих трёх roots. [Полный generic JSON](2026-10-08-generic-multiple-skills.json).
