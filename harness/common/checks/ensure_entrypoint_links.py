"""Restore entrypoint links; run from the project root or pass that root."""
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from pathlib import Path


BOOTSTRAP = '''# Harness

В начале каждой сессии до выполнения задачи запусти из корня проекта:

```sh
python3 harness/{package}/checks/ensure_entrypoint_links.py
```

При ошибке проверки остановись и сообщи причину.
Прочитай в следующем порядке (точный порядок очень важен): START.md обоих
пакетов, все Markdown-правила .claude/rules и подпапок, затем INDEX.md обоих
пакетов. В каждой группе сначала common, затем project. Все правила получи
завершёнными вызовами до чтения тела скилла; не объединяй правила и скилл
в одном вызове. Подробности открывай по задаче; README.human.md не читай.
Индивидуальные инструкции не отменяют применимые канонические требования.
Прямые правки AGENTS.md и CLAUDE.md запрещены договорённостью harness, но технически
не заблокированы; изменения предлагай через inbox. Согласованное создание и восстановление
стартовых ссылок — узкое исключение. Динамическую память сохраняй внутри harness.
'''


def fenced_lines(text, *, reject_unclosed=True):
    """Classify original lines; allow an unclosed historical example through EOF."""
    fence = None
    depth, list_indent = 0, 0
    for number, line in enumerate(text.splitlines(keepends=True), 1):
        inside = fence is not None
        candidate = line
        quotes = 0
        while (not inside or quotes < depth) and re.match(r'^ {0,3}>[ \t]?', candidate):
            candidate = re.sub(r'^ {0,3}>[ \t]?', '', candidate, count=1)
            quotes += 1
        if inside and quotes < depth and candidate.strip() and reject_unclosed:
            raise ValueError(f'Ambiguous Markdown quote fence at line {number}.')
        bullet = re.match(r'^ {0,3}(?:[-+*]|[0-9]+[.)])[ \t]+', candidate) if not inside else None
        indentation = len(bullet.group()) if bullet else 0
        if bullet:
            candidate = candidate[indentation:]
            if (re.match(r'^ {0,3}(?:>|[-+*]|[0-9]+[.)])', candidate)
                    and re.search(r'`{3,}|~{3,}', candidate) and reject_unclosed):
                raise ValueError(f'Unsupported nested Markdown fence at line {number}.')
        elif inside and list_indent and candidate.startswith(' ' * list_indent):
            candidate = candidate[list_indent:]
        elif inside and list_indent and candidate.strip() and reject_unclosed:
            raise ValueError(f'Ambiguous Markdown list fence at line {number}.')
        match = re.match(r'^ {0,3}(`{3,}|~{3,})([^\r\n]*)', candidate)
        if match:
            marker, suffix = match.groups()
            if fence is None and (marker[0] == '~' or '`' not in suffix):
                fence, start = marker, number
                depth, list_indent = quotes, indentation
                inside = True
            elif (fence is not None and quotes == depth and marker[0] == fence[0]
                  and len(marker) >= len(fence) and not suffix.strip(' \t')):
                fence = None
        elif not inside and re.match(r'^(?: {4}|\t)', candidate):
            inside = True
        yield line, inside
    if fence is not None and reject_unclosed:
        raise ValueError(f'Unclosed Markdown code fence starting at line {start}.')


def instruction_text(text):
    """Exclude common fenced and inline code examples from link detection."""
    text = ''.join(line for line, inside in fenced_lines(text) if not inside)
    return re.sub(r'(`+).*?\1', '', text, flags=re.S)


WARNING = ('Прямое редактирование AGENTS.md и CLAUDE.md запрещено договорённостью harness, '
           'но технически не заблокировано. Изменения предлагайте через заявку в '
           'harness/<пакет>/inbox/.')
NOTICE = 'Стартовые ссылки повреждены и будут автоматически восстановлены.'
RULES_LINK = '- [.claude/rules](.claude/rules/)'
RULES_READ = ('До выполнения задачи прочитай все Markdown-правила из .claude/rules '
              'и его подпапок, кроме README.human.md; соблюдай применимые требования.')
LINK_LINES = {f'- [harness/{p}/{n}](harness/{p}/{n})'
              for p in ('common', 'project') for n in ('INDEX.md', 'START.md')} | {RULES_LINK, RULES_READ, RULES_LINK + ' ' + RULES_READ}


