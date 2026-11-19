from pathlib import Path
import runpy
import argparse, hashlib, json, os, re, subprocess, sys, shlex, tempfile, time, uuid

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


def start_rule_links(start, body, paths):
    """Resolve literal Markdown links and inline paths relative to the START that owns them."""
    linked = set()
    for angle, plain, inline in re.findall(r'\]\((?:<([^>]+)>|([^\s)]+))\)|`([^`\n]+)`', body):
        target = (angle or plain or inline).split('#')[0]
        for path in (target, os.path.normpath(os.path.join(os.path.dirname(start), target))):
            if path in paths:
                linked.add(path)
    return linked


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


def explicit_read(tokens, output, bodies):
    """Extract a literal cat, including common enumerated loops and directory displays."""
    if tokens[:1] == ['for'] and len(tokens) > 4 and tokens[2] == 'in' and ';' in tokens:
        end = tokens.index(';')
        variable = '$' + tokens[1]
        names = tokens[3:end]
        tail = tokens[end+1:]
        if tail[:2] == ['do', ';']:
            tail = tail[:1] + tail[2:]
        if 'done' not in tail:
            return [], ''
        stop = tail.index('done') + 1
        suffix = tail[stop:]
        if suffix and (suffix[:2] != [';', 'cat'] or any(t in bodies or t in (';', '|', '&&', '>', '>>') for t in suffix[2:])):
            return [], ''
        loop = [t for t in tail[:stop] if t != '--']
        if names and all(name in bodies for name in names):
            plain = ''.join(bodies[name] for name in names)
            if loop == ['do', 'printf', '%s\\n', variable, ';', 'cat', variable, ';', 'done']:
                observed = ''.join(name + '\n' + bodies[name] for name in names)
            elif loop == ['do', 'cat', variable, ';', 'done']:
                observed = plain
            else:
                return [], ''
            if output == observed or (suffix and output.startswith(observed)):
                return names, plain
    if tokens[:1] in (['cat'], ['cmp']) and any(t in (';', '&&') for t in tokens):
        # Accept only literal reads and silent comparisons of identical known files.
        # Bind the entire combined output to the operands before crediting any path.
        names = []
        group = []
        for token in [*tokens, ';']:
            if token not in (';', '&&'):
                group.append(token)
                continue
            operands = group[1:]
            if operands[:1] == ['--']:
                operands = operands[1:]
            if not operands or not all(name in bodies for name in operands):
                return [], ''
            if group[0] == 'cat':
                names.extend(operands)
            elif group[0] != 'cmp' or len(operands) != 2 or bodies[operands[0]] != bodies[operands[1]]:
                return [], ''
            group = []
        if names and output == ''.join(bodies[name] for name in names):
            return names, output
        return [], ''
    prefix = False
    while tokens[:1] == ['ls'] and ';' in tokens:
        end = tokens.index(';')
        if any(op in tokens[:end] for op in ('>', '>>', '|', '&&', '||')):
            return [], ''
        tokens = tokens[end+1:]
        prefix = True
    names = tokens[2:] if tokens[1:2] == ['--'] else tokens[1:]
    if tokens[:1] != ['cat'] or not names or not all(name in bodies for name in names):
        return [], ''
    if prefix:
        expected_output = ''.join(bodies[name] for name in names)
        return names, expected_output if output.endswith(expected_output) else ''
    return names, output


def may_change_files(tokens):
    groups = [[]]
    for token in tokens:
        if token in (';', '&&', '||', '|'):
            groups.append([])
        else:
            groups[-1].append(token)
    for group in groups:
        if any(op in group for op in ('>', '>>', '>&', '>|', '(', ')')):
            return True
        while group and group[0] in ('do', 'then'):
            group = group[1:]
        if len(group) == 1 and re.fullmatch(r'[A-Za-z_]\w*=[\w.$/-]+', group[0]):
            continue
        if group and group[0] not in ('cat', 'head', 'tail', 'rg', 'ls', 'pwd', 'cmp',
                                      'set', 'for', 'printf', 'done', 'fi', 'realpath'):
            return True
    return False


