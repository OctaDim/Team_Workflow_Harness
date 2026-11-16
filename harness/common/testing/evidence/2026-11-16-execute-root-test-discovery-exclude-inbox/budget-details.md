# Штатные бюджеты и компактность

baseline: skill /home/octadim/MyProjects/Team_Workflow_Harness/harness/common/skills/comm-install-harness — A/95; trigger/invoke/deferred/total=38/383/1130/1551.
Штатные thresholds/bands/checks сохранены в JSON без изменений. Texts=0 — полностью известный ноль: все deferred-компоненты находятся в references; иных учитываемых файлов нет.
SKILL.md=383/references/checks.md=817 /Texts=0 --> 1200 (heavy-warn)
SKILL.md=383/references/testing.md=313 /Texts=0 --> 696 (heavy-warn)

baseline: skill /home/octadim/MyProjects/Team_Workflow_Harness/harness/common/skills/comm-process-harness-inbox — A/95; trigger/invoke/deferred/total=26/326/1081/1433.
Штатные thresholds/bands/checks сохранены в JSON без изменений. Texts=0 — полностью известный ноль: все deferred-компоненты находятся в references; иных учитываемых файлов нет.
SKILL.md=326/references/workflow.md=1081 /Texts=0 --> 1407 (excessive-fail)

prepared: skill /home/octadim/MyProjects/Team_Workflow_Harness/harness/common/inbox/2026-11-16-root-test-discovery-exclude-inbox/candidate/comm-install-harness — B/86; trigger/invoke/deferred/total=38/383/1542/1963.
Штатные thresholds/bands/checks сохранены в JSON без изменений. Texts=0 — полностью известный ноль: все deferred-компоненты находятся в references; иных учитываемых файлов нет.
SKILL.md=383/references/checks.md=817 /Texts=0 --> 1200 (heavy-warn)
SKILL.md=383/references/testing.md=725 /Texts=0 --> 1108 (heavy-warn)

prepared: skill /home/octadim/MyProjects/Team_Workflow_Harness/harness/common/inbox/2026-11-16-root-test-discovery-exclude-inbox/candidate/comm-process-harness-inbox — B/86; trigger/invoke/deferred/total=26/326/1219/1571.
Штатные thresholds/bands/checks сохранены в JSON без изменений. Texts=0 — полностью известный ноль: все deferred-компоненты находятся в references; иных учитываемых файлов нет.
SKILL.md=326/references/workflow.md=1219 /Texts=0 --> 1545 (excessive-fail)

candidate: skill /home/octadim/MyProjects/Team_Workflow_Harness/harness/common/inbox/2026-11-16-root-test-discovery-exclude-inbox/candidate-v2/comm-install-harness — A/95; trigger/invoke/deferred/total=38/383/1199/1620.
Штатные thresholds/bands/checks сохранены в JSON без изменений. Texts=0 — полностью известный ноль: все deferred-компоненты находятся в references; иных учитываемых файлов нет.
SKILL.md=383/references/checks.md=817 /Texts=0 --> 1200 (heavy-warn)
SKILL.md=383/references/testing.md=382 /Texts=0 --> 765 (heavy-warn)

candidate: skill /home/octadim/MyProjects/Team_Workflow_Harness/harness/common/inbox/2026-11-16-root-test-discovery-exclude-inbox/candidate-v2/comm-process-harness-inbox — A/95; trigger/invoke/deferred/total=26/326/1171/1523.
Штатные thresholds/bands/checks сохранены в JSON без изменений. Texts=0 — полностью известный ноль: все deferred-компоненты находятся в references; иных учитываемых файлов нет.
SKILL.md=326/references/workflow.md=1171 /Texts=0 --> 1497 (excessive-fail)

Prepared версии превышали deferred 1200 (1542/1219) и получили B/86; они не публикуются. Компактные версии: 1199/1171, A/95 без fail/error. Штатный moderateMax=520, heavyMax=1200 не менялся; deferred warnings сохранены.
Крупнейший install reference — неизменённый checks.md (817); workflow сохраняет прежний протокол полномочий и статусов. Изменены только testing.md и добавляемый абзац workflow.md. Отдельная шкала строк — дополнительная, не замена статуса анализатора; строки не складываются.
Цель resource sum 1000 превышена и до задачи (1130/1081), и после неё; сохранение непричастного approval/install контракта важнее посторонней переработки. По сравнению с prepared избыточность уменьшена без удаления требований. Факты lock/coverage переиспользуют существующий docs owner; этот внешний документ и runtime-код учитываются отдельно от локального resource budget.
Единицы estimated-static; это не расход токенов сессии и не весь стартовый/доступный контекст. Реальные native reads/usage сохраняются отдельно.
