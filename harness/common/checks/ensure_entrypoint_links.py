"""Restore entrypoint links; run from the project root or pass that root."""
import argparse
import re
import subprocess
import sys
from pathlib import Path


BOOTSTRAP = '''# Harness

В начале каждой сессии до выполнения задачи запусти из корня проекта:

```sh
python3 harness/common/checks/ensure_entrypoint_links.py
```

При ошибке проверки остановись и сообщи причину. Затем прочитай INDEX.md и START.md
подключённых пакетов. Подробности открывай по задаче; README.human.md не читай.
Индивидуальные инструкции не отменяют применимые канонические требования.
AGENTS.md принадлежит пользователю; разрешено только восстановление указанных ниже
ссылок. Динамическую память сохраняй внутри harness.
'''


def instruction_text(text):
    """Exclude common fenced and inline code examples from link detection."""
    text = re.sub(r'(?ms)^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$', '', text)
    return re.sub(r'(`+).*?\1', '', text, flags=re.S)


WARNING = ('Прямое редактирование AGENTS.md и CLAUDE.md запрещено. '
           'Предложите изменение через заявку в harness/<пакет>/inbox/.')
NOTICE = 'Стартовые ссылки повреждены и будут автоматически восстановлены.'
LINK_LINES = {f'- [harness/{p}/{n}](harness/{p}/{n})'
              for p in ('common', 'project') for n in ('INDEX.md', 'START.md')}


def git(root, *args):
    return subprocess.run(['git', *args], cwd=root, capture_output=True)


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


def check_protected(root, staged=False, require_links=True):
    top = git(root, 'rev-parse', '--show-toplevel')
    if top.returncode or Path(top.stdout.decode().strip()).resolve() != root:
        raise ValueError(WARNING + ' Проверка требует корень Git-проекта.')
    for name in ('AGENTS.md', 'CLAUDE.md'):
        baseline = git(root, 'show', f'HEAD:{name}')
        if baseline.returncode:
            raise ValueError(WARNING + f' Нет согласованной версии {name} в HEAD; '
                             'начальная регистрация требует подтверждения пользователя.')
        path = root / name
        if staged:
            entry = git(root, 'ls-files', '--stage', '--', name)
            mode = entry.stdout.split(maxsplit=1)[0] if entry.stdout else b''
            if entry.returncode or mode not in (b'100644', b'100755'):
                raise ValueError(WARNING + f' {name}: в индексе нет обычного файла.')
            current = git(root, 'show', f':{name}')
            if current.returncode:
                raise ValueError(WARNING + f' {name}: файл недоступен в индексе.')
            content = current.stdout.decode('utf-8')
        else:
            if path.is_symlink() or (path.exists() and not path.is_file()):
                raise ValueError(WARNING + f' {name}: требуется обычный файл.')
            content = path.read_bytes().decode('utf-8') if path.exists() else ''
        before = baseline.stdout.decode('utf-8')
        if name == 'AGENTS.md':
            if without_startup_links(content) != without_startup_links(before):
                raise ValueError(WARNING + f' {name}: изменены настройки вне стартовых ссылок.')
            if require_links:
                visible = instruction_text(content)
                for package in ('common', 'project'):
                    if (root / 'harness' / package).is_dir():
                        for resource in ('INDEX.md', 'START.md'):
                            relative = f'harness/{package}/{resource}'
                            if not re.search(r'\[[^\]\n]+\]\(<?(?:\./)?' + re.escape(relative)
                                             + r'(?:#[^\s)>]+)?>?\)', visible):
                                raise ValueError(WARNING + f' {name}: отсутствует ссылка {relative}.')
        elif content not in ('@AGENTS.md', '@AGENTS.md\n'):
            if require_links or content:
                raise ValueError(WARNING + ' CLAUDE.md должен содержать только @AGENTS.md.')
    return True


def ensure(root):
    # Before the initial approved Git registration, only link repair is available.
    top = git(root, 'rev-parse', '--show-toplevel')
    if not top.returncode and Path(top.stdout.decode().strip()).resolve() == root:
        if all(not git(root, 'show', f'HEAD:{name}').returncode
               for name in ('AGENTS.md', 'CLAUDE.md')):
            check_protected(root, require_links=False)
        else:
            print('Защита содержимого ещё не активирована: нет согласованной версии входов в HEAD.',
                  file=sys.stderr)
    else:
        print('Защита содержимого не проверена: проект не зарегистрирован в Git.', file=sys.stderr)
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
    original_agents = agents.read_text(encoding='utf-8') if agents.exists() else ''
    content = original_agents or BOOTSTRAP
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
    if bridge.strip() not in ('@AGENTS.md', '@./AGENTS.md'):
        raise ValueError('CLAUDE.md import restored, but additional content was preserved. '
                         'Предложите исправление через harness/<пакет>/inbox/.')
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-protected', action='store_true', help='read-only content protection check')
    parser.add_argument('--staged', action='store_true', help='check the Git index before a commit')
    parser.add_argument('root', nargs='?', default='.')
    args = parser.parse_args()
    if args.staged and not args.check_protected:
        parser.error('--staged requires --check-protected')
    root = Path(args.root).resolve()
    try:
        if args.check_protected:
            check_protected(root, staged=args.staged)
            print('Protected entrypoints OK' + (' (Git index)' if args.staged else ' (working tree)'))
        else:
            changed = ensure(root)
            print('Entrypoint links OK' + (': updated ' + ', '.join(changed) if changed else ''))
    except (OSError, UnicodeError, ValueError) as error:
        print(f'Entrypoint check failed: {error}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
