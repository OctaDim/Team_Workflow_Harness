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
        duplicate_paths = sorted({f'.claude/rules/nested/rule {n}.md' for n in repeated})
        details.append(f'дублированное чтение {unique + duplicates} из 12 (' + ', '.join(duplicate_paths) + ')')
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


def test_duplicate_in_compound_literal_reads(tmp_path):
    import shlex

    trace, rules, starts, aliases = fixture_trace('both', 2, repeated=(0,))
    paths = list(aliases)
    installed = aliases[paths[0]]
    extra = tmp_path / 'AGENTS.md'
    extra.write_text('Fixture entry.\n')
    reads = event('cat ' + shlex.quote(paths[0]) + '\ncat ' + shlex.quote(paths[1])
                  + '\ncat AGENTS.md',
                  rules[installed] + rules[aliases[paths[1]]] + extra.read_text())
    compare = f'cmp {shlex.quote(paths[0])} {shlex.quote(installed)}'
    repeat = event(compare + '\ncat ' + shlex.quote(installed), rules[installed])
    root = next(p for p in Path(__file__).absolute().parents
                if (p / 'harness/common/checks/ensure_entrypoint_links.py').is_file())
    assess = runpy.run_path(str(root / 'harness/common/checks/check_human_guide_search.py'))['assess_rule_reading']
    def audit(first):
        return assess([*trace[:2], first, *trace[4:-3], repeat, *trace[-2:]], rules,
                      starts=starts, aliases=aliases, root=tmp_path, immutable_fixture=True)
    result = audit(reads)
    assert result['duplicate_rule_reads'] == {installed: 1}
    assert installed in result['rule_read_report'][-1]
    for bad in (dict(reads, aggregated_output=extra.read_text()),
                dict(reads, command=reads['command'].replace('cat AGENTS.md', 'echo unsafe'))):
        assert not audit(bad)['duplicate_rule_reads']

@pytest.mark.parametrize('mode', ['common', 'both'])
@pytest.mark.parametrize('linked', [0, 2, 12])
@pytest.mark.parametrize('body_lines', [1, 1200])
def test_rule_link_applies_after_owner_before_next_rule(mode, linked, body_lines):
    trace, rules, starts, aliases = fixture_trace(mode, linked)
    early = '.agents/skills/config-check/SKILL.md'
    late = '.agents/skills/example/SKILL.md'
    body = '# Configuration procedure\n'
    owner, other = list(rules)[:2]
    for path in [owner, other]:
        original = rules[path]
        rules[path] += f'For a configuration change read {early}.\n' + ('Context.\n' * body_lines)
        for row in trace:
            if row['aggregated_output'] == original:
                row['aggregated_output'] = rules[path]
    lookup = next(i for i, row in enumerate(trace) if '--files' in row['command'])
    offset = (next(i for i, row in enumerate(trace) if row['aggregated_output'] == rules[owner]) + 1
              if linked else lookup + 2)
    step = event('cat ' + early, body)
    ordered = trace[:offset] + [step] + trace[offset:]
    root = next(p for p in Path(__file__).absolute().parents
                if (p / 'harness/common/checks/ensure_entrypoint_links.py').is_file())
    assess = runpy.run_path(str(root / 'harness/common/checks/check_human_guide_search.py'))['assess_rule_reading']
    def audit(events, active):
        return assess(events, rules, starts=starts, aliases=aliases,
                      skill_links=active, skill_bodies={early: body, late: '# Skill\n'}, task_skills={late})
    links = {owner: {early: 0}, other: {early: 0}}
    ok = audit(ordered, links)
    assert ok['rule_reading_pass'], ok['rule_read_report']
    assert ok['skill_reads'] == [early, late]
    assert ok['full_rule_read_before_skill'] is False
    assert ok['full_rule_read_before_index'] is True
    assert audit(trace, {})['rule_reading_pass']
    index = trace[-2]
    # Listing and complete reading are independent requirements at the first INDEX.
    for incomplete in ([*ordered[:offset+1], index, *ordered[offset+1:]],
                       [row for row in ordered if '--files' not in row['command']],
                       [*ordered[:lookup], event('ls .claude/rules'), index, *ordered[lookup:]]):
        assert not audit(incomplete, links)['rule_reading_pass']
    if linked == len(rules):
        before_list = next(i for i,row in enumerate(ordered) if '--files' in row['command'])
        failure = audit([*ordered[:before_list], index, *ordered[before_list:]], links)
        assert not failure['rule_reading_pass']
        assert 'INDEX открыт до получения полного списка правил' in failure['rule_read_report'][-1]
        assert failure['full_rule_read_before_index'] is False
    if linked:
        short = dict(ordered[offset-1], aggregated_output=rules[owner].split('Context.')[0])
        assert not audit([*ordered[:offset-1], short, *ordered[offset:]], links)['rule_reading_pass']
        # A metadata probe does not open INDEX; its actual contents stay deferred.
        assert audit([event('ls harness/common/INDEX.md'), *ordered], links)['rule_reading_pass']

    assert not audit(ordered, {})['rule_reading_pass']
    assert not audit(ordered, {owner: {early: 999}})['rule_reading_pass']
    assert not audit(trace, links)['rule_reading_pass']
    late_condition = {owner: {early: len(trace) - 1}}
    assert audit([*trace[:-1], step, trace[-1]], late_condition)['rule_reading_pass']
    metadata = event('ls -l ' + early)
    assert audit([*ordered[:offset], metadata, *ordered[offset:]], links)['rule_reading_pass']
    bulk = event('find .agents/skills -name SKILL.md -exec cat {} +')
    assert not audit([*ordered, bulk], links)['rule_reading_pass']

    for forbidden in ([step, *ordered], [*ordered, step],
                      [*ordered, event('cat .agents/skills/*/SKILL.md')],
                      [*ordered[:offset], dict(step, aggregated_output='partial'), *ordered[offset+1:]]):
        assert not audit(forbidden, links)['rule_reading_pass']