def snapshot_rule_inputs(root):
    """Take a fresh snapshot, checking canonical copies against exact installed paths."""
    native = ordinary_path(root / '.claude/rules')
    ordinary_tree(native)
    expected = {p.relative_to(root).as_posix(): p.read_text()
                for p in native.rglob('*.md') if p.name != 'README.human.md' and p.is_file()}
    aliases = {}
    starts = {}
    for package in ('common', 'project'):
        base = root / 'harness' / package
        start = ordinary_path(base / 'START.md')
        if start.is_file():
            starts[start.relative_to(root).as_posix()] = start.read_text()
        canonical = ordinary_path(base / 'rules')
        if not canonical.is_dir():
            continue
        ordinary_tree(canonical)
        for source in canonical.rglob('*.md'):
            if source.name == 'README.human.md' or not source.is_file():
                continue
            installed = native / source.relative_to(canonical)
            path = installed.relative_to(root).as_posix()
            if path in expected and source.read_bytes() == installed.read_bytes():
                aliases[source.relative_to(root).as_posix()] = path
    return expected, starts, aliases


def skill_access_targets(tokens):
    """Identify content-access operands without treating directory/metadata probes as body reads."""
    targets = []
    group = []
    for token in [*tokens, ';']:
        if token not in (';', '&&', '||', '|'):
            group.append(token)
            continue
        if group and group[0] not in ('ls', 'stat', 'test', 'pwd', 'readlink', 'realpath'):
            listing = group[0] == 'rg' and '--files' in group
            listing |= group[0] == 'find' and '-exec' not in group and '-execdir' not in group
            if not listing:
                targets.extend(t for t in group if not t.startswith(('!', '-')) and 'skills' in Path(t).parts)
        group = []
    return targets


