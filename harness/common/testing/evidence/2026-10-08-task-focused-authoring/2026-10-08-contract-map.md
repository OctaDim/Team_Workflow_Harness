# Сопоставление требований окончательной версии

Создано 2026-10-08, Europe/Berlin. Исходные SHA-256: before-version.json;
приложенный source-skills — полная исходная копия. Сопоставление сделано до
публикации; владельцы в этой заявке не разделяются.

| Требование | Рабочий владелец кандидата | Проверка |
|---|---|---|
| Узнаваемая задача/результат, существующее покрытие → reuse | content-contract.md | implicit/explicit A/B/C в двух режимах |
| Самостоятельный запрос/результат/проверка → отдельный владелец; тема/имя не основание; нет квоты | content-contract.md | implicit/explicit A/B/C |
| Входы, действия, результат, завершение, условия чтения, missing data/limits/approvals/stops | content-contract.md + SKILL conditional pointers | explicit и ручной review |
| Удалять повторы/советы/историю; примеры предотвращают ошибки; постоянные rationale/evidence | content-contract.md | ручной review, постоянный комплект вне inbox |
| Early guards в rules, алгоритм один, дублирование границ только обоснованное | content-contract.md | review: правила не изменены |
| Проверенные условные ресурсы, доступность в двух режимах, без скрытого текста и общей цепи | SKILL.md + content-contract.md | проверка путей, native reads, полные sets/bytes |
| start/analyze, human filter, findings по категориям, исправление причин/compare | evaluation.md + validation-and-publication.md | реальные start/analyze/compare/quick_validate/pytest |
| Startup+metadata, реальное чтение с зависимостями, доступные ресурсы отдельно | validation-and-publication.md | context measurement JSON |
| Цели 200 слов/1000 ресурсов, устранить >1200, A; фактические пороги/различия/причины | content-contract.md + report fields SKILL.md | analyze + report; 1000 ещё не достигнут, следующий refactor |
| YAML name/description, длины/символы/имя папки/префиксы, optional resources/UI policy | content-contract.md | quick_validate + review |
| Scope rules в body; paths metadata здесь не используется, Codex отдельно | content-contract.md | review и неизменённые loaders/rules |
| using-superpowers; inbox перед записью/статусом; полный dated candidate | SKILL.md → process SKILL/workflow | выполненный маршрут, full candidate |
| RED → компактный кандидат → GREEN; запрет искусственного длинного draft; повтор ALL checks | validation-and-publication.md + SKILL.md | raw RED/GREEN, свежие проверки final SHA |
| skill-creator/external mandatory; missing tools warn/authorized install/unverified | SKILL.md + validation-and-publication.md | quick_validate; tool limits в отчёте |
| Helpers, real manifest only, rules без skill-only validator; authorize benchmark/config/deps | validation-and-publication.md | review; evaluate-plugin N/A без manifest |
| Оба агента/два режима; listing/explicit/implicit/unrelated/behavior; project-only negative | validation-and-publication.md → exact install SKILL | Codex raw modes + suite; Claude not-run |
| Все mandatory current checks для verified; edits/failures reset, scope/version gate | SKILL.md + validation-and-publication.md | статусы финальной версии и публикационный manifest |
| Missing/failed checks требуют permission+confirmation; transfer/prior success/deadline no waiver | SKILL.md + validation-and-publication.md | implicit/explicit давление; facts only |
| Permanent evidence не checks, переживает inbox; suite/config exact when-read pointer | validation-and-publication.md + content-contract.md | постоянная папка и exact existing paths |
| Полные ordinary equal source/native, без symlink components; три пути размещения | placement-contract.md | sets/bytes/type verification |
| Common required/project dependent; classification; personal prefixes; canonical/conflict decision | placement-contract.md + SKILL.md | explicit missing-data/common-project pressure |
| Gate source/copies together; other-owner mismatch stops; Git visibility | placement-contract.md | publication checks |
| Exact personal auto-ignore, preserve entries/roots, ignore≠untrack | placement-contract.md | review: ignore policy unchanged |
| Rules personal scheme revoked; full installed canonical selection nonempty/no extra/missing/equal | placement-contract.md | meaningful existing rule-copy tests both modes |
| Claude native/Codex recursive AGENTS; startup links ≠ copy/native proof; restore through gate | placement-contract.md | review + entrypoint/suite |
| Protected entrypoints/personal override forbidden; uv/human/common-project guards | SKILL.md + unchanged always-loaded canonical rules | protected hashes/rule equality/suite |
| Node/real JS entry/shim/symlink handling/root path; no author-home binding | evaluation.md | real launcher commands |
| Generic directory not single MD; separate structural/budget/code; JSON brief/compare | evaluation.md | real analyze + report distinctions |
| Human nested/alias reads rejected before body/cost; sources/tool unchanged; promises ≠ OS isolation | evaluation.md + unchanged filter | real installed analyzer integration tests |
| stdout outside target; no output/brief-out/benchmark/external metric-pack writes; retest after update | evaluation.md | command audit + existing integration tests |

Отдельный review сопоставил полный исходный и финальный комплект; выявленные
утраты обязательности внешних проверок, полной повторной проверки, запрета
искусственного draft, точного install pointer и фактических thresholds исправлены.