def without_startup_links(text):
    """Ignore generated links outside fenced code, and trailing line endings."""
    return ''.join(line for line, inside in fenced_lines(text, reject_unclosed=False)
                   if inside or line.rstrip('\r\n') not in LINK_LINES).rstrip('\r\n')


def report_history_changes(root):
    """Use existing Git history if available; no registration or setup is required."""
    try:
        top = subprocess.run(['git', '--no-optional-locks', 'rev-parse', '--show-toplevel'],
                             cwd=root, capture_output=True)
        if top.returncode or Path(top.stdout.decode().strip()).resolve() != root:
            print('Сравнение настроек с историей не проверено: нет истории этого проекта.')
            return
        for name in ('AGENTS.md', 'CLAUDE.md'):
            baseline = subprocess.run(['git', '--no-optional-locks', 'show', f'HEAD:{name}'],
                                      cwd=root, capture_output=True)
            if baseline.returncode:
                print(f'{name}: сравнение с историей не проверено; версии в HEAD нет.')
                continue
            file = root / name
            current = file.read_bytes().decode('utf-8') if file.exists() else ''
            previous = baseline.stdout.decode('utf-8')
            changed = (without_startup_links(current) != without_startup_links(previous)
                       if name == 'AGENTS.md' else current != previous)
            if changed:
                print(f'{name}: обнаружено изменение настроек относительно HEAD. ' + WARNING)
    except FileNotFoundError:
        print('Сравнение настроек с историей не проверено: Git отсутствует; он не обязателен.')


def ordinary_path(path):
    """Check original components from the root before following any ancestor."""
    path = Path(path).absolute()
    for component in (*reversed(path.parents), path):
        try:
            mode = component.lstat().st_mode
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(mode):
            raise ValueError(f'Symlink forbidden: {component}')
    return path


def ordinary_tree(path):
    """Inspect directory entries without following links or suppressing I/O errors."""
    path = ordinary_path(path)
    pending = [path] if path.is_dir() else []
    while pending:
        directory = ordinary_path(pending.pop())
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_symlink():
                    raise ValueError(f'Symlink forbidden: {entry.path}')
                if entry.is_dir(follow_symlinks=False):
                    pending.append(Path(entry.path))


def ordinary_directory(path, root):
    ordinary_path(path)
    for directory in (*reversed(path.parents), path):
        if directory.exists() and not directory.is_dir():
            relative = directory.relative_to(root) if directory.is_relative_to(root) else directory
            raise ValueError(f'Not an ordinary directory: {relative}')


def utf8_text(data, name):
    try:
        return data.decode('utf-8')
    except UnicodeError as error:
        raise ValueError(f'Invalid UTF-8 text: {name}: {error}') from error


def check_rule_copies(root):
    """Check the complete installed canonical set without publishing missing copies."""
    common = root / 'harness/common'
    ordinary_directory(common, root)
    if not common.is_dir():
        raise ValueError('harness/common is required; project-only is unsupported.')
    native = root / '.claude/rules'
    ordinary_directory(native, root)
    sources = {}
    for package, prefix in (('common', 'comm-'), ('project', 'proj-')):
        rules = root / 'harness' / package / 'rules'
        ordinary_directory(rules, root)
        if rules.is_dir():
            for path in (rules, *rules.rglob('*')):
                if path.is_symlink():
                    raise ValueError(f'Not an ordinary file: {path}')
                if path.is_dir():
                    tuple(path.iterdir())  # glob may silently omit unreadable directories.
                if path.name.startswith(prefix) and path.suffix == '.md' and path.parent != rules:
                    raise ValueError(f'Canonical rules must be direct ordinary files: {path}')
            sources.update((file.name, file) for file in rules.glob(prefix + '*.md'))
    if not any(name.startswith('comm-') for name in sources):
        raise ValueError('No canonical shared rules found; nothing checked.')
    for path in (native, *native.rglob('*')):
        if path.is_symlink():
            raise ValueError(f'Not an ordinary file: {path}')
        if path.is_dir():
            tuple(path.iterdir())
    actual = {file.relative_to(native).as_posix() for file in native.rglob('*.md')
              if file.name.startswith(('comm-', 'proj-'))}
    expected = set(sources)
    if expected != actual:
        raise ValueError(f'Missing copies: {sorted(expected - actual)}; '
                         f'extra copies: {sorted(actual - expected)}')
    for name, source in sorted(sources.items()):
        copy = native / name
        if not source.is_file() or not copy.is_file():
            raise ValueError(f'Not an ordinary file: {name}')
        data = source.read_bytes()
        if not utf8_text(data, source.relative_to(root)).strip():
            raise ValueError(f'Empty canonical rule: {name}')
        if data != copy.read_bytes():
            raise ValueError(f'Different rule bytes: {name}')
    return len(sources)


