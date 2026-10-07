"""Summarize raw current-session outputs; file sizes are not runtime usage."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    rows = []
    for phase, folder in [('red', 'before'), ('green', 'candidate')]:
        source = HERE / folder
        files = [p for p in (source / 'harness').rglob('*.md')
                 if p.name != 'README.human.md'
                 and not any(x in p.relative_to(source).parts
                             for x in ['testing', 'inbox', 'handoffs'])]
        texts = {str(p.relative_to(source)): p.read_text() for p in files}
        assert any('/skills/' in name for name in texts), 'Empty content selection'
        traces = list(HERE.glob(f'codex-*-{phase}-*-events.json'))
        if phase == 'green':
            traces += list((HERE / 'final-matrix-save-observation').glob('*-events.json'))
        for path in sorted(traces):
            raw = json.loads(path.read_text())
            events = [json.loads(line) for line in raw['stdout'].splitlines()
                      if line.startswith('{')]
            reads = []
            for event in events:
                item = event.get('item', {})
                if event.get('type') != 'item.completed' or item.get('type') != 'command_execution':
                    continue
                output = item.get('aggregated_output', '')
                if not output:
                    continue
                matched = [name for name, text in texts.items() if text and text in output]
                reads.append({'item_id': item.get('id'), 'command': item.get('command'),
                              'exit_code': item.get('exit_code'), 'output_chars': len(output),
                              'output_sha256': hashlib.sha256(output.encode()).hexdigest(),
                              'full_machine_text_matches': matched})
            rows.append({'events_file': str(path.relative_to(HERE)), 'phase': phase,
                         'usage': [e.get('usage') for e in events if e.get('type') == 'turn.completed'],
                         'command_outputs': reads,
                         'command_output_chars': sum(x['output_chars'] for x in reads),
                         'elapsed_seconds': raw['elapsed_seconds'],
                         'file_changes': raw.get('file_changes'), 'exit_code': raw['exit_code']})
    (HERE / 'runtime-context.json').write_text(json.dumps({
        'method': 'Completed command outputs and reported CLI usage. Full-text matches prove observed content, not the physical path when copies have identical text. Missing match alone does not prove non-reading (truncation/formatting); manual review decides relevance/discovery. Command outputs include startup notifications, search matches and rereads; not unique file sizes. Usage includes CLI preamble, tool turns, responses and cache effects; no monetary inference or controlled causal token-savings claim.',
        'rows': rows,
    }, ensure_ascii=False, indent=2) + '\n')
    print(f'Measured {len(rows)} raw sessions')


if __name__ == '__main__':
    main()
