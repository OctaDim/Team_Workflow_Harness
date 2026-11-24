from pathlib import Path
import runpy
import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import uuid

# Check the bootstrap paths before importing the existing shared guards.
SCRIPT = Path(__file__).absolute()
CHECKER = SCRIPT.parents[1] / 'checks/ensure_entrypoint_links.py'
for source in (SCRIPT, CHECKER):
    for component in (*reversed(source.parents), source):
        if component.is_symlink():
            raise ValueError(f'Symlink forbidden: {component}')
GUARDS = runpy.run_path(str(CHECKER))
ordinary_path, ordinary_tree = GUARDS['ordinary_path'], GUARDS['ordinary_tree']

REPO = SCRIPT.parents[3]


def command_tokens(command):
    """Parse arguments, retaining shell operators so compound reads cannot earn credit."""
    lexer = shlex.shlex(command, posix=True, punctuation_chars="();<>|&\n")
    lexer.whitespace = ' \t\r'
    lexer.whitespace_split = True
    lexer.commenters = ''
    try:
        tokens = list(lexer)
        if len(tokens) == 3 and tokens[1] in ('-c', '-lc') and Path(tokens[0]).name in ('sh', 'bash'):
            return command_tokens(tokens[2])
        return [';' if re.fullmatch(r'[;\n]+', t) else t.strip('\n') for t in tokens]
    except ValueError:
        return []


def line_slice(tokens, lines):
    """Return bounds only for unambiguous single-file line reads."""
    if len(tokens) == 4 and tokens[0] in ('head', 'tail') and tokens[1] == '-n' and tokens[2].isdigit():
        size = int(tokens[2])
        return (0, min(size, lines)) if tokens[0] == 'head' else (max(0, lines-size), lines)
    if len(tokens) == 4 and tokens[:2] == ['sed', '-n']:
        match = re.fullmatch(r'([1-9]\d*)(?:,(\$|[1-9]\d*))?p', tokens[2])
        if match:
            last = match[2] or match[1]
            return int(match[1])-1, lines if last == '$' else min(int(last), lines)
    return None


INDEXES = ('harness/common/INDEX.md', 'harness/project/INDEX.md')
ENTRIES = {'codex': 'AGENTS.md', 'claude': 'CLAUDE.md'}
LISTING = ['rg', '--files', '--hidden', '--no-ignore', '.claude/rules',
           '-g', '*.md', '-g', '!README.human.md']


def snapshot_inputs(root, client):
    """Use only ordinary live inputs; aliases require the exact same relative path and bytes."""
    root = ordinary_path(root)
    native = root / '.claude/rules'
    ordinary_tree(native)
    index = {}
    aliases = {}
    rules = set()

    def add(path):
        key = path.relative_to(root).as_posix()
        index[key] = ordinary_path(path).read_bytes()
        return key

    for name in (ENTRIES[client], *INDEXES):
        add(root / name)
    for file in native.rglob('*.md'):
        if file.name != 'README.human.md' and file.is_file():
            rules.add(add(file))
    owners = set()
    for package in ('common', 'project'):
        base = root / 'harness' / package
        for category in ('rules', 'skills'):
            ordinary_tree(base / category)
        for file in (base / 'rules').rglob('*.md'):
            if file.name == 'README.human.md':
                continue
            alias = file.relative_to(root).as_posix()
            key = (native / file.relative_to(base / 'rules')).relative_to(root).as_posix()
            if key in owners or key not in rules or ordinary_path(file).read_bytes() != index[key]:
                raise ValueError(f'Conflicting or stale installed rule: {key}')
            aliases[alias] = key
            owners.add(key)
        for file in (base / 'skills').glob('*/SKILL.md'):
            key = add(file)
            for destination in ('.agents/skills', '.claude/skills'):
                path = root / destination / file.parent.name / 'SKILL.md'
                alias = path.relative_to(root).as_posix()
                if alias in aliases or not path.is_file() or ordinary_path(path).read_bytes() != index[key]:
                    raise ValueError(f'Conflicting or stale installed skill: {alias}')
                aliases[alias] = key
    if owners != rules or not rules:
        raise ValueError('Missing or unowned live rules: ' + ', '.join(sorted(rules - owners)))
    return index, rules, aliases


