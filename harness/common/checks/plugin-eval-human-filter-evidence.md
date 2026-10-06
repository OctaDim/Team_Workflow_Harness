# Фильтр человеческих README: текущая приёмка

Дата: 2026-10-06. Решение: [plugin-eval-human-filter.md](../decisions/plugin-eval-human-filter.md).

Launcher исключает точное README.human.md до budget walk/read и запрещает
прямое/alias чтение, запись и внешние metric-pack процессы. Файлы анализатора
и человеческие описания не изменяются. Это фильтр используемых promises API,
не ОС-защита; после обновления plugin-eval повторить интеграционную проверку.

Текущий integration PASS: настоящий skill/plugin/generic analyzer, вложенные
README, прямое чтение, alias, запрет записи, неизменность plugin/input.
Четыре текущих Codex common/both × explicit/implicit PASS:
[полные журналы/review](codex-human-filter-native.json). Процедура прочитана
перед filtered start/analyze, hashes fixture неизменны.
Bounded generic анализ папки только текущего правила: 100/A, без FAIL/WARN;
статическая оценка не native proof и не измеренный расход сессии.

Claude — не проверено. Указатель SHA-256
100036e5fc40a58ba24d9556dbb916aa311decfba447b50c43d6406309aa288d
ожидает явного разрешения и подтверждения непроверенной публикации по
путям harness/common/rules/comm-human-folder-guides.md и
.claude/rules/comm-human-folder-guides.md. AGENTS.md/CLAUDE.md не изменяются.
Предшествующая B опубликована, коммит cdf8e55.
Исторические неуспешные проверки сохранены в заявке и не заменяют текущие.

## Публикация текущей версии

Пользователь явно разрешил и подтвердил непроверенную по Claude публикацию
указанного SHA-256 по двум named source/native путям. Копирование выполнено;
hashes одинаковы. После установки 39/39 tests и проверка входов PASS.
Заявка выполнена; Codex PASS, Claude не проверено.
