# Публикация навыка нормализации LF/CRLF

Дата: 2026-10-08T21:20:00.884817+02:00, Europe/Berlin.
Кандидат SHA-256: `f026597aca7ff151e49a410b5fae97f319583024c0742543c43977daf071d4c5`.

Пользователь ответил «публикуй» на отдельный вопрос о публикации этой версии
в common и native-копии с непроверенным итоговым статусом. Разрешение и
подтверждение получены. Кандидат не изменён; файлы репозитория не нормализованы.

## Установленный результат

- `harness/common/skills/comm-normalize-text-line-endings/`
- `.agents/skills/comm-normalize-text-line-endings/`
- `.claude/skills/comm-normalize-text-line-endings/`

Во всех папках полный исходный состав: SKILL.md и README.human.md.
Наборы, байты и хеши равны кандидату; пути обычные без симлинков;
Git видит все шесть файлов. Защищённые входы и 20 файлов project сохранены.
Проверен весь установленный набор правил: 7 равных canonical/native файлов.
Скилл не содержит относительных ссылок или дополнительных ресурсов.
[Манифест и проверки](2026-10-08-publication-checks.json).

## Новые проверки публикации

- `python3 /home/octadim/.codex/skills/.system/skill-creator/scripts/quick_validate.py <candidate>` — PASS;
  повтор для опубликованного common — PASS.
  [Вывод](2026-10-08-publication-quick-validate.txt).
- Node + plugin-eval 0.1.0 через `plugin_eval_without_human.mjs`, start → analyze — A/100,
  0 ошибок/предупреждений, обязательных и рекомендуемых исправлений нет.
  [Start](2026-10-08-publication-plugin-eval-start.json),
  [analyze](2026-10-08-publication-plugin-eval-analyze.json).
- Статические бюджеты: trigger 40 (good ≤48), invoke 359 (moderate ≤480), deferred 0 (good ≤180).
  Это не расход сессии; прежние фактические измерения сохранены в
  [контексте](2026-10-08-context-measurement.json).
- `.venv/bin/python -m pytest -q`: до публикации 76/76,
  [до](2026-10-08-publication-pytest-before.txt); после 76/76,
  [после](2026-10-08-publication-pytest-after.txt).
  Набор включает human-фильтр, правила, оба режима установки, повторный startup,
  отрицательный project-only контроль. Исторические редакции не повторялись.
- `python3 -B harness/common/checks/ensure_entrypoint_links.py` после установки — PASS,
  без восстановления ссылок и изменения защищённых входов.
  [Вывод](2026-10-08-publication-entrypoint.txt).
- Полные опубликованные папки перенесены в две чистые временные установки,
  common-only и common+project. Проверены равенство native-копий, все 7 правил,
  повторяемость startup, нейтральный отсутствующий project, сохранение существующего.
  Использованы TestPortability.install/run_check и check_rule_copies.
  [Результаты](2026-10-08-publication-installations.json).
- Для вызова check_rule_copies системный Python не содержал pytest;
  повтор через существующий `.venv/bin/python` успешен. Зависимости не устанавливались.

## Границы статусов и завершение

Прежние 10 нативных сценариев Codex относятся к тому же SHA-256 и сохранены
с исходными датами. Новые проверки структурные; native поведение не повторялось.
Codex: проверено в перечисленных сценариях прежнего
[отчёта кандидата](2026-10-08-result.md). Claude: непроверенный.
Windows cmd.exe: непроверенный, доступного runtime нет.
Итог: непроверенный, публикация выполнена по разрешённому исключению.
Копирование и разрешение статусы не повышают. Baseline без кандидата также
проходил; улучшение поведения против baseline не доказано.

Скилл опубликован в common и обоих native-каталогах; основания, полный снимок,
сырые прежние свидетельства и новые результаты находятся вне inbox.
Заявка выполнена. Остальные 35 завершённых заявок не повторялись.