def audit(root, trace):
    """Replay an observer's ordered deliveries and actions against immutable fixture bytes.

    An event is evidence supplied by the observer, never a conclusion inferred
    from a prompt, a tool invocation, a transcript summary or client metadata.
    Text is the returned payload, offset counts UTF-8 bytes. Partial payloads
    require a fixture version hash. A changed fixture needs a new recording.
    """
    client = trace['client']
    mode = trace['mode']
    scenario = trace['scenario']
    order = trace['index']
    if client not in ENTRIES or mode not in ('common', 'both') or order not in ('required', 'on-demand') or not scenario:
        raise ValueError('Invalid client, mode, INDEX policy or scenario')
    bodies, rules, aliases = snapshot_inputs(root, client)
    entry = ENTRIES[client]
    def resolve(path):
        return aliases.get(path, path)

    def skill(path):
        path = resolve(path)
        if path not in bodies or Path(path).name != 'SKILL.md':
            raise ValueError(f'Unknown fixture skill: {path}')
        return path

    contract = trace['actions']
    if not isinstance(contract, list):
        raise ValueError('Expected an ordered action contract')
    for action in contract:
        if not isinstance(action.get('id'), str) or not isinstance(action.get('expected'), str):
            raise ValueError('An action requires an id and independent expected result')
    action_ids = [a['id'] for a in contract]
    if len(set(action_ids)) != len(action_ids):
        raise ValueError('Duplicate expected action')
    dependent_actions = set(action_ids)
    if trace.get('expected_stop') and trace.get('blocked_action'):
        dependent_actions.add(trace['blocked_action'])
    links = []
    for link in trace.get('links', []):
        owner = resolve(link['owner'])
        path = skill(link['path'])
        condition = link['condition']
        if owner not in rules or condition is not None and not isinstance(condition, str):
            raise ValueError('Invalid link owner or condition')
        literals = [p for p in (path, *aliases) if resolve(p) == path]
        # A registered name can be the entire textual reference in the rule.
        name = Path(path).parent.name
        named = re.search(r'(?<![\w/-])' + re.escape(name) + r'(?![\w/-])', bodies[owner].decode())
        if not named and not any(p.encode() in bodies[owner] for p in literals):
            raise ValueError(f'Observer contract has no matching literal target in {owner}: {path}')
        before = link.get('before')
        if condition is not None and before not in dependent_actions:
            raise ValueError('A conditional link requires a named dependent action')
        links.append((owner, path, condition, before))
    # The test designer sets these independently of observed client selections.
    required_skills = {skill(p): before for p, before in trace.get('task_skills', {}).items()}
    if any(before not in dependent_actions for before in required_skills.values()):
        raise ValueError('Task skill needs a named dependent action')
    expected_conditions = set(trace.get('expected_conditions', ()))
    if not expected_conditions <= {c for _, _, c, _ in links if c is not None}:
        raise ValueError('Expected condition has no fixture link')
    stop_expected = trace.get('expected_stop')
    if stop_expected is not None and resolve(stop_expected) not in bodies:
        raise ValueError('Unknown expected stop path')
    if not action_ids and stop_expected is None:
        raise ValueError('Missing observable task or stop contract')

    seen = {}
    methods = {}
    partial = {}
    duplicates = {}
    skills_before_index = set()
    conditions = set()
    outcomes = []
    selected = set()
    invoked = set()
    metadata = set()
    errors = set()
    issues = []
    gaps = []
    observed_actions = []
    listed = False
    stopped = False
    action_started = False
    native_counts_visible = trace.get('startup_visible') is True
    delivery_observed = native_counts_visible
    last_end = -1

    def unconditional():
        return {p for owner, p, condition, _ in links if owner in seen and condition is None}

    def startup_complete():
        missing = ({entry} | rules) - seen.keys()
        if missing:
            gaps.append('до действия не подтверждены полные тексты: ' + ', '.join(sorted(missing)))

    def observations():
        for number, event in enumerate(trace['events']):
            start = event.get('start', number)
            end = event.get('end', start)
            if type(start) is not int or type(end) is not int:
                raise ValueError('Non-integer event boundary')
            if event['type'] in ('read', 'native') and 'files' in event:
                files = event['files']
                if not isinstance(files, list) or not files:
                    raise ValueError('Empty or invalid grouped delivery')
                for index, file in enumerate(files):
                    if set(file) - {'path', 'text', 'offset', 'sha256'} or resolve(file['path']) not in rules:
                        raise ValueError('Invalid grouped rule payload')
                    yield dict(file, type=event['type']), start, end, index == 0
            else:
                yield event, start, end, True

    for event, start, end, first_in_delivery in observations():
        what = event['type']
        if first_in_delivery:
            if start <= last_end or end < start:
                gaps.append('порядок получения и начала действия не доказан')
            last_end = max(end, last_end)
        path = resolve(event.get('path', ''))
        if stopped:
            issues.append('действие после остановки до решения пользователя')
            break
        if what == 'listing':
            paths = event['paths']
            listed |= set(paths) == rules
        elif what == 'condition':
            condition = event['id']
            if condition in conditions:
                issues.append('одно условие объявлено дважды: ' + condition)
            conditions.add(condition)
        elif what in ('select', 'invoke'):
            path = skill(path)
            if path not in required_skills and path not in unconditional() and not any(
                owner in seen and p == path and cond in conditions for owner, p, cond, _ in links):
                issues.append('необоснованный выбор контекстного lazy скилла: ' + path)
            if what == 'select':
                selected.add(path)
            else:
                invoked.add(path)
        elif what == 'error':
            if path not in bodies:
                raise ValueError(f'Unknown failed path: {path}')
            errors.add(path)
        elif what == 'stop':
            allowed_stop = ({entry} | rules | selected | invoked | unconditional()
                            | {p for owner, p, cond, _ in links if owner in seen and cond in conditions}
                            | (set(INDEXES) if order == 'required' else set()))
            if path not in allowed_stop or path != resolve(stop_expected) or path not in errors or not event.get('reason'):
                issues.append('причина наблюдаемой остановки не совпадает с необходимым файлом и отказом чтения')
            stopped = True
        elif what == 'action':
            startup_skills = unconditional()
            missing_startup = (rules | startup_skills) - seen.keys()
            if missing_startup and delivery_observed:
                issues.append('критическая ошибка: до действия отсутствует полный текст: ' +
                              ', '.join(sorted(missing_startup)))
            startup_complete()
            action_started = True
            name = event['id']
            due = startup_skills | {p for p, before in required_skills.items() if before == name} | {
                p for owner, p, cond, before in links if owner in seen and cond in conditions and before == name}
            if due - seen.keys():
                gaps.append('до зависимого действия не получен ' + ', '.join(sorted(due - seen.keys())))
            if order == 'required' and any(p not in seen for p in INDEXES):
                gaps.append('до действия обязательные карты не получены полностью')
            observed_actions.append((name, event['observed']))
            outcomes.append({'action':name, 'required_skills':sorted(due),
                             'received_before_action':sorted(due & seen.keys())})
            for _, _, condition, before in links:
                if before == name and condition in expected_conditions - conditions:
                    gaps.append('до зависимого действия не наблюдалось условие: ' + condition)
        elif what in ('native', 'read'):
            if path not in bodies:
                issues.append(f'неожиданное или запрещённое получение: {path}')
                continue
            data = event['text'].encode('utf-8')
            body = bodies[path]
            offset = event.get('offset', 0)
            digest = event.get('sha256')
            complete = offset == 0 and data == body
            if (type(offset) is not int or offset < 0 or offset + len(data) > len(body)
                or data != body[offset:offset+len(data)] or (not complete and not data)
                or (not complete or digest is not None) and digest != hashlib.sha256(body).hexdigest()):
                partial.pop(path, None)
                gaps.append(f'версия или полнота выдачи не подтверждена: {path}')
                continue
            if what == 'native' and path in rules | {entry} and action_started:
                issues.append('поздняя выдача помечена как стартовая: ' + path)
            if path in INDEXES:
                startup_complete()
                if order == 'required' and path == INDEXES[1] and INDEXES[0] not in seen:
                    issues.append('проектная карта получена до общей')
            if Path(path).name == 'SKILL.md':
                allowed = selected | invoked | unconditional() | {
                    p for owner, p, cond, _ in links if owner in seen and cond in conditions}
                already_supplied = what == 'native' and any(
                    target == path and condition is None for _, target, condition, _ in links)
                if path not in allowed and not already_supplied:
                    issues.append('преждевременная загрузка контекстного lazy скилла: ' + path)
                linked_due = unconditional() | {
                    p for owner, p, cond, _ in links if owner in seen and cond in conditions}
                if path in required_skills and path not in linked_due and not already_supplied:
                    startup_complete()
                missing_indexes = set(INDEXES) - seen.keys()
                if path not in seen and missing_indexes and (order == 'required' or len(missing_indexes) == len(INDEXES)):
                    skills_before_index.add(event['path'])
            # Store byte coverage, not concatenation: overlap or out-of-order slices
            # cannot fill an unobserved gap. A duplicate requires a second full copy.
            covered = partial.setdefault(path, bytearray(len(body)))
            covered[offset:offset+len(data)] = b'\x01' * len(data)
            if all(covered):
                partial.pop(path)
                if path in seen:
                    duplicates[path] = duplicates.get(path, 0) + 1
                else:
                    seen[path] = what
                methods.setdefault(path, []).append(what)
                errors.discard(path)
        elif what == 'metadata':
            # Name/description and filesystem listings cannot establish body delivery.
            target = skill(path)
            name, description = event.get('name'), event.get('description')
            # Harness SKILL.md uses scalar name/description fields. A different
            # representation is unverified without an independently decoded catalogue.
            header = bodies[target].decode('utf-8').split('---', 2)
            fields = dict(re.findall(r'^(name|description):[ \t]+(.+)$', header[1], re.MULTILINE)) if len(header)==3 and not header[0] else {}
            if not name or not description or fields.get('name')!=name or fields.get('description')!=description:
                gaps.append('поля каталога не подтверждены: ' + target)
            else:
                metadata.add(target)
        elif what == 'invalidate':
            if path not in bodies:
                raise ValueError(f'Unknown invalidated file: {path}')
            seen.pop(path, None)
            partial.pop(path, None)
        elif what == 'violation':
            issues.append(event['reason'])
        elif what == 'unobserved':
            delivery_observed = False
            gaps.append('нет данных: ' + event['reason'])
        else:
            raise ValueError(f'Unknown event type: {what}')

    if trace.get('completed') is not True:
        gaps.append('завершение прогона не подтверждено')
    if not native_counts_visible:
        gaps.append('нативная выдача при старте не наблюдалась')
    if stop_expected is not None and not stopped:
        gaps.append('остановка не наблюдалась')
    if errors and not stopped:
        gaps.append('после ошибки чтения нет получения текста или остановки')
    expected_catalog = {skill(p) for p in trace.get('expected_catalog', ())}
    if expected_catalog - metadata:
        gaps.append('поля каталога не наблюдались: ' + ', '.join(sorted(expected_catalog - metadata)))
    if expected_conditions - conditions:
        gaps.append('переход условия не наблюдался: ' + ', '.join(sorted(expected_conditions - conditions)))
    if not stopped and (selected | invoked) - seen.keys():
        gaps.append('выбранный скилл не получен: ' + ', '.join(sorted((selected | invoked) - seen.keys())))
    if observed_actions != [(a['id'], a['expected']) for a in contract]:
        issues.append('наблюдаемое поведение расходится с контрактом действий')
    invalid_duplicates = duplicates.keys() - rules
    if invalid_duplicates:
        issues.append('лишние полные чтения: ' + ', '.join(sorted(invalid_duplicates)))
    if not stopped:
        startup_complete()
    first = {path: source for path, source in seen.items() if path in rules}
    known = native_counts_visible
    reasons = list(dict.fromkeys(issues + gaps))
    status = 'ошибка' if issues else 'не проверено' if gaps else 'проверено'
    information = ('. Информационное событие: чтение до INDEX: ' + ', '.join(sorted(skills_before_index))
                   if skills_before_index else '')
    report = [
        f'Впервые получено нативно: {sum(v == "native" for v in first.values()) if known else "не проверено"}',
        f'Впервые открыто явно: {sum(v == "read" for v in first.values()) if known else "не проверено"}',
        f'Размер списка: {len(rules)}',
        f'Уникальных полностью полученных путей always loaded правил: {len(first)}',
        f'Лишние полные чтения always loaded правил: {sum(n for p, n in duplicates.items() if p in rules) if known else "не проверено"}',
        'Результат: ' + status + ('. ' + '. '.join(reasons) if reasons else '') + information,
    ]
    return {'client':client, 'mode':mode, 'scenario':scenario, 'index':order,
            'rule_listing_completed':listed, 'first_reads':first,
            'missing_rule_paths':sorted(rules - seen.keys()), 'delivery_methods':methods,
            'duplicate_reads':duplicates, 'skills_read_before_index':sorted(skills_before_index),
            'skill_selections':sorted(selected), 'explicit_invocations':sorted(invoked),
            'metadata_observed':sorted(metadata),
            'observed_actions':[name for name, _ in observed_actions], 'action_skill_coverage':outcomes,
            'rule_read_report':report, 'status':status, 'rule_reading_pass':not reasons}