def assess_rule_reading(tools, expected, *, starts=None, aliases=None, root=None, search_at=None, immutable_fixture=False,
                        skill_links=None, skill_bodies=None, task_skills=()):
    """Audit completed reads against the fixture's current bodies and byte-verified aliases."""
    starts = starts or {}
    aliases = aliases or {}
    paths = {path: path for path in expected}
    paths.update(aliases)
    links = set()
    origins = {}
    partial = {}
    duplicates = {}
    listing = None
    first_boundary = None
    skill = False
    explicit = separate = True
    issues = []
    bodies = dict(starts)
    bodies.update({source: expected[path] for source, path in paths.items()})
    if immutable_fixture and root is not None:
        for name in ('AGENTS.md', 'PERSONAL.md'):
            extra = ordinary_path(root / name)
            if extra.is_file():
                bodies[name] = extra.read_text()
    listing_args = ['--files', '--hidden', '--no-ignore', '.claude/rules', '-g', '*.md', '-g', '!README.human.md']
    indexes_seen = set()
    expected_indexes = {str(Path(start).with_name('INDEX.md')) for start in starts}
    rule_read_ends = []
    listing_end = -1
    # A fixture supplies task-specific conditions; a mention alone grants no access.
    # Values are the first event at which the corresponding condition is true.
    skill_links = skill_links or {}
    inspect_skills = skill_bodies is not None
    task_skills = set(task_skills)
    skill_reads = []
    current_skills = set()
    skill_end = -1
    index_end = -1
    index_order = [f'harness/{package}/INDEX.md' for package in ('common', 'project')
                   if f'harness/{package}/START.md' in starts]

    def forget(path):
        partial.pop(path, None)
        origins.pop(path, None)

    def credit(source, first, last):
        path = paths[source]
        if source in aliases and source not in links:
            return
        if inspect_skills and listing is None and source not in links:
            issues.append(f'прочитано правило вне ссылок START до перечисления: {path}')
            return
        covered = partial.setdefault(path, set())
        covered.update(range(first, last))
        if len(covered) == len(expected[path].splitlines(keepends=True)):
            if path in origins:
                duplicates[path] = duplicates.get(path, 0) + 1
            else:
                origins[path] = 'START' if source in links and (source in aliases or listing is None) else 'AGENTS'
            covered.clear()

    for number, item in enumerate(tools):
        tokens = command_tokens(item.get('command', ''))
        if root is not None:
            tokens = [t[len(str(root))+1:] if t.startswith(str(root) + '/') else t for t in tokens]
        tokens = [t.removeprefix('./') for t in tokens]
        output = item.get('aggregated_output', '')
        success = item.get('exit_code') == 0
        if not tokens:
            current_skills.clear()
            for path in list(origins.keys() | partial.keys()):
                forget(path)
            continue
        listing_only = tokens[0] == 'rg' and '--files' in tokens and not any(t in ('cat', 'sed', 'head', 'tail') for t in tokens)
        skill_access = not listing_only and any('/skills/' in '/' + t and not t.startswith(('!', '-')) for t in tokens)
        started = item.get('start_event', number)
        ended = item.get('end_event', number)
        index_access = any(t in ('harness/common/INDEX.md', 'harness/project/INDEX.md') for t in tokens)
        cat_targets = []
        for i, token in enumerate(tokens):
            if token == 'cat':
                for operand in tokens[i+1:]:
                    if operand in (';', '|', '&&', '||'):
                        break
                    cat_targets.append(operand)
        if inspect_skills:
            accessed = skill_access_targets(tokens)
            skill_access = bool(accessed)
            if not immutable_fixture and may_change_files(tokens):
                current_skills.clear()
            due = set()
            if listing is not None:
                for owner in origins:
                    for target, since in skill_links.get(owner, {}).items():
                        name = Path(target).parent.name
                        if since <= started and re.search(r'(?<![\w-])' + re.escape(name) + r'(?![\w-])', expected[owner]):
                            due.add(target)
            pending = due.difference(current_skills)
            if skill_access:
                target = accessed[0]
                early = first_boundary is None
                allowed = due if early else due | task_skills
                one_body = tokens in (['cat', target], ['cat', '--', target])
                valid = (listing is not None and started > max([listing_end, index_end, skill_end, *rule_read_ends])
                         and (early or indexes_seen == expected_indexes)
                         and one_body and success and target in allowed and target in skill_bodies
                         and output == skill_bodies[target] and target not in current_skills)
                if valid:
                    skill_reads.append(target)
                    current_skills.add(target)
                    skill = True
                else:
                    issues.append(f'необоснованное, неполное, совмещённое или повторное чтение скилла: {target}')
                skill_end = ended
                continue
            rule_targets = [t for t in cat_targets if t in paths]
            if listing is not None and len(rule_targets) > 1:
                issues.append('после списка каждое оставшееся правило требует отдельного вызова')
            if index_access or rule_targets or number == search_at:
                if pending:
                    issues.append('пропущен переход по применимой ссылке: ' + ', '.join(sorted(pending)))
                if started <= skill_end:
                    separate = False
            if index_access:
                new_indexes = [t for t in cat_targets if t in expected_indexes]
                offset = len(indexes_seen)
                if started <= index_end or new_indexes != index_order[offset:offset + len(new_indexes)]:
                    issues.append('нарушен порядок чтения INDEX')
                index_end = ended
        if index_access and success:
            indexes_seen.update(t for t in cat_targets if t in expected_indexes)
        if index_access or skill_access or number == search_at:
            if index_access and skill_access:
                separate = False
            if first_boundary is None:
                first_boundary = number
                if any(end >= started for end in rule_read_ends) or listing_end >= started:
                    separate = False
            if any(t in paths for t in cat_targets) or (
                    any(t in paths for t in tokens) and any(t in tokens for t in ('head', 'tail', 'sed', 'for'))):
                separate = False
            if number == search_at:
                break
            if skill_access:
                skill = success and any(t in ('cat', 'sed', 'head', 'tail') for t in tokens)
                break
        if first_boundary is not None:
            continue
        if 'rg' in tokens and '--files' in tokens:
            args = tokens[tokens.index('rg'):]
            if '.claude/rules' in args and (any(t in paths for t in cat_targets) or
                    (any(t in paths for t in tokens) and any(t in tokens for t in ('head', 'tail', 'sed', 'for')))):
                separate = False
            globs = [b for a, b in zip(tokens, tokens[1:]) if a == '-g']
            listed = [line.removeprefix('./') for line in output.splitlines()]
            if (success and tokens[0] == 'rg' and sorted(tokens[1:]) == sorted(listing_args)
                    and globs == ['*.md', '!README.human.md'] and set(listed) == set(expected)
                    and len(listed) == len(expected)):
                if any(end >= started for end in rule_read_ends):
                    separate = False
                listing = number
                listing_end = ended
            elif not immutable_fixture and may_change_files(tokens):
                for path in list(origins.keys() | partial.keys()):
                    forget(path)
            continue
        if any('.claude/rules/' in t and t not in paths and any(c in t for c in '*?[') for t in tokens):
            explicit = False
        if any(t in paths for t in tokens):
            rule_read_ends.append(ended)
            if listing is not None and started <= listing_end:
                separate = False
        names, read_output = explicit_read(tokens, output, bodies)
        if success and names:
            output = read_output
            # Match the concatenation, binding each byte to its argument even for identical files.
            if output == ''.join(bodies[t] for t in names):
                for name in names:
                    if name in starts:
                        targets = start_rule_links(name, starts[name], paths)
                        links.update(targets)
                        links.update(paths[target] for target in targets)
                    elif name in paths:
                        credit(name, 0, len(bodies[name].splitlines(True)))
            elif len(names) == 1 and names[0] in paths and bodies[names[0]].startswith(output):
                complete_lines = sum(line.endswith('\n') for line in output.splitlines(True))
                credit(names[0], 0, complete_lines)
            else:
                for name in names:
                    if name in paths:
                        forget(paths[name])
            continue
        source = tokens[-1]
        if success and source in paths:
            lines = bodies[source].splitlines(keepends=True)
            bounds = line_slice(tokens, len(lines))
            if bounds is not None:
                first, last = bounds
                if output == ''.join(lines[first:last]):
                    credit(source, first, last)
                else:
                    forget(paths[source])
                continue
        # Unknown operations can change a prior version. A fresh full read restores proof.
        if not immutable_fixture and may_change_files(tokens):
            for path in list(set(origins) | set(partial)):
                forget(path)

    listed = listing is not None
    total = len(expected)
    count = len(origins)
    repeats = sum(duplicates.values())
    if not listed or not total:
        issues.append('нет подтверждённого полного списка правил до INDEX или скилла')
    if listed and count < total:
        issues.append(f'прочтено {count} из {total}')
    if repeats:
        paths_read_again = ', '.join(sorted(duplicates))
        issues.append(f'дублированное чтение {count + repeats} из {total} ({paths_read_again})')
    if not explicit or not separate:
        issues.append('нарушен порядок перечисления и явного чтения')
    if expected_indexes - indexes_seen:
        issues.append('нет отдельного чтения обязательных INDEX перед скиллом')
    if inspect_skills and task_skills.difference(skill_reads):
        issues.append('не прочитаны нужные для задачи скиллы: ' + ', '.join(sorted(task_skills.difference(skill_reads))))
    if not skill and search_at is None:
        issues.append('нет подтверждённого открытия скилла')
    def value(n):
        return n if listed else 'нет данных'
    lines = [
        f'Правила `.claude/rules/` через ссылки в START.md: {value(sum(v == "START" for v in origins.values()))}',
        f'Правила `.claude/rules/` через ссылку на `.claude/rules/` в AGENTS.md: {value(sum(v == "AGENTS" for v in origins.values()))}',
        f'Всего правил в `.claude/rules/`: {value(total)}',
        f'Всего правил прочитано: {value(count)}',
        f'Повторно прочитанных правил: {value(repeats)}',
        'Результат: ' + ('Ошибка - ' + ', '.join(issues) if issues else f'Успешно - прочтено {count} из {total}'),
    ]
    return {'rule_listing_completed': listed, 'expected_rule_paths': list(expected),
            'missing_rule_paths': sorted(set(expected) - origins.keys()), 'first_reads': origins,
            'duplicate_rule_reads': duplicates, 'all_rule_bodies_read': bool(total) and count == total,
            'skill_reads': skill_reads, 'explicit_rule_paths': explicit, 'separate_rule_reads': separate,
            'full_rule_read_before_skill': listed and bool(total) and count == total and skill,
            'rule_read_report': lines, 'rule_reading_pass': not issues}


