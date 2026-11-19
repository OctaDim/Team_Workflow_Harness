"""Reject incomplete/unsafe native traces; do not call the external agent in pytest."""
import runpy
from pathlib import Path

import pytest


def test_rule_reader_rejects_globs_missing_files_and_combined_calls():
    script = Path(__file__).with_name('check_human_guide_search.py')
    if not script.is_file():
        root = next(p for p in Path(__file__).resolve().parents
                    if (p / 'harness/common/checks/ensure_entrypoint_links.py').is_file())
        script = root / 'harness/common/checks/check_human_guide_search.py'
    try:
        assess = runpy.run_path(str(script))['assess_rule_reading']
    except (SystemExit, KeyError):
        pytest.fail('The check cannot assess a completed bulk-rule-reading trace')
    paths = ['.claude/rules/comm-a.md', '.claude/rules/nested/personal space.md']
    bodies = dict(zip(paths, ['# First rule\n', '# Nested rule\n']))
    listing = {'command': "rg --files --hidden --no-ignore .claude/rules -g '*.md' -g '!README.human.md'",
               'aggregated_output': '\n'.join(paths) + '\n', 'exit_code': 0}
    reading = {'command': "cat '.claude/rules/comm-a.md' '.claude/rules/nested/personal space.md'",
               'aggregated_output': '# First rule\n# Nested rule\n', 'exit_code': 0}
    skill = {'command': 'cat .agents/skills/example/SKILL.md',
             'aggregated_output': 'Skill body', 'exit_code': 0}
    assert assess([listing, reading, skill], bodies)['rule_reading_pass']
    startup_listing = dict(listing, command='cat harness/common/START.md; ' + listing['command'],
                           aggregated_output='# Startup boundary\n' + listing['aggregated_output'])
    assert not assess([startup_listing, reading, skill], bodies)['rule_reading_pass']
    preliminary = [dict(listing, command=listing['command'].replace('--no-ignore ', '')),
                   dict(reading, command='cat .claude/rules/comm-a.md', aggregated_output='# First rule\n')]
    assert not assess(preliminary + [listing, reading, skill], bodies)['rule_reading_pass']
    assert not assess([reading, skill], bodies)['rule_reading_pass']
    assert not assess([dict(listing, command=listing['command'].replace('--no-ignore ', '')), reading, skill], bodies)['rule_reading_pass']
    assert not assess([dict(listing, aggregated_output=paths[0]), reading, skill], bodies)['rule_reading_pass']
    assert not assess([listing, dict(reading, aggregated_output='# First rule\n'), skill], bodies)['rule_reading_pass']
    assert not assess([listing, dict(reading, command='cat .claude/rules/*.md'), skill], bodies)['rule_reading_pass']
    combined = dict(listing, command=listing['command'] + ' && ' + reading['command'],
                    aggregated_output=listing['aggregated_output'] + reading['aggregated_output'])
    assert not assess([combined, listing, reading, skill], bodies)['rule_reading_pass']
    reversed_call = dict(listing, command=reading['command'] + ' && ' + listing['command'],
                         aggregated_output=reading['aggregated_output'] + listing['aggregated_output'])
    assert not assess([listing, reading, reversed_call, skill], bodies)['rule_reading_pass']
    assert not assess([listing, skill, reading], bodies)['rule_reading_pass']
    assert not assess([listing, dict(reading, exit_code=1), skill], bodies)['rule_reading_pass']
    assert not assess([], {})['rule_reading_pass']


def event(command, output='', code=0):
    return {'command': command, 'aggregated_output': output, 'exit_code': code}


def fixture_trace(mode, linked, skipped=(), repeated=()):
    import shlex
    from collections import defaultdict

    paths = [f'.claude/rules/nested/rule {n}.md' for n in range(12)]
    rules = {p: f'# Rule {n}\nSecond line {n}\n' for n, p in enumerate(paths)}
    starts = defaultdict(str)
    aliases = {}
    for n, path in enumerate(paths[:linked]):
        package = 'project' if mode == 'both' and n % 2 else 'common'
        relative = path.removeprefix('.claude/')
        starts[f'harness/{package}/START.md'] += f'[{n}](<{relative}>)\n'
        aliases[f'harness/{package}/{relative}'] = path
    trace = [event('cat ' + s, body) for s, body in starts.items()]
    trace += [event('cat ' + shlex.quote(s), rules[p]) for s, p in aliases.items()]
    trace.append(event("rg --files --hidden --no-ignore .claude/rules -g '*.md' -g '!README.human.md'",
                       '\n'.join(paths)))
    for n in [*range(linked, 12), *repeated]:
        if n not in skipped:
            trace.append(event('cat ' + shlex.quote(paths[n]), rules[paths[n]]))
    indexes = ' '.join(str(Path(start).with_name('INDEX.md')) for start in starts) or 'harness/common/INDEX.md'
    trace += [event('cat ' + indexes, '# Index\n'),
              event('cat .agents/skills/example/SKILL.md', '# Skill\n')]
    return trace, rules, starts, aliases


def evaluate(trace, rules, starts, aliases):
    root = next(p for p in Path(__file__).absolute().parents
                if (p / 'harness/common/checks/ensure_entrypoint_links.py').is_file())
    check = runpy.run_path(str(root / 'harness/common/checks/check_human_guide_search.py'))
    return check['assess_rule_reading'](trace, rules, starts=starts, aliases=aliases)