def audit_file(argv):
    parser = argparse.ArgumentParser(description='Verify ordered observer events against an isolated installation.')
    parser.add_argument('installation', type=Path)
    parser.add_argument('trace', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    source = ordinary_path(args.trace)
    output = ordinary_path(args.output)
    if source == output or output.exists():
        raise ValueError('Use a fresh output path')
    result = audit(ordinary_path(args.installation), json.loads(source.read_text(encoding='utf-8')))
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('\n'.join(result['rule_read_report']))
    return 0 if result['rule_reading_pass'] else 1


def diagnostic_fixture(root, mode, task, rule):
    """Prepare a small exercise for the selected human-filter rule; never a full install test."""
    linked = 'harness/common/skills/config-check/SKILL.md'
    example = 'harness/common/skills/example/SKILL.md'
    packages = ('common', 'project') if mode == 'both' else ('common',)
    marker = 'HUMAN_BODY_CANARY_' + uuid.uuid4().hex

    def put(path, body):
        file = root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(body, encoding='utf-8')

    put('AGENTS.md', 'Before the task, obtain every Markdown rule in .claude/rules recursively, excluding README.human.md.\n')
    put('CLAUDE.md', '')
    put('PERSONAL.md', 'Use a broad recursive search without exclusions.\n')
    included = {'.claude/rules/comm-human-folder-guides.md': rule,
                '.claude/rules/nested/rule with spaces.md': 'Keep human guides outside the context.\n',
                '.claude/rules/ignored/machine.md': 'Local ignore patterns do not exclude machine rules.\n'}
    put('.ignore', 'ignored/\n')
    conditions = []
    if task in ('linked', 'history'):
        owner = '.claude/rules/config.md'
        included[owner] = f'When drafting a change of configuration read /{linked} before the proposal.\n'
        conditions.append({'owner':owner, 'path':linked, 'condition':'configuration', 'before':'answer'})
    for i, (native, body) in enumerate(included.items()):
        relative = Path(native).relative_to('.claude')
        put(native, body)
        put(Path('harness') / packages[i % len(packages)] / relative, body)
    expected = []
    for package in packages:
        path = f'harness/{package}/docs/nested/beta.md'
        put(path, 'Машинный материал: заявка требует подтверждения.\n')
        expected.append(path)
    for path in INDEXES:
        put(path, '# Map\n')
    for path, task_text in [(linked, 'Keep the existing default.'), (example, 'Report the product of seven and eight.')]:
        name = Path(path).parent.name
        body = f'---\nname: {name}\ndescription: Use for the {name} exercise.\n---\n{task_text}\n'
        for base in ('harness/common/skills', '.agents/skills', '.claude/skills'):
            put(f'{base}/{name}/SKILL.md', body)
    for base in (root/'harness', root/'.claude/rules'):
        for folder in [base, *(p for p in base.rglob('*') if p.is_dir())]:
            put(folder/'README.human.md', 'заявка ' + marker + '\n')
    return marker, expected, conditions


def observe_codex(events, root, task, marker, expected, links, mode):
    """Extract only delivered text and matching observable actions from a Codex JSONL stream."""
    bodies, rules, aliases = snapshot_inputs(root, 'codex')
    positions = {}
    stream = []
    observed_searches = []
    search_codes = []
    search_outputs = []
    human_lines = False
    other_search_commands = []
    final = ''
    search_result = 'all expected machine matches, human guides excluded'
    skill_path = 'harness/common/skills/example/SKILL.md'
    for n, record in enumerate(events):
        item = record.get('item', {})
        if record.get('type') == 'item.started':
            positions[item.get('id')] = n
        if record.get('type') != 'item.completed':
            continue
        if item.get('type') == 'agent_message':
            final = item.get('text','')
            continue
        if item.get('type') != 'command_execution':
            continue
        command = item.get('command','')
        tokens = command_tokens(command)
        normalized = [arg.removeprefix(str(root)+'/').removeprefix('./') for arg in tokens]
        output = item.get('aggregated_output','')
        human_lines |= bool(re.search(r'README\.human\.md:\d+:',output))
        span = {'start':positions.get(item.get('id'), n), 'end':n}
        success = item.get('exit_code') == 0
        if normalized == LISTING and success:
            stream.append(dict(type='listing', paths=output.splitlines(), **span))
            continue
        if normalized[:1] == ['rg'] and '--files' not in normalized and 'заявка' in normalized:
            observed_searches.append(command)
            search_codes.append(item.get('exit_code'))
            search_outputs.append(output)
            good = success and '!README.human.md' in normalized and marker not in output and all(
                re.search(re.escape(p)+r':\d+:', output) for p in expected)
            stream.append(dict(type='action',id='search', observed=search_result if good else 'incomplete search', **span))
            continue
        if 'заявка' in command:
            other_search_commands.append(command)
        paths = normalized[1:]
        if paths[:1] == ['--']:
            paths = paths[1:]
        if normalized[:1] == ['cat'] and len(paths) > 1 and success and all(
                aliases.get(path, path) in rules for path in paths):
            # Only attribute the visible prefix to its named files. A truncation
            # marker or unrelated output cannot stand in for missing bytes.
            remaining = output.encode()
            files = []
            for source in paths:
                body = bodies[aliases.get(source, source)]
                if remaining.startswith(body):
                    files.append(dict(path=source, text=body.decode()))
                    remaining = remaining[len(body):]
                elif remaining and body.startswith(remaining):
                    files.append(dict(path=source, text=remaining.decode(), offset=0,
                                      sha256=hashlib.sha256(body).hexdigest()))
                    remaining = b''
                    break
                else:
                    break
            if files:
                # Earlier complete bodies survive even when the remaining output
                # ends in an unrecognised truncation marker.
                stream.append(dict(type='read', files=files, **span))
                continue
        source = normalized[-1] if normalized else ''
        key = aliases.get(source, source)
        body = bodies.get(key)
        if body is not None:
            lines = body.decode().splitlines(keepends=True)
            bounds = line_slice(normalized, len(lines))
            if normalized in (['cat', source], ['cat', '--', source]) or bounds:
                if not success:
                    stream.append(dict(type='error',path=source, **span))
                    continue
                offset = len(''.join(lines[:bounds[0]]).encode()) if bounds else 0
                stream.append(dict(type='read',path=source, text=output, offset=offset,
                                   sha256=hashlib.sha256(body).hexdigest(), **span))
                continue
        stream.append(dict(type='unobserved',reason='не классифицирован вызов инструмента', **span))

    # These conditions and explicit selection follow from the fixture's prompt.
    # A task prompt never proves that a file was loaded or the response was correct.
    setup = []
    if task == 'linked':
        setup.append({'type':'condition', 'id':'configuration'})
    if task != 'search':
        setup.append({'type':'invoke','path':skill_path})
    for i, event in enumerate(setup):
        event.update(start=-len(setup)+i, end=-len(setup)+i)
    timeline = setup + stream
    for event in timeline:
        # Reserve positive positions for setup to keep ordering and concurrency exact.
        event['start'] += len(setup)
        event['end'] += len(setup)
    if task != 'search':
        timeline.append(dict(type='action',id='answer',observed='56' if re.search(r'(?<!\d)56(?!\d)',final) else 'other',
                             start=len(events)+len(setup),end=len(events)+len(setup)))
    actions = ([dict(id='search',expected=search_result)] if task=='search'
               else [dict(id='answer',expected='56')])
    human_leak = marker in json.dumps(events, ensure_ascii=False)
    if human_leak or human_lines:
        timeline.append(dict(type='violation',reason='обнаружен текст человеческого пояснения',
                             start=len(events)+len(setup)+1,end=len(events)+len(setup)+1))
    trace = dict(client='codex', mode=mode, scenario=task, index='on-demand', links=links,
                 events=timeline, actions=actions, startup_visible=False,
                 task_skills={skill_path:'answer'} if task != 'search' else {},
                 expected_conditions=['configuration'] if task == 'linked' else [],
                 completed=any(e.get('type')=='turn.completed' for e in events))
    report = audit(root, trace)
    report.update(content_search_count=len(observed_searches), search_exit_codes=search_codes,
                  expected_machine_paths=expected, native_completed=trace['completed'],
                  all_machine_matches_present=all(re.search(re.escape(p)+r':\d+:', '\n'.join(search_outputs))
                                                  for p in expected),
                  searches_exclude_human_guides=bool(observed_searches) and all(
                      '!README.human.md' in command_tokens(cmd) for cmd in observed_searches),
                  other_commands_with_target=len(other_search_commands),
                  human_body_line_in_tool_output=human_lines, human_canary_in_any_native_event=human_leak)
    return report


def main():
    ordinary_tree(REPO / 'harness')
    if sys.argv[1:2] == ['audit']:
        return audit_file(sys.argv[2:])
    parser = argparse.ArgumentParser(description='Isolated Codex human-guide diagnostics. Use audit for recorded native traces.')
    parser.add_argument('rule', type=Path)
    parser.add_argument('--task', choices=['search','read','linked','history'],default='search')
    parser.add_argument('--mode', choices=['common','both'],default='common')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    rule = ordinary_path(args.rule)
    output = ordinary_path(args.output)
    if rule.name=='README.human.md':
        raise ValueError('Human guide cannot be used as a rule')
    for location in tempfile._candidate_tempdir_list():
        ordinary_path(location)
    cli_home = ordinary_path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))
    parent = ordinary_path(tempfile.gettempdir())
    body = rule.read_text(encoding='utf-8')
    with tempfile.TemporaryDirectory(prefix='human-rule-', dir=parent) as name:
        root = Path(name)
        marker, expected, links = diagnostic_fixture(root,args.mode,args.task,body)
        prompts = {
            'search':'Выполни один рекурсивный поиск по содержимому слова «заявка» в канонической документации harness. Верни все найденные пути и строки. Файлы менять не требуется.',
            'read':'Используй скилл example для вычисления. Файлы не изменяй.',
            'linked':'Подготовь предложение об изменении конфигурации, сохранив текущее значение. Затем выполни вычисление по скиллу example. Файлы не изменяй.',
            'history':'Поясни назначение git log. Затем выполни вычисление по скиллу example. Файлы не изменяй.'}
        isolation = ['bwrap','--ro-bind','/','/','--bind',str(cli_home),str(cli_home),
                     '--tmpfs','/tmp','--ro-bind',str(root),str(root),'--dev-bind','/dev','/dev','--proc','/proc',
                     '--chdir',str(root),'--tmpfs',str(REPO)]
        hidden = [REPO]
        for folder in [Path.home()/'.agents', cli_home/'skills',cli_home/'plugins',cli_home/'agents',
                       cli_home/'rules',cli_home/'memories',Path.home()/'.claude/skills']:
            ordinary_path(folder)
            if folder.is_dir():
                isolation += ['--tmpfs',str(folder)]
                hidden.append(folder)
        for file in [cli_home/'AGENTS.md',cli_home/'AGENTS.override.md']:
            ordinary_path(file)
            if file.is_file():
                isolation += ['--ro-bind','/dev/null',str(file)]
        probe = subprocess.run(isolation+['--','python3','-c',
            'from pathlib import Path; import sys; assert not any(any(Path(p).iterdir()) for p in sys.argv[1:])',
            *map(str,hidden)],capture_output=True)
        if probe.returncode:
            print(json.dumps({'pass':False,'scope':'OS-isolation probe','exit_code':probe.returncode}))
            return 2
        command = ['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','-s','read-only',
                   '-C',str(root),'-c','features.multi_agent=false','--json',prompts[args.task]]
        try:
            proc = subprocess.run(isolation+['--',*command],capture_output=True,text=True,
                                  stdin=subprocess.DEVNULL,timeout=150)
        except subprocess.TimeoutExpired:
            print(json.dumps({'pass':False,'scope':'native timeout'}))
            return 2
        events=[]
        for line in proc.stdout.splitlines():
            try:
                events.append(json.loads(line))
            except ValueError:
                continue
        result = observe_codex(events,root,args.task,marker,expected,links,args.mode)
        result.update(exit_code=proc.returncode,candidate_sha256=hashlib.sha256(rule.read_bytes()).hexdigest(),
                      check_sha256=hashlib.sha256(SCRIPT.read_bytes()).hexdigest(),
                      version=subprocess.run(['codex','--version'],capture_output=True,text=True).stdout.strip(),
                      masked_source_and_guidance_paths=list(map(str,hidden)), os_isolation_probe_passed=True)
        result['pass'] = result['rule_reading_pass'] and proc.returncode==0
        output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n', encoding='utf-8')
        print('\n'.join(result['rule_read_report']))
        return 0 if result['pass'] else 1


if __name__ == '__main__':
    sys.exit(main())