@pytest.mark.parametrize('mode', ['common', 'both'])
def test_skill_read_once_across_rule_and_index(mode, tmp_path):
    trace, rules, starts, aliases = fixture_trace(mode, linked=2)
    target = '.agents/skills/example/SKILL.md'
    body = '# Skill\nUse the existing default.\n'
    owner = next(iter(rules))
    before = rules[owner]
    rules[owner] += f'When needed, read {target}.\n'
    for row in trace:
        if row['aggregated_output'] == before:
            row['aggregated_output'] = rules[owner]
    pos = next(i for i,row in enumerate(trace) if row['aggregated_output'] == rules[owner]) + 1
    trace[-2]['aggregated_output'] += f'[Required procedure](../../{target})\n'
    full = event('cat ' + target, body)
    first = event('head -n 1 ' + target, '# Skill\n')
    last = event('tail -n 1 ' + target, 'Use the existing default.\n')
    root = next(p for p in Path(__file__).absolute().parents
                if (p / 'harness/common/checks/ensure_entrypoint_links.py').is_file())
    audit = runpy.run_path(str(root / 'harness/common/checks/check_human_guide_search.py'))['assess_rule_reading']

    def check(early=(), late=(), due=True, **kwargs):
        events = trace[:pos] + list(early) + trace[pos:-1] + list(late)
        return audit(events, rules, starts=starts, aliases=aliases,
                     skill_links={owner: {target: 0}} if due else {},
                     skill_bodies={target: body}, task_skills={target}, **kwargs)

    positive = check([full])
    assert positive['rule_reading_pass'] and positive['skill_reads'] == [target]
    negative = check([full], [full])
    assert not negative['rule_reading_pass']
    assert negative['duplicate_skill_reads'] == {target: 1}
    assert target in negative['rule_read_report'][-1] and 'решение пользователя' in negative['rule_read_report'][-1]
    assert check([], [full], due=False)['rule_reading_pass']
    assert check([first], [last])['rule_reading_pass']
    assert not check([first], [])['rule_reading_pass']
    assert not check([first], [event('tail -n 1 ' + target, 'Incorrect\n')])['rule_reading_pass']
    unrelated = event('touch unrelated.txt')
    assert check([full], [unrelated, full])['duplicate_skill_reads'] == {target: 1}

    changed = '# Skill\nUse the revised default.\n'
    reread = event('cat ' + target, changed)
    at = len(trace)  # after the inserted early read and both INDEX reads
    updated = check([full], [reread], skill_updates={at: {target: changed}})
    assert updated['rule_reading_pass'] and updated['skill_reads'] == [target, target]
    assert not check([first], [event('tail -n 1 ' + target, changed.splitlines(True)[1])],
                     skill_updates={at: {target: changed}})['rule_reading_pass']

    canonical = 'harness/common/skills/example/SKILL.md'
    for path in (target, canonical):
        file = tmp_path / path
        file.parent.mkdir(parents=True)
        file.write_text(body)
    canonical_read = event('cat ' + canonical, body)
    alias_repeat = check([canonical_read], [full], root=tmp_path, immutable_fixture=True)
    assert alias_repeat['duplicate_skill_reads'] == {target: 1}
    (tmp_path / canonical).write_text(changed)
    distinct = check([event('cat ' + canonical, changed)], [full], root=tmp_path, immutable_fixture=True)
    assert not distinct['rule_reading_pass'] and not distinct['duplicate_skill_reads']
