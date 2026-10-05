"""Restore entrypoint links; run from the project root or pass that root."""
import re
import subprocess
import sys
from pathlib import Path


BOOTSTRAP = '''# Harness

В начале каждой сессии до выполнения задачи запусти из корня проекта:

```sh
python3 harness/{package}/checks/ensure_entrypoint_links.py
```

При ошибке проверки остановись и сообщи причину. Затем прочитай INDEX.md и START.md
подключённых пакетов. Подробности открывай по задаче; README.human.md не читай.
Индивидуальные инструкции не отменяют применимые канонические требования.
Прямые правки AGENTS.md и CLAUDE.md запрещены договорённостью harness, но технически
не заблокированы; изменения предлагай через inbox. Согласованное создание и восстановление
стартовых ссылок — узкое исключение. Динамическую память сохраняй внутри harness.
'''


def instruction_text(text):
    """Exclude common fenced and inline code examples from link detection."""
    text = re.sub(r'(?ms)^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$', '', text)
    return re.sub(r'(`+).*?\1', '', text, flags=re.S)


WARNING = ('Прямое редактирование AGENTS.md и CLAUDE.md запрещено договорённостью harness, '
           'но технически не заблокировано. Изменения предлагайте через заявку в '
           'harness/<пакет>/inbox/.')
NOTICE = 'Стартовые ссылки повреждены и будут автоматически восстановлены.'
LINK_LINES = {f'- [harness/{p}/{n}](harness/{p}/{n})'
              for p in ('common', 'project') for n in ('INDEX.md', 'START.md')}


def without_startup_links(text):
    """Ignore only generated link lines outside fenced code, and trailing LF."""
    result, fence = [], None
    for line in text.splitlines(keepends=True):
        match = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            result.append(line)
        elif fence is not None or line.rstrip('\n') not in LINK_LINES:
            result.append(line)
    return ''.join(result).rstrip('\n')


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


def ensure(root):
    print(WARNING)
    packages = [name for name in ('common', 'project')
                if (root / 'harness' / name).is_dir()]
    if not packages:
        raise ValueError('No installed harness package found.')
    resources = [f'harness/{package}/{name}' for package in packages
                 for name in ('INDEX.md', 'START.md')]
    for relative in resources:
        path = root / relative
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError(f'Missing or unsafe resource: {relative}')
    agents, claude = root / 'AGENTS.md', root / 'CLAUDE.md'
    for path in (agents, claude):
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise ValueError(f'Not a regular file: {path.name}')
    report_history_changes(root)
    original_agents = agents.read_text(encoding='utf-8') if agents.exists() else ''
    content = original_agents or BOOTSTRAP.replace('{package}', packages[0])
    visible = instruction_text(content)
    missing = [relative for relative in resources if not re.search(
        r'\[[^\]\n]+\]\(<?(?:\./)?' + re.escape(relative) + r'(?:#[^\s)>]+)?>?\)', visible)]
    if missing:
        content = content.rstrip('\n') + '\n\n' + '\n'.join(
            f'- [{relative}]({relative})' for relative in missing) + '\n'
    original_claude = claude.read_text(encoding='utf-8') if claude.exists() else ''
    bridge = original_claude
    if not re.search(r'(?m)^@(?:\./)?AGENTS\.md[ \t]*$', instruction_text(bridge)):
        bridge = '@AGENTS.md\n' + bridge
    changed = []
    if missing or bridge != original_claude:
        print(NOTICE, flush=True)
    for path, original, updated in ((agents, original_agents, content),
                                     (claude, original_claude, bridge)):
        if updated != original or not path.exists():
            path.write_text(updated, encoding='utf-8')
            changed.append(path.name)
    if bridge not in ('@AGENTS.md', '@AGENTS.md\n'):
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
