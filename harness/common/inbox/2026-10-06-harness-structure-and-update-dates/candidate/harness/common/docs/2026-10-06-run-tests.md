# Запуск pytest

Из корня проекта, Python 3.9+ и установленный uv:

```sh
uv venv .venv
uv pip sync --python .venv/bin/python harness/common/testing/requirements.lock
.venv/bin/python -m pytest
.venv/bin/python harness/common/scripts/run_tests.py
```

Обычный запуск собирает основной набор. Последняя команда отдельно запускает
каждую фактическую редакцию тестов, включая все копии inbox; одноимённые модули
не смешиваются благодаря `--import-mode=importlib`. Сбор тестов не зависит от
установленных сторонних pytest-плагинов: при диагностике можно задать
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.

После переноса common скопируй `harness/common/testing/pytest.ini` в корневой
`pytest.ini`, затем выполни команды выше. Не перезаписывай отличающуюся
конфигурацию существующего проекта: интегрируй путь основного набора и режим
импорта в его настройку pytest. Тестовая зависимость не нужна для стартовой
проверки `python3 -B harness/common/checks/ensure_entrypoint_links.py`.

`requirements.txt` фиксирует прямые зависимости, `requirements.lock` —
результат `uv pip compile --universal --python-version 3.9` с условными
зависимостями платформ и версий Python. Coverage нужен для сравнения покрытия
при миграциях; основной набор не использует pytest-плагины.
