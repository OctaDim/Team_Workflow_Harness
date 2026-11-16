"""Check the request's exact menu slots and corrected ownership contract."""
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text()
slots = (
    '- **Superpowers + Compound Engineering:** `using-superpowers + ce-brainstorm → ce-plan → ce-work`  - с одновременным выполненим `using-superpowers и ce-brainstorm`',
    '- **Compound Engineering:**  `ce-brainstorm → ce-plan → ce-work`  - нативный ce-маршрут',
    '- Без специального маршрута — выбранная модель выполняет задачу самостоятельно с текущим effort.',
)
for slot in slots:
    assert text.count(slot) == 1, f'Missing or duplicated exact menu slot: {slot}'
assert 'Если перед задачей пользователь совместно явно вызвал' not in text
assert 'контекст одного основного агента' in text
assert 'фактического вызова инструмента делегирования' in text
assert 'не заменяет' in text and 'не создаёт разрешения' in text
assert 'Молчание' in text and 'не выбирай маршрут автоматически' in text
print('Exact menu and ownership contract PASS:', path)