def snapshot_input(path, root):
    ordinary_path(path)
    ordinary_directory(path.parent, root)
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError(f'Not a regular file: {path.name}')
    if not path.exists():
        return None
    before = path.stat()
    data = path.read_bytes()
    after = path.stat()
    attributes = lambda value: (value.st_dev, value.st_ino, value.st_mtime_ns, value.st_ctime_ns,
                                value.st_size, value.st_uid, value.st_gid, stat.S_IMODE(value.st_mode))
    if attributes(before) != attributes(after):
        raise ValueError(f'Input changed while reading: {path.name}')
    return data, attributes(after)


def replace_input(path, original, updated, root):
    """Replace one input atomically, preserving a detected concurrent edit."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.' + path.name + '-', delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(updated)
            handle.flush()
            if original is not None:
                uid, gid, mode = original[1][-3:]
                current = temporary.stat()
                if (current.st_uid, current.st_gid) != (uid, gid):
                    if not hasattr(os, 'chown'):
                        raise ValueError(f'Cannot preserve input ownership: {path.name}')
                    os.chown(temporary, uid, gid)
                if hasattr(os, 'listxattr'):
                    attributes = {name: os.getxattr(path, name, follow_symlinks=False)
                                  for name in os.listxattr(path, follow_symlinks=False)}
                    for name in os.listxattr(temporary, follow_symlinks=False):
                        if name not in attributes:
                            os.removexattr(temporary, name, follow_symlinks=False)
                    for name, value in attributes.items():
                        os.setxattr(temporary, name, value, follow_symlinks=False)
                temporary.chmod(mode)
            os.fsync(handle.fileno())
        if snapshot_input(path, root) != original:
            raise ValueError(f'Input changed before replacement: {path.name}')
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def load_project_skeleton(common, root):
    template = common / 'base/project-skeleton.json'
    ordinary_directory(template.parent, root)
    if not template.is_file() or template.is_symlink():
        raise ValueError('Missing or unsafe resource: harness/common/base/project-skeleton.json')
    data = json.loads(template.read_text(encoding='utf-8'))
    categories = data.get('categories') if isinstance(data, dict) else None
    if not isinstance(categories, dict) or not categories:
        raise ValueError('Project skeleton requires nonempty categories.')
    for name, details in categories.items():
        if (not re.fullmatch(r'[a-z0-9][a-z0-9_-]*(?:/[a-z0-9][a-z0-9_-]*)*', name)
                or not isinstance(details, dict)
                or any(not isinstance(details.get(key), str) or not details[key].strip()
                       for key in ('purpose', 'example'))):
            raise ValueError(f'Invalid project skeleton category: {name}')
    return categories


def create_project_skeleton(project, categories):
    # Build off-path so an interrupted write cannot leave a half-created project.
    with tempfile.TemporaryDirectory(prefix='.project-skeleton-', dir=project.parent) as temporary:
        staging = Path(temporary)
        (staging / 'README.human.md').write_text(
            '# Проектный harness\n\nЗдесь сохраняются материалы текущего проекта; '
            'при создании каркаса рабочих материалов ещё нет. Например, согласованный '
            'контракт проекта позже можно сохранить в base/project-contract.md. '
            'Пример иллюстративный, а наличие папок не подтверждает проверенность.\n', encoding='utf-8')
        rows = []
        for name, details in categories.items():
            directory = staging / name
            directory.mkdir(parents=True, exist_ok=True)
            (directory / 'README.human.md').write_text(
                f'# {name}\n\n{details["purpose"]}\n\n'
                f'Пример (иллюстративный): {details["example"]}\n', encoding='utf-8')
            rows.append(f'| {details["purpose"]} | [{name}/]({name}/) |')
        # Include explanations for intermediate directories of an approved nested path.
        for directory in staging.rglob('*'):
            if directory.is_dir() and not (directory / 'README.human.md').exists():
                (directory / 'README.human.md').write_text(
                    '# Проектные материалы\n\nЗдесь сгруппированы утверждённые категории. '
                    'Например, вложенная категория хранит относящиеся к её задаче материалы. '
                    'Это иллюстративный пример для пока пустой папки.\n', encoding='utf-8')
        (staging / 'INDEX.md').write_text(
            '# Проектный harness\n\nПустой каркас для знаний текущего проекта.\n\n'
            '| Назначение | Каталог |\n|---|---|\n' + '\n'.join(rows) +
            '\n\nИщи материалы по задаче, исключая README.human.md. '
            'Наличие категории не подтверждает её наполненность или проверенность.\n', encoding='utf-8')
        (staging / 'START.md').write_text(
            '# Старт проектного harness\n\nПроектный пакет требует установленного common. '
            'Из корня проекта запускается `python3 -B harness/common/checks/ensure_entrypoint_links.py`; '
            'повторный запуск после команды статичного входа не нужен. '
            'Затем ищи проектные материалы по INDEX.md; подробности открывай по задаче.\n', encoding='utf-8')
        if project.exists() or project.is_symlink():
            raise ValueError('Project appeared during initialization; existing data preserved.')
        staging.rename(project)



def startup_connections(content, resources):
    visible = instruction_text(content)
    present = set()
    for relative in resources + ['.claude/rules']:
        target = re.escape(relative) + (r'/?' if relative == '.claude/rules' else '')
        if re.search(r'\[[^\]\n]+\]\(<?(?:\./)?' + target + r'(?:#[^\s)>]+)?>?\)', visible):
            present.add(relative)
    return visible, present


def repair_startup_blocks(content, resources, missing_connections):
    """Validate each block; repair only recognizable missing connections."""
    pattern = re.compile(r'^- \[(?P<label>[^\]\n]+)\]\(<?(?:\./)?(?P<target>harness/(?:common|project)/(?:START|INDEX)\.md|\.claude/rules/?)(?:#[^\s)>]+)?>?\)')
    lines = list(fenced_lines(content))
    parts = []
    order = resources[:2] + ['.claude/rules'] + resources[2:]
    ending = re.search(r'\r?\n', content)
    newline = ending.group() if ending else '\n'
    index = 0
    while index < len(lines):
        line, inside = lines[index]
        if inside or not pattern.match(line):
            parts.append(line)
            index += 1
            continue
        block, labels = {}, {}
        start = index + 1
        while index < len(lines) and not lines[index][1]:
            match = pattern.match(lines[index][0])
            if not match:
                if block and next(reversed(block)) == '.claude/rules' and lines[index][0].rstrip('\r\n') == RULES_READ:
                    block['.claude/rules'] += lines[index][0]
                    index += 1
                    continue
                break
            target = match.group('target').rstrip('/')
            if target in block:
                break
            block[target] = lines[index][0]
            labels[target] = match.group('label').rstrip('/')
            index += 1
        if len(block) < 3 or (len(block) < len(order) and any(labels[p] != p for p in block)):
            raise ValueError(f'Ambiguous partial startup link list at line {start}.')
        if list(block) != [path for path in order if path in block]:
            raise ValueError(f'Invalid startup block order at line {start}; use inbox for reordering.')
        parts.append(block)
    has_complete = any(isinstance(part, dict) and len(part) == len(order) for part in parts)
    output, changed = [], False
    for part in parts:
        if isinstance(part, str):
            output.append(part)
            continue
        missing = [path for path in order if path not in part]
        # Complete global links without a full block may be deliberate user fragments.
        if not missing or (not missing_connections and not has_complete):
            output.extend(part.values())
            continue
        for path in missing:
            part[path] = (RULES_LINK + ' ' + RULES_READ if path == '.claude/rules'
                          else f'- [{path}]({path})') + newline
        output.extend(part[path] if part[path].endswith('\n') else part[path] + newline for path in order)
        changed = True
    return ''.join(output), changed


def ensure(root):
    print(WARNING)
    root = ordinary_path(root)
    ordinary_directory(root, root)
    root = Path(os.path.normpath(root))
    script = ordinary_path(__file__)
    ordinary_directory(script.parent, root)
    if script.is_symlink():
        raise ValueError(f'Unsafe checker path: {script}')
    common, project = root / 'harness/common', root / 'harness/project'
    for directory in (common, common / 'checks', project):
        ordinary_directory(directory, root)
    if not common.is_dir():
        raise ValueError('harness/common is required; project-only is unsupported.')
    checker = ordinary_path(common / 'checks/ensure_entrypoint_links.py')
    if checker.is_symlink() or (checker.exists() and not checker.is_file()):
        raise ValueError(f'Unsafe checker path: {checker}')
    ordinary_tree(root / 'harness')
    categories = load_project_skeleton(common, root)
    create_project = not project.exists()
    resources = [f'harness/{package}/{name}' for name in ('START.md', 'INDEX.md')
                 for package in ('common', 'project')]
    for relative in resources:
        if create_project and relative.startswith('harness/project/'):
            continue
        path = root / relative
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError(f'Missing or unsafe resource: {relative}')
        if not utf8_text(path.read_bytes(), relative).strip():
            raise ValueError(f'Empty resource: {relative}')
    agents, claude = root / 'AGENTS.md', root / 'CLAUDE.md'
    for path in (agents, claude):
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise ValueError(f'Not a regular file: {path.name}')
    rules = root / '.claude' / 'rules'
    for path in (rules.parent, rules):
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            raise ValueError(f'Not an ordinary directory: {path.relative_to(root)}')
    check_rule_copies(root)
    snapshots = {path: snapshot_input(path, root) for path in (agents, claude)}
    report_history_changes(root)
    original_agents = utf8_text(snapshots[agents][0], agents.name) if snapshots[agents] is not None else ''
    content = original_agents or BOOTSTRAP.replace('{package}', 'common')
    _, present = startup_connections(content, resources)
    content, repaired_blocks = repair_startup_blocks(content, resources,
        bool(set(resources + ['.claude/rules']) - present))
    visible, present = startup_connections(content, resources)
    missing = [relative for relative in resources if relative not in present]
    additions = [f'- [{relative}]({relative})' for relative in missing]
    if '.claude/rules' not in present:
        additions.append(RULES_LINK)
    if RULES_READ not in visible:
        additions.append(RULES_READ)
    if additions:
        ending = re.search(r'\r?\n', content)
        newline = ending.group() if ending else '\n'
        order = {f'- [{relative}]({relative})': index
                 for index, relative in enumerate(resources[:2] + ['.claude/rules/'] + resources[2:])}
        order[RULES_LINK] = 2
        order[RULES_READ] = 2.5
        additions.sort(key=lambda line: order[line])
        if RULES_LINK in additions and RULES_READ in additions:
            additions[additions.index(RULES_LINK)] += ' ' + RULES_READ
            additions.remove(RULES_READ)
        content += ('' if content.endswith('\n') else newline) + newline + newline.join(additions) + newline
    original_claude = utf8_text(snapshots[claude][0], claude.name) if snapshots[claude] is not None else ''
    bridge = original_claude
    if not re.search(r'(?m)^@(?:\./)?AGENTS\.md[ \t]*\r?$', instruction_text(bridge)):
        ending = re.search(r'\r?\n', bridge)
        newline = ending.group() if ending else '\n'
        bridge = '@AGENTS.md' + newline + bridge
    changed = []
    updates = [(path, updated.encode('utf-8'))
               for path, original, updated in ((agents, original_agents, content),
                                               (claude, original_claude, bridge))
               if updated != original or snapshots[path] is None]
    for path, original in snapshots.items():
        if snapshot_input(path, root) != original:
            raise ValueError(f'Input changed during planning: {path.name}')
    if additions or repaired_blocks or bridge != original_claude:
        print(NOTICE, flush=True)
    try:
        if create_project:
            print('harness/project отсутствует: создаётся пустой каркас из common.', flush=True)
            create_project_skeleton(project, categories)
            changed.append('harness/project')
        for path, updated in updates:
            replace_input(path, snapshots[path], updated, root)
            changed.append(path.name)
    except (OSError, ValueError) as error:
        raise ValueError(f'{error}; already changed: {changed}; '
                         f'pending inputs: {[p.name for p, _ in updates if p.name not in changed]}') from error
    if bridge not in ('@AGENTS.md', '@AGENTS.md\n', '@AGENTS.md\r\n'):
        print('CLAUDE.md: требуется единственная строка @AGENTS.md; '
              'дополнительное или отличающееся содержимое сохранено. ' + WARNING)
    return changed


def main():
    if len(sys.argv) > 2:
        print('Usage: python3 ensure_entrypoint_links.py [project-root]', file=sys.stderr)
        return 2
    root = Path(sys.argv[1] if len(sys.argv) == 2 else '.').absolute()
    try:
        changed = ensure(root)
    except (OSError, UnicodeError, ValueError) as error:
        print(f'Entrypoint check failed: {error}', file=sys.stderr)
        return 2
    print('Entrypoint check completed' + (': changed paths: ' + ', '.join(changed) if changed else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