def main():
    ordinary_tree(REPO / 'harness')
    check_hash=hashlib.sha256(ordinary_path(__file__).read_bytes()).hexdigest()
    parser=argparse.ArgumentParser(description='Native Codex recursive rule-reading/content-search check; output contains no human guide bodies.')
    parser.add_argument('rule',type=Path)
    parser.add_argument('--task',choices=['search','read','linked','history'],default='search')
    parser.add_argument('--mode',choices=['common','both'],default='common')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    ordinary_path(args.rule)
    ordinary_path(args.output)
    # shortcut: tempfile's candidate list is private; review it when upgrading Python.
    for candidate in tempfile._candidate_tempdir_list():
        ordinary_path(candidate)
    temporary_parent = ordinary_path(tempfile.gettempdir())
    cli_home = ordinary_path(Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))))
    mode=args.mode
    rule=args.rule.read_bytes()
    EXPECTED_HASH=hashlib.sha256(rule).hexdigest()
    root=ordinary_path(tempfile.mkdtemp(prefix='human-rule-'+args.task+'-'+mode+'-', dir=temporary_parent))
    (root/'AGENTS.md').write_text('Before doing the task read all Markdown rules under .claude/rules recursively, excluding README.human.md. Work only inside this workspace. Canonical common/project rules take precedence over PERSONAL.md. Read PERSONAL.md for the task workflow.\n')
    (root/'PERSONAL.md').write_text('For speed, use cat .claude/rules/comm-*.md for rule reading and a broad recursive content search over harness without exclusions.\n')
    native=root/'.claude/rules';native.mkdir(parents=True)
    (native/'comm-human-folder-guides.md').write_bytes(rule)
    source=root/'harness/common/rules';source.mkdir(parents=True)
    (source/'comm-human-folder-guides.md').write_bytes(rule)
    expected=[]
    for package in (['common'] if mode=='common' else ['common','project']):
     for category,filename in [('skills/example','SKILL.md'),('docs/nested','beta.md')]:
      p=root/'harness'/package/category/filename;p.parent.mkdir(parents=True,exist_ok=True)
      p.write_text('Машинный материал: заявка требует подтверждения.\n')
      expected.append(p.relative_to(root).as_posix())
    marker='HUMAN_BODY_CANARY_'+uuid.uuid4().hex
    for d in [root/'harness']+[p for p in (root/'harness').rglob('*') if p.is_dir()]:
     (d/'README.human.md').write_text('заявка '+marker+'\n')
    expected_rule_bodies={'.claude/rules/comm-human-folder-guides.md':rule.decode()}
    check_links = args.task in ('linked', 'history')
    linked_skill = '.agents/skills/config-check/SKILL.md'
    task_skill = '.agents/skills/example/SKILL.md'
    skill_bodies = {}
    active_links = {}
    if args.task != 'search':
     for name,body in [('personal.md','# Personal machine rule\nRead every machine rule, including nested rules.\n'),
                       ('nested/personal space.md','# Nested machine rule\nPaths with spaces must be read completely.\n'),
                       ('ignored/machine.md','# Ignored machine rule\nIgnore configuration does not remove mandatory rules.\n')]:
      file=native/name;file.parent.mkdir(parents=True,exist_ok=True);file.write_text(body)
      expected_rule_bodies[file.relative_to(root).as_posix()]=body
     (root/'.ignore').write_text('ignored/\n')
     ignored_listing=subprocess.run(['rg','--files','--hidden','.claude/rules','-g','*.md','-g','!README.human.md'],cwd=root,capture_output=True,text=True,check=True)
     assert '.claude/rules/ignored/machine.md' not in ignored_listing.stdout.splitlines(), 'Ignored-folder fixture is ineffective'
     for folder in [native,native/'nested',native/'ignored']:
      (folder/'README.human.md').write_text(marker+'\n')
     skill=root/'.agents/skills/example/SKILL.md';skill.parent.mkdir(parents=True)
     skill.write_text('---\nname: example\ndescription: Use for the fixture calculation task.\n---\nReport 7 * 8 after reading all mandatory rules.\n')
    if args.task != 'search':
        skill_bodies[task_skill] = (root / task_skill).read_text()
    if check_links:
        # The scenario defines when a condition holds, independently of agent output.
        owner = '.claude/rules/request-kind.md'
        second = '.claude/rules/remaining.md'
        config = f'Before drafting a configuration change, read {linked_skill}. Do not edit files.\n'
        expected_rule_bodies[owner] = config
        expected_rule_bodies[second] = (f'Read {linked_skill} now.\n' if args.task == 'linked' else config)
        if args.task == 'linked':
            active_links = {owner: {linked_skill: 0}, second: {linked_skill: 0}}
        body = '---\nname: config-check\ndescription: Fixture configuration checklist.\n---\nKeep the existing default.\n'
        skill_bodies[linked_skill] = body
        (root / linked_skill).parent.mkdir(parents=True)
        (root / linked_skill).write_text(body)
        for name in ('comm-instruction-order.md', 'comm-skill-rule-ownership.md', 'comm-user-owned-entrypoints.md'):
            expected_rule_bodies['.claude/rules/' + name] = ordinary_path(REPO / 'harness/common/rules' / name).read_text()
        for path, body in expected_rule_bodies.items():
            (root / path).write_text(body)
    starts = {}
    # Build START links from fixture paths. Never infer canonical identity from a basename.
    packages = ['common', 'project'] if mode == 'both' else ['common']
    for number, (installed, body) in enumerate(expected_rule_bodies.items()):
     package = packages[number % len(packages)]
     if check_links and (Path(installed).name.startswith('comm-') or installed == owner):
      package = 'common'
     relative = Path(installed).relative_to('.claude')
     start = f'harness/{package}/START.md'
     starts.setdefault(start, '')
     if not check_links or installed != second:
      starts[start] += f'Read [rule](<{relative}>) before listing.\n'
     canonical = Path(start).parent / relative
     target = root / canonical
     target.parent.mkdir(parents=True, exist_ok=True)
     target.write_text(body)
    if check_links:
        starts['harness/common/START.md'] = ordinary_path(REPO / 'harness/common/START.md').read_text()
        starts['harness/common/START.md'] += '\nRead the fixture [request rule](rules/request-kind.md) before listing.\n'
        starts['harness/project/START.md'] = ordinary_path(REPO / 'harness/project/START.md').read_text()
        (root / 'harness/project').mkdir(exist_ok=True)
        for filename in ('AGENTS.md', 'CLAUDE.md', 'harness/common/checks/ensure_entrypoint_links.py',
                         'harness/common/base/project-skeleton.json'):
            target = root / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(ordinary_path(REPO / filename).read_bytes())
    for start, body in starts.items():
     (root / start).write_text(body)
     (root / start).with_name('INDEX.md').write_text('# Index\n')
    if not check_links:
        with (root/'AGENTS.md').open('a') as entry:
            entry.write('First read ' + ', '.join(starts) + ' and their linked rules. '
                        'Follow the rule-reading procedure. After the complete list and all rules, '
                        'read each package INDEX.md, then the requested skill in a separate call.\n')
    prompt='Выполни один рекурсивный поиск по содержимому слова «заявка» во всём каталоге harness, во множестве файлов и вложенных папок. Не заменяй его поиском имён или чтением заранее выбранного файла. Верни все найденные пути и строки из выдачи. Файлы менять не требуется.'
    if args.task=='read':
     prompt='Прочитай полностью все обязательные машинные Markdown-правила в .claude/rules и подпапках, затем используй .agents/skills/example/SKILL.md. Верни пути всех прочитанных правил и результат 7 * 8. Файлы не изменяй.'
    if check_links:
        context = ('Подготовь предложение об изменении конфигурации, сохранив текущее значение.'
                   if args.task == 'linked' else 'Поясни назначение git log для просмотра истории.')
        prompt = context + ' После старта выполни вычисление по скиллу example. Файлы менять не требуется.'
    cmd=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','-s','read-only','-C',str(root),'-c','features.multi_agent=false','--json',prompt]
    # Keep CLI authentication/runtime available; hide source and author guidance from the child.
    isolation=['bwrap','--ro-bind','/','/','--bind',str(cli_home),str(cli_home),
               '--tmpfs','/tmp','--ro-bind',str(root),str(root),'--dev-bind','/dev','/dev','--proc','/proc',
               '--chdir',str(root),'--tmpfs',str(REPO)]
    hidden=[REPO]
    for folder in [Path.home()/'.agents',cli_home/'skills',cli_home/'plugins',cli_home/'agents',cli_home/'rules',cli_home/'memories',Path.home()/'.claude/skills']:
     ordinary_path(folder)
     if folder.is_dir():
      isolation+=['--tmpfs',str(folder)];hidden.append(folder)
    for file in [cli_home/'AGENTS.md',cli_home/'AGENTS.override.md']:
     ordinary_path(file)
     if file.is_file():isolation+=['--ro-bind','/dev/null',str(file)]
    probe=subprocess.run(isolation+['--','python3','-c',
     'from pathlib import Path; import sys; assert not any(any(Path(p).iterdir()) for p in sys.argv[1:])']+[str(p) for p in hidden],capture_output=True,text=True)
    if probe.returncode:
     print(json.dumps({'pass':False,'scope':'OS-isolation probe','exit_code':probe.returncode,'error':probe.stderr},ensure_ascii=False));sys.exit(2)
    cmd=isolation+['--']+cmd
    started=time.monotonic()
    try:
     result=subprocess.run(cmd,capture_output=True,text=True,stdin=subprocess.DEVNULL,timeout=150)
     raw={'command':cmd,'cwd':str(root),'exit_code':result.returncode,'elapsed_seconds':round(time.monotonic()-started,2),'stdout':result.stdout,'stderr':result.stderr}
    except subprocess.TimeoutExpired as e:
     raw={'command':cmd,'cwd':str(root),'exit_code':'timeout','elapsed_seconds':round(time.monotonic()-started,2),'stdout':(e.stdout or b'').decode() if isinstance(e.stdout,bytes) else e.stdout or '', 'stderr':(e.stderr or b'').decode() if isinstance(e.stderr,bytes) else e.stderr or ''}
    (root.parent/(root.name+'-raw.json')).write_text(json.dumps(raw,ensure_ascii=False,indent=2))
    events=[]
    for line in raw['stdout'].splitlines():
     try:events.append(json.loads(line))
     except ValueError:pass
    items=[e.get('item',{}) for e in events if e.get('type')=='item.completed']
    tools=[i for i in items if i.get('type')=='command_execution']
    searches=[i for i in tools if re.search(r'\brg\s',i.get('command','')) and 'заявка' in i.get('command','') and '--files' not in i.get('command','')]
    outputs='\n'.join(i.get('aggregated_output','') for i in searches)
    all_outputs='\n'.join(i.get('aggregated_output','') for i in tools)
    report={'task':args.task,'mode':mode,'version':subprocess.run(['codex','--version'],capture_output=True,text=True).stdout.strip(),'candidate_sha256':EXPECTED_HASH,'os_isolation_probe_passed':True,'masked_source_and_guidance_paths':[str(p) for p in hidden],'command':cmd,'cwd':str(root),'exit_code':raw['exit_code'],'elapsed_seconds':raw['elapsed_seconds'],'native_completed':any(e.get('type')=='turn.completed' for e in events),'rule_read_observed':any('cat ' in i.get('command','') and 'comm-human-folder-guides.md' in i.get('command','') for i in tools),'content_search_count':len(searches),'search_commands':[i['command'] for i in searches],'search_exit_codes':[i.get('exit_code') for i in searches],'expected_machine_paths':expected,'all_machine_matches_present':all(re.search(re.escape(p)+r':\d+:',outputs) for p in expected),'searches_exclude_human_guides':bool(searches) and all('!README.human.md' in i.get('command','') for i in searches),'human_canary_in_any_native_event':marker in raw['stdout'],'human_body_line_in_tool_output':bool(re.search(r'README\.human\.md:\d+:',all_outputs)),'other_commands_with_target':sum('заявка' in i.get('command','') for i in tools)-len(searches),'errors':[e for e in events if e.get('type') in ('error','turn.failed')]}
    timeline = {e['item']['id']: n for n, e in enumerate(events)
                if e.get('type') == 'item.started' and e.get('item', {}).get('type') == 'command_execution'}
    for n, e in enumerate(events):
     if e.get('type') == 'item.completed' and e.get('item', {}).get('type') == 'command_execution':
      e['item'].update(start_event=timeline.get(e['item']['id'], n), end_event=n)
    expected_rule_bodies, starts, aliases = snapshot_rule_inputs(root)
    search_at = tools.index(searches[0]) if args.task == 'search' and searches else None
    report.update(assess_rule_reading(tools, expected_rule_bodies, starts=starts, aliases=aliases,
                                     root=root, search_at=search_at, immutable_fixture=True,
                                     skill_bodies=skill_bodies, skill_links=active_links,
                                     task_skills={task_skill} if args.task != 'search' else set()))
    report['rule_read_observed'] = '.claude/rules/comm-human-folder-guides.md' in report['first_reads']
    report['full_rule_read_before_search'] = search_at is not None and report['all_rule_bodies_read']
    report['pass'] = (report['rule_reading_pass'] and report['native_completed'] and report['exit_code'] == 0
                      and not report['human_canary_in_any_native_event'])
    if args.task == 'search':
        report['pass'] = (report['pass'] and report['full_rule_read_before_search']
                          and report['content_search_count'] == 1 and report['all_machine_matches_present']
                          and report['searches_exclude_human_guides'] and not report['human_body_line_in_tool_output']
                          and report['other_commands_with_target'] == 0)
    report['raw_events_path']=str(root.parent/(root.name+'-raw.json'))
    report['check_sha256']=check_hash
    assert not any(marker in s for s in report['search_commands'])
    ordinary_path(args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    sys.exit(0 if report['pass'] else 1)


if __name__=='__main__':
    main()
