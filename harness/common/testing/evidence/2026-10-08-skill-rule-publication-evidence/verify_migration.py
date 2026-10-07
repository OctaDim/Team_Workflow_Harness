"""Verify this migration's permanent copies without requiring the old inbox."""
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
manifest = json.loads((HERE / '2026-10-08-migration-map.json').read_text())
assert len(manifest['files']) == 21
assert sum(row['required'] for row in manifest['files']) == 18
assert len({row['copy'] for row in manifest['files']}) == 21
for row in manifest['files']:
    file = HERE / row['copy']
    assert file.is_file() and not file.is_symlink(), row['copy']
    assert hashlib.sha256(file.read_bytes()).hexdigest() == row['sha256'], row['copy']
report = HERE.parent / '2026-10-05-skill-rule-contract-publication.md'
assert hashlib.sha256(report.read_bytes()).hexdigest() == manifest['report']['after_sha256']
text = report.read_text()
assert '../../inbox/' not in text
links = re.findall(r'\[[^\]]+\]\(([^)]+)\)', text)
proofs = [target for target in links if target.startswith(HERE.name + '/')]
assert len(proofs) == 13  # nine original proof links, diff, RED, GREEN, and map
assert all((report.parent / target).is_file() for target in proofs)
assert '2deab24eb9c3' in text and '1572' in text
assert 'Формальные отметки обоих агентов — **не проверено**' in text
print('PASS: 18 required and 3 supporting artifacts; hashes, links, and historical statuses')
