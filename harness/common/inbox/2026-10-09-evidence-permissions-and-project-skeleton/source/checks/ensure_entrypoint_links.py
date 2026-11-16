"""Restore entrypoint links; run from the project root or pass that root."""
import json
import re
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
    # ponytail: top-level fences only; use a Markdown parser if nested containers are needed.
    fence = None
    for number, line in enumerate(text.splitlines(keepends=True), 1):
        inside = fence is not None
        match = re.match(r'^ {0,3}(`{3,}|~{3,})([^\r\n]*)', line)
        if match:
            marker, suffix = match.groups()
            if fence is None and (marker[0] == '~' or '`' not in suffix):
                fence, start = marker, number
                inside = True
            elif (fence is not None and marker[0] == fence[0]
                  and len(marker) >= len(fence) and not suffix.strip(' \t')):
                fence = None
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


def ordinary_directory(path, root):
    for directory in (path, *path.parents):
        if directory == root:
            break
        if directory.is_symlink() or (directory.exists() and not directory.is_dir()):
            raise ValueError(f'Not an ordinary directory: {directory.relative_to(root)}')


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



def repair_startup_blocks(content, resources, missing):
    """Repair only incomplete generated link blocks, retaining labels and user text."""
    pattern = re.compile(r'^- \[[^\]\n]+\]\((harness/(?:common|project)/(?:START|INDEX)\.md|\.claude/rules/?)\)')
    lines = list(fenced_lines(content))
    output, changed = [], False
    index = 0
    while index < len(lines):
        line, inside = lines[index]
        if inside or not pattern.match(line):
            output.append(line)
            index += 1
            continue
        block, seen = [], set()
        while index < len(lines) and not lines[index][1] and pattern.match(lines[index][0]):
            target = pattern.match(lines[index][0]).group(1).rstrip('/')
            if target in seen:
                break
            seen.add(target)
            block.append(lines[index][0])
            index += 1
        links = {pattern.match(line).group(1).rstrip('/'): line for line in block}
        missing_here = [path for path in resources if path not in links]
        # A repeated canonical block is repaired even if another copy has the missing link.
        complete_block = '.claude/rules' in links and any(path in links for path in resources)
        missing_rules = set(resources).issubset(links) and '.claude/rules' not in links and (missing or list(links) == resources)
        if (not missing_here and not missing_rules) or not (missing or complete_block or missing_rules):
            output.extend(block)
            continue
        newline = '\r\n' if any(line.endswith('\r\n') for line in block) else '\n'
        if missing_rules:
            links['.claude/rules'] = RULES_LINK + ' ' + RULES_READ + newline
        for path in missing_here:
            links[path] = f'- [{path}]({path})' + newline
        order = resources[:2] + (['.claude/rules'] if '.claude/rules' in links else []) + resources[2:]
        output.extend(links[path] if links[path].endswith('\n') else links[path] + newline
                      for path in order)
        changed = True
    return ''.join(output), changed


def ensure(root):
    print(WARNING)
    common, project = root / 'harness/common', root / 'harness/project'
    for directory in (common, project):
        ordinary_directory(directory, root)
    if not common.is_dir():
        raise ValueError('harness/common is required; project-only is unsupported.')
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
    agents, claude = root / 'AGENTS.md', root / 'CLAUDE.md'
    for path in (agents, claude):
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise ValueError(f'Not a regular file: {path.name}')
    rules = root / '.claude' / 'rules'
    for path in (rules.parent, rules):
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            raise ValueError(f'Not an ordinary directory: {path.relative_to(root)}')
    report_history_changes(root)
    original_agents = agents.read_bytes().decode('utf-8') if agents.exists() else ''
    content = original_agents or BOOTSTRAP.replace('{package}', 'common')
    visible = instruction_text(content)
    missing = [relative for relative in resources if not re.search(
        r'\[[^\]\n]+\]\(<?(?:\./)?' + re.escape(relative) + r'(?:#[^\s)>]+)?>?\)', visible)]
    additions = [f'- [{relative}]({relative})' for relative in missing]
    if not re.search(r'\[[^\]\n]+\]\(<?(?:\./)?\.claude/rules/?(?:#[^\s)>]+)?>?\)', visible):
        additions.append(RULES_LINK)
    if RULES_READ not in visible:
        additions.append(RULES_READ)
    content, repaired_blocks = repair_startup_blocks(content, resources, missing + (['.claude/rules'] if RULES_LINK in additions else []))
    if repaired_blocks:
        # The repaired blocks already contain all missing package links.
        additions = [line for line in additions if line in (RULES_LINK, RULES_READ)]
        if RULES_LINK in content:
            additions = [line for line in additions if line != RULES_LINK]
        if RULES_READ in content:
            additions = [line for line in additions if line != RULES_READ]
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
    original_claude = claude.read_bytes().decode('utf-8') if claude.exists() else ''
    bridge = original_claude
    if not re.search(r'(?m)^@(?:\./)?AGENTS\.md[ \t]*\r?$', instruction_text(bridge)):
        ending = re.search(r'\r?\n', bridge)
        newline = ending.group() if ending else '\n'
        bridge = '@AGENTS.md' + newline + bridge
    changed = []
    if additions or repaired_blocks or bridge != original_claude:
        print(NOTICE, flush=True)
    if create_project:
        print('harness/project отсутствует: создаётся пустой каркас из common.', flush=True)
        create_project_skeleton(project, categories)
    rules.mkdir(parents=True, exist_ok=True)
    for path, original, updated in ((agents, original_agents, content),
                                     (claude, original_claude, bridge)):
        if updated != original or not path.exists():
            path.write_bytes(updated.encode('utf-8'))
            changed.append(path.name)
    if bridge not in ('@AGENTS.md', '@AGENTS.md\n', '@AGENTS.md\r\n'):
        print('CLAUDE.md: требуется единственная строка @AGENTS.md; '
              'дополнительное или отличающееся содержимое сохранено. ' + WARNING)
    return changed


def main():
    if len(sys.argv) > 2:
        print('Usage: python3 ensure_entrypoint_links.py [project-root]', file=sys.stderr)
        return 2
    root = Path(sys.argv[1] if len(sys.argv) == 2 else '.').resolve()
    try:
        changed = ensure(root)
    except (OSError, UnicodeError, ValueError) as error:
        print(f'Entrypoint check failed: {error}', file=sys.stderr)
        return 2
    print('Entrypoint check completed' + (': updated links in ' + ', '.join(changed) if changed else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
