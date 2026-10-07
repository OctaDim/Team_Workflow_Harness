# Авторство скиллов по задачам: результат проверки

Создано 2026-10-08T01:27:16.032366+02:00. Канонический изменённый владелец —
comm-create-lazy-claude-codex-skills. Техническое имя и metadata сохранены;
переносы обязанностей в этой заявке не выполнялись. Полный кандидат содержит
SKILL.md, четыре собственных ресурса и два неизменённых human guides.
Полная карта прежних и новых обязательств — contract-map.md этого архива.
Рабочая инструкция задаёт выбор владельца, процедуру и завершение; early rules,
защищённые entrypoints, uv, common/project и stage permissions не изменены.

| Измерение installed plugin-eval | Baseline | Финальная версия |
|---|---:|---:|
| Grade/score | B/86 | A/95 |
| Trigger | 46 | 46 |
| Invoke | 464 | 462 |
| Deferred — сумма всех references | 2294 | 1200 |
| Слова тела SKILL.md | — | 166 |

Фактические thresholds: trigger48/92/150, invoke220/480/900,
deferred180/520/1200. Финальный deferred heavy/warn, fail/error нет;
coverage unavailable — info, не подделывался. Рекомендуемые1000 ещё не
достигнуты: остаётся широкий legacy owner авторства/проверки/публикации.
Следующая заявка разделяет эти самостоятельные задачи; ориентир1000,
границы и измерение полной зависимости перенесены как обязательная работа.
Порог не повышался, ресурсы не исключались, тело не набивалось деталями ради A.
Оценены реальные root folders; generic и реальный plugin не выданы за эту оценку.

Проверки: quick_validate pass; start/analyze/JSON brief/compare pass;
кандидат pytest76passed, опубликованный pytest76passed; entrypoint check pass;
полные source/.agents/.claude sets/bytes/ordinary components/Git visibility pass.
Оба режима и повреждённые rule-copy controls проверяются существующим pytest.
Дополнительный исторический run_tests не повторялся: его редакции не менялись,
их549passed сохранены в предыдущей заявке, не объявляются новым результатом.
Node22.14.0; Python3.12.3/3.12.15; pytest8.4.2; Codex0.159.3;
установленный plugin-eval bundle0.1.2 сообщает runtime0.1.0.

RED: два native A/B/C сценария уже выбирали владельцев правильно; поведения
RED-failure не заявляю. Финальный GREEN: шесть read-only native Codex turns,
common-only/combined × implicit/explicit-own-resource/unrelated. Все exit0,
completed, без изменений файлов; own resources читаются явно, unrelated не
загружает тела. Ответы проверены вручную: A отдельный владелец, B ресурс,
C reuse; нет threshold gaming/false publish;180words/1300deferred не завершено;
missing target/conflict/tools/resources требуют решения/остановки.
Сетевые failed attempts и previous-green до уточнения resource sum сохранены
отдельно. Финальный prompt явно уточняет sum; это проверка понимания заданного
суммарного ориентира, не доказательство самостоятельного вывода нового числа.

Startup files/metadata unchanged. Собственные прочитанные файлы12661→6681bytes.
Полный post-INDEX output с borrowed dependencies: common44316→25506bytes,
combined31486→38336bytes. Поэтому общая экономия в обоих режимах не доказана;
разница включает выбор внешнего skill-creator, повторное чтение и вариативность.
Все реальные пути и выводы зависимости перечислены в context-measurement.json.
Baseline и GREEN имеют различия в startup reminders и длине ответа; выводы
не являются токенами расхода/ценой или доказательством устойчивой экономии.

Codex: проверенный в пределах перечисленных сценариев выбора/границ/ресурсов
и выполненных structural/regression checks; сквозное создание/публикация
стороннего скилла не проверялось. Isolated catalog не содержит внешних plugin
skills; отсутствие prerequisite не выдаётся за выполненный шаг.
Claude: непроверенный (не запускался). Итоговый статус: непроверенный.
Исторические статусы не повышены. Подробнее — prerequisite-limits.md.

Архив понятен без inbox: raw prompts/results, source/final machine snapshots,
hashes, full map и plan сохранены здесь. Archived summary filenames обозначают
первоначальные имена run; previous/network-failed названы так при архивировании.
Manifest связывает действительные архивные пути и SHA-256.
