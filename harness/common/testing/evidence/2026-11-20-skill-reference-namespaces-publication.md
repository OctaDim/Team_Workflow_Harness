# Публикация candidate-v2 по заявке № 6

20 ноября 2026 года. Кандидат из коммита `0f5cd01` установлен в канонические правила и скиллы common и в их нативные копии. Сверены SHA-256 девяти изменённых исходных файлов и 16 установленных копий. Полные деревья пяти скиллов в common, .agents/skills и .claude/skills совпали с кандидатом. Стартовая команда прошла. После установки полный прогон pytest из корня завершился успешно — 230 тестов.

## Дополнение из бокового диалога

В обычном профиле Codex CLI 0.166.0 для каждого из 14 имён выполнили отдельный вызов `Примени $плагин:скилл` с учебной задачей и просьбой прочитать SKILL.md. Запрос не содержал путь к целевому файлу. Во всех 14 случаях Codex самостоятельно нашёл файл в локальном кэше, полностью прочитал его и применил процедуру к задаче. Все процессы завершились с кодом 0. Ни одно из этих имён не появилось в skills/list после проверки. Это подтверждено снимками до и после как для учебного каталога, так и для рабочего проекта.

При публикации также сверены имена, запросы, полные тексты SKILL.md в успешных событиях инструментов и завершение исходных диалогов. В таблице номера строк каждого JSONL приведены с единицы. Оценка применения процедуры взята из результата боковой проверки. Она дополняет ранее сохранённую [проверку кандидата в двух режимах](2026-11-20-skill-reference-namespaces-candidate-v2.md).

| Переданное имя | Версия плагина | Полное чтение, событие | SHA-256 трассы |
|---|---|---:|---|
| `plugin-eval:evaluate-plugin` | 0.1.2 | 10 | `694d7db489199d9b61786c83948e7fbe3d1f35e5833dbc1737a0ae96f7b23bc3` |
| `plugin-eval:evaluate-skill` | 0.1.2 | 9 | `67fd094e4485e614b5aa952e674815b7b6e5ec2bd66ce3ec7325170adcc79f30` |
| `plugin-eval:improve-skill` | 0.1.2 | 9 | `daaa360c01b55406885bf6af933c51a6fc879023d16120a6d8bcf74a7d46cfbf` |
| `plugin-management:plugin-management` | 0.1.0 | 9 | `4a9bd4e6596126f45aa1403f9fce4e036ec80672be0ca9a7dcc8527f8b93ead3` |
| `superpowers:brainstorming` | 7.0.1 | 7 | `b441e3a17c587608a5a2794171e334d35c313a6bae66b2114e3b19c1459ece8b` |
| `superpowers:executing-plans` | 7.0.1 | 9 | `567233687947eda30116b88ec77759ab22dd60eec6981ea2384a98c0353cb981` |
| `superpowers:finishing-a-development-branch` | 7.0.1 | 9 | `445a2c228a2dd9f14517c193629622798bff0fff3e7cd8e3e84cbab7b3166603` |
| `superpowers:subagent-driven-development` | 7.0.1 | 9 | `8ac59a77d07c3cdf017f34e80391dc11675615119f7a874cb53b54b4cd2cda98` |
| `superpowers:systematic-debugging` | 7.0.1 | 9 | `4b12595afcd872827807ed4534171af3080f36e202677a7bce10ef9d9dc27db4` |
| `superpowers:test-driven-development` | 7.0.1 | 9 | `057b1ee31790b2d97041645aa87901048072128fe7ad3e8e6b960a0b28b73274` |
| `superpowers:using-superpowers` | 7.0.1 | 9 | `6daeffb23f2dd64934f6b4a358798543f94f18068d09ace53fca27568389610a` |
| `superpowers:verification-before-completion` | 7.0.1 | 9 | `abff70367d3c63e8f0b1abe5d167f70c63ad783b49c9aea47c7eaccced76d382` |
| `superpowers:writing-plans` | 7.0.1 | 11 | `65e8a3f7572117fedc52aee28147c059d139fdfd8776652fc860a45b5c9281d7` |
| `superpowers:writing-skills` | 7.0.1 | 9 | `eda6577f4815f87251d4da8124bf17bd194e7db0e2eb77692bcd2b177986afea` |

Проверка Claude — непроверенный. Итоговый статус опубликованной версии — **непроверенный**.
