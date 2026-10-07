# Хронологическое выполнение inbox, 2026-10-06

Порядок birth time: B 10:02:53 → C 12:34:33 → A 15:26:15 (Europe/Berlin).
12 ранее завершённых заявок пропущены. Три оставшиеся выполнены последовательно,
после каждой создан отдельный локальный коммит. Подагенты и новые чаты не запускались.

| Заявка | Результат | Нативные статусы |
|---|---|---|
| Два режима | 30 путей manifest 388a37a1…, common-only создаёт нейтральный project, common+project сохраняет материалы; коммит cdf8e55 | Codex PASS; Claude не проверено |
| Фильтр plugin-eval | Launcher/procedure и две копии указателя 100036e5…; коммит a4ee856 | Codex PASS; Claude не проверено |
| Стадии согласования | 10 путей manifest b921993d948560489e3e29612009293179be985935f9a0f0a230ebec619c8352; правило, ресурс, решения, примеры и урок опубликованы | Codex не проверено (два S8 FAIL); Claude не проверено |

B/C опубликованы по отдельным точным разрешениям/подтверждениям; A — по
явному разрешению публикации всех текущих задач. Желаемые отметки «проверено»
не подменяют фактические результаты. Защищённые входы остались byte-identical.
После каждой установки 39/39 локальных tests PASS; native copies обычные, полные
и равны source. Итоговый installed skill 95/A, 1198 WARN, без FAIL (static).

A final explicit/implicit own-resource чтение в обоих режимах PASS.
Короткие S8 пропускают чтение правил/урока и конкретный запрос разрешения;
публикация это ограничение не устраняет. Старые 18 cases относятся к прежнему
manifest и сохранены отдельно, не объявлены проверкой финальной версии.

[Версии и пути](2026-10-06-inbox-current-candidate-manifests.json).
[B native](../2026-10-06-two-installation-modes/2026-10-06-codex-two-modes-final-compaction.json);
[C native](../2026-10-06-plugin-eval-human-filter/2026-10-06-codex-human-filter-native.json);
[A final native](../2026-10-06-inbox-authorization/2026-10-06-codex-inbox-authorization-native.json);
[A contract/limitations](../2026-10-06-inbox-authorization/2026-10-06-inbox-authorization-interpretation-evidence.md).