@pytest.mark.parametrize('mode', ['common', 'both'])
@pytest.mark.parametrize('linked,skipped,repeated,unique,duplicates', [
    (0, (), (), 12, 0), (1, (), (), 12, 0), (2, (), (), 12, 0),
    (5, (), (), 12, 0), (12, (), (), 12, 0), (2, (9, 10), (), 10, 0),
    (2, (), (1, 4, 4), 12, 3), (2, (11,), (3,), 11, 1),
])
def test_start_rule_accounting(mode, linked, skipped, repeated, unique, duplicates):
    result = evaluate(*fixture_trace(mode, linked, skipped, repeated))
    status = 'Успешно' if unique == 12 and not duplicates else 'Ошибка'
    details = []
    if unique != 12 or not duplicates:
        details.append(f'прочтено {unique} из 12')
    if duplicates:
        details.append(f'дублированное чтение {unique + duplicates} из 12')
    assert result['rule_read_report'] == [
        f'Правила `.claude/rules/` через ссылки в START.md: {linked}',
        f'Правила `.claude/rules/` через ссылку на `.claude/rules/` в AGENTS.md: {unique - linked}',
        'Всего правил в `.claude/rules/`: 12',
        f'Всего правил прочитано: {unique}',
        f'Повторно прочитанных правил: {duplicates}',
        f'Результат: {status} - ' + ', '.join(details),
    ]
    assert result['rule_reading_pass'] == (status == 'Успешно')
    print(mode, *result['rule_read_report'], sep='\n')


def test_partial_current_reads_and_boundaries():
    trace, rules, starts, aliases = fixture_trace('common', 1)
    path = next(iter(aliases))
    body = rules[aliases[path]]
    second = event(f"sed -n '2,$p' '{path}'", body.splitlines(True)[1])
    partial = event(f"head -n 1 '{path}'", body.splitlines(True)[0])
    def passed(events):
        return evaluate(events, rules, starts, aliases)['rule_reading_pass']

    assert passed([trace[0], partial, trace[2], second, *trace[3:]])
    assert not passed([trace[0], partial, *trace[2:]])
    assert not passed([trace[0], dict(trace[1], aggregated_output='old'), *trace[2:]])
    # A changed or unverified version invalidates accumulated fragments.
    for marker in [event("cat '" + path + "'", 'different version\n'),
                   event("touch '" + path + "'")]:
        assert not passed([trace[0], partial, marker, trace[2], second, *trace[3:]])
        assert passed([*trace[:2], marker, trace[2], trace[1], *trace[3:]])
    for boundary in [trace[-2], event('cat .agents/skills/example/references/help.md')]:
        assert not passed([*trace[:2], boundary, *trace[2:]])
        mixed = dict(trace[-3], command=trace[-3]['command'] + ' && ' + boundary['command'])
        assert not passed([*trace[:-3], mixed, *trace[-2:]])
    assert not passed([trace[0], dict(trace[1], command='cat unrelated/rule.md'), *trace[2:]])
    assert not passed([trace[1], trace[0], *trace[2:]])
    assert not evaluate([trace[0], *trace[2:]], rules, starts, {})['rule_reading_pass']


def test_canonical_mapping_requires_full_relative_path_and_matching_bytes(tmp_path):
    root = next(p for p in Path(__file__).absolute().parents
                if (p / 'harness/common/checks/check_human_guide_search.py').is_file())
    snapshot = runpy.run_path(str(root / 'harness/common/checks/check_human_guide_search.py'))['snapshot_rule_inputs']
    native = tmp_path / '.claude/rules'
    canonical = tmp_path / 'harness/project/rules'
    for parent in [native, canonical]:
        for relative in ['x/same.md', 'y/same.md', '.ignored/local.md', 'z/README.human.md']:
            target = parent / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('# Identical content\n')
    (canonical / 'y/same.md').write_text('New version\n')
    (canonical / 'START.md').write_text('Unrelated file\n')
    expected, _, aliases = snapshot(tmp_path)
    assert set(expected) == {'.claude/rules/' + name for name in ['x/same.md', 'y/same.md', '.ignored/local.md']}
    assert aliases == {'harness/project/rules/' + name: '.claude/rules/' + name
                       for name in ['x/same.md', '.ignored/local.md']}


@pytest.mark.parametrize('mode', ['common', 'both'])
def test_skill_and_listing_must_wait_for_rule_read_results(mode):
    trace, rules, starts, aliases = fixture_trace(mode, 5)
    for i, row in enumerate(trace):
        row.update(start_event=2*i, end_event=2*i+1)
    listing = next(i for i, row in enumerate(trace) if '--files' in row['command'])
    for index in [listing, listing+1, len(trace)-2]:
        overlapping = [*trace]
        overlapping[index] = dict(trace[index], start_event=trace[index-1]['start_event'])
        assert not evaluate(overlapping, rules, starts, aliases)['rule_reading_pass']


@pytest.mark.parametrize('form', ['ls', 'loop'])
def test_literal_reads_with_directory_output_and_named_loop(form):
    import shlex

    trace, rules, starts, aliases = fixture_trace('common', 5)
    names = list(aliases)
    args = ' '.join(map(shlex.quote, names))
    if form == 'ls':
        command = 'ls -la harness/common; cat -- ' + args
        output = 'directory contents\n' + ''.join(rules[aliases[name]] for name in names)
    else:
        command = 'for p in ' + args + "; do printf '%s\\n' \"$p\"; cat \"$p\"; done"
        output = ''.join(name + '\n' + rules[aliases[name]] for name in names)
    reads = event(command, output)
    assert evaluate([trace[0], reads, *trace[6:]], rules, starts, aliases)['rule_reading_pass']
    assert not evaluate([trace[0], dict(reads, aggregated_output=output[:-10]), *trace[6:]],
                        rules, starts, aliases)['rule_reading_pass']
