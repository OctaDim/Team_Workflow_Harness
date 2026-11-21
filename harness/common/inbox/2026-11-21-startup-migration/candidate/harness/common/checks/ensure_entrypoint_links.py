"""Check the harness installation and recover working files from its published packages."""
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path


PUBLICATION_MARKER = '.harness-publication.json'
WINDOWS_LOCK_FILE = '.harness-startup.lock'
WARNING = ('Прямое редактирование AGENTS.md и CLAUDE.md запрещено договорённостью harness, '
           'но технически не заблокировано. Изменения предлагайте через заявку в '
           'harness/<пакет>/inbox/.')
HUMAN = 'README.human.md'
PROTECTED = ('AGENTS.md', 'CLAUDE.md')
PACKAGES = (('common', 'comm-'), ('project', 'proj-'))
SKILL_CLIENTS = ('.agents/skills', '.claude/skills')
RESTART_REQUIRED = 3
MAP_LABELS = {
    'rules': 'Always loaded правила проекта',
    'skills': 'Контекстные lazy скиллы и рабочий опыт проекта',
    'testing/evidence/work': 'Результаты работ по приложению',
    'testing/evidence/harness': 'Результаты проверок механизма project',
}


def validate_type(path, info):
    mode = info.st_mode
    reparse = getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0)
    if stat.S_ISLNK(mode):
        raise ValueError(f'Symlink forbidden: {path}')
    if reparse:
        raise ValueError(f'Reparse point forbidden: {path}')
    if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
        raise ValueError(f'Special file forbidden: {path}')


def ordinary_path(path):
    """Validate the original components; never normalize away a symlink."""
    path = Path(path).absolute()
    for item in (*reversed(path.parents), path):
        try:
            info = item.lstat()
        except FileNotFoundError:
            continue
        validate_type(item, info)
        if item != path and not stat.S_ISDIR(info.st_mode):
            raise ValueError(f'Not an ordinary directory: {item}')
    return path


def ordinary_directory(path, root):
    path = ordinary_path(path)
    if path.exists() and not path.is_dir():
        raise ValueError(f'Not an ordinary directory: {path}')
    return path


def entries(path):
    """Walk without following links, suppressing errors or opening file contents."""
    if not ordinary_path(path).exists():
        return
    pending = [path]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as iterator:
            for item in sorted(iterator, key=lambda entry: entry.name):
                file = directory / item.name
                info = item.stat(follow_symlinks=False)
                validate_type(file, info)
                is_dir = stat.S_ISDIR(info.st_mode)
                yield file, is_dir
                if is_dir:
                    pending.append(file)


def ordinary_tree(path):
    path = ordinary_path(path)
    if path.is_dir():
        for _ in entries(path):
            pass


@contextmanager
def root_lock(root):
    """Serialize a checking/repairing startup with other startups and the publisher."""
    root = ordinary_directory(root, root)
    if os.name == 'nt':
        import msvcrt
        path = ordinary_path(root / WINDOWS_LOCK_FILE)
        fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_BINARY, 0o600)
        try:
            info = path.lstat()
            validate_type(path, info)
            if not stat.S_ISREG(info.st_mode) or not os.path.samestat(os.fstat(fd), info):
                raise ValueError(f'Invalid startup lock: {path}')
            os.lseek(fd, 0, os.SEEK_SET)
            try:
                # A byte range beyond EOF can be locked before initialization.
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise ValueError(f'Harness lock unavailable: {path} ({exc})') from exc
            if not os.fstat(fd).st_size:
                os.lseek(fd, 0, os.SEEK_SET)
                os.write(fd, b'\0')
                os.fsync(fd)
            yield
        finally:
            os.close(fd)
        return
    import fcntl
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError(f'Harness busy: {root}') from exc
        yield
    finally:
        os.close(fd)


def file_attributes(value):
    return (value.st_dev, value.st_ino, value.st_mtime_ns, value.st_ctime_ns,
            value.st_size, value.st_uid, value.st_gid, stat.S_IMODE(value.st_mode))


def snapshot_input(path, root):
    """Read one regular file and bind its bytes to its identity; None means missing."""
    ordinary_path(path)
    try:
        before = path.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(before.st_mode):
        raise ValueError(f'Not a regular file: {path}')
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) |
                 getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_BINARY', 0))
    with os.fdopen(fd, 'rb') as source:
        identity = file_attributes(before)
        if file_attributes(os.fstat(fd)) != identity:
            raise ValueError(f'Input changed before reading: {path}')
        data = source.read()
        if file_attributes(os.fstat(fd)) != identity or file_attributes(path.lstat()) != identity:
            raise ValueError(f'Input changed while reading: {path}')
    return data, identity


def require_file(path, root):
    result = snapshot_input(path, root)
    if result is None:
        raise ValueError(f'Missing canonical file: {path}')
    return result


def replace_input(path, original, updated, root, new_mode=None):
    """Preserve existing permissions/attributes and publish a complete file atomically."""
    ordinary_directory(path.parent, root)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.' + path.name + '-',
                                         delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(updated)
            handle.flush()
            if original is not None:
                uid, gid, mode = original[1][-3:]
                current = temporary.stat()
                if (current.st_uid, current.st_gid) != (uid, gid):
                    if not hasattr(os, 'chown'):
                        raise ValueError(f'Cannot preserve file ownership: {path}')
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
            elif new_mode is not None:
                temporary.chmod(new_mode & 0o777)
            os.fsync(handle.fileno())
        if snapshot_input(path, root) != original:
            raise ValueError(f'Input changed before replacement: {path}')
        if original is None:
            # A file created by another owner after the snapshot must survive.
            if os.name == 'nt':
                os.rename(temporary, path)  # Windows refuses an existing destination.
            else:
                os.link(temporary, path, follow_symlinks=False)
        else:
            os.replace(temporary, path)
        if os.name != 'nt':
            directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def load_project_skeleton(common, root):
    raw, _ = require_file(common / 'base/project-skeleton.json', root)
    template = json.loads(raw.decode('utf-8'))
    categories = template.get('categories') if isinstance(template, dict) else None
    if not isinstance(categories, dict) or not categories:
        raise ValueError('Project skeleton requires nonempty categories.')
    for name, detail in categories.items():
        if (not re.fullmatch(r'[a-z0-9][a-z0-9_-]*(?:/[a-z0-9][a-z0-9_-]*)*', name)
                or not isinstance(detail, dict)
                or any(not isinstance(detail.get(k), str) or not detail[k].strip()
                       for k in ('purpose', 'example'))):
            raise ValueError(f'Invalid project skeleton category: {name}')
    return categories


def create_project_skeleton(project, categories):
    """Create only the missing project. A failure never exposes a partial skeleton."""
    with tempfile.TemporaryDirectory(prefix='.project-skeleton-', dir=project.parent) as temporary:
        staging = Path(temporary)
        (staging / HUMAN).write_text(
            '# Проектный harness\n\nЗдесь сохраняются материалы проекта. Например, '
            'согласованный контракт можно поместить в base/project-contract.md.\n',
            encoding='utf-8')
        rows = ['# Проектный harness', '', '| Назначение | Каталог |', '|---|---|']
        for name, detail in categories.items():
            directory = staging / name
            directory.mkdir(parents=True, exist_ok=True)
            (directory / HUMAN).write_text(f'# {name}\n\n{detail["purpose"]}\n\n'
                                           f'Пример: {detail["example"]}\n', encoding='utf-8')
            label = MAP_LABELS.get(name, detail['purpose'])
            rows.append(f'| {label} | [{directory.name}](/harness/project/{name}) |')
        for directory in staging.rglob('*'):
            if directory.is_dir() and not (directory / HUMAN).exists():
                (directory / HUMAN).write_text(
                    '# Материалы проекта\n\nЗдесь размещаются вложенные категории, '
                    'например документы проекта.\n', encoding='utf-8')
        (staging / 'INDEX.md').write_text('\n'.join(rows) + '\n', encoding='utf-8')
        if ordinary_path(project).exists():
            raise ValueError(f'Project appeared during initialization: {project}')
        staging.rename(project)


def canonical_rules(root):
    """Retain the relative path to each published comm-/proj- rule, including subfolders."""
    sources = {}
    for package, prefix in PACKAGES:
        folder = ordinary_directory(root / 'harness' / package / 'rules', root)
        if package == 'common' and not folder.is_dir():
            raise ValueError(f'Missing canonical folder: {folder}')
        for file, is_dir in entries(folder):
            if is_dir or file.suffix.lower() != '.md' or file.name == HUMAN:
                continue
            if not file.name.startswith(prefix) or file.suffix != '.md':
                raise ValueError(f'Unknown canonical rule owner: {file}')
            key = file.relative_to(folder)
            if key in sources:
                raise ValueError(f'Canonical rule collision: {sources[key]} and {file}')
            sources[key] = file
    if not any(key.name.startswith('comm-') for key in sources):
        raise ValueError('No canonical shared rules found.')
    return sources


def rule_destinations(root):
    sources = canonical_rules(root)
    native = ordinary_directory(root / '.claude/rules', root)
    copies = {native / name: source for name, source in sources.items()}
    for file, is_dir in entries(native):
        if not is_dir and file.suffix.lower() == '.md' and file not in copies:
            raise ValueError(f'Unmanaged native rule: {file}; stop and resolve through INBOX.')
    return copies


def check_rule_copies(root):
    """Read-only verifier retained for installed callers and diagnostics."""
    copies = rule_destinations(root)
    for target, source in copies.items():
        expected = require_file(source, root)[0]
        if not expected.decode('utf-8').strip():
            raise ValueError(f'Empty canonical rule: {source}')
        actual = snapshot_input(target, root)
        if actual is None or actual[0] != expected:
            raise ValueError(f'Missing or different rule copy: {target}')
    return len(copies)


def skill_destinations(root):
    folders = {}
    for package, prefix in PACKAGES:
        folder = ordinary_directory(root / 'harness' / package / 'skills', root)
        if not folder.is_dir():
            continue
        for source in sorted(folder.iterdir()):
            if source.name == HUMAN and source.is_file():
                continue
            if not source.is_dir() or not source.name.startswith(prefix):
                raise ValueError(f'Unknown canonical skill owner: {source}')
            if not (source / 'SKILL.md').is_file():
                raise ValueError(f'Incomplete canonical skill: {source}')
            folders[source.name] = source
    copies, directories = {}, set()
    for client in SKILL_CLIENTS:
        native = ordinary_directory(root / client, root)
        if native.is_dir():
            for entry in native.iterdir():
                if entry.name.startswith(('comm-', 'proj-')) and entry.name not in folders:
                    raise ValueError(f'Unmanaged reserved skill name: {entry}; resolve through INBOX.')
        for name, folder in folders.items():
            target = ordinary_directory(native / name, root)
            directories.add(target)
            for file, is_dir in entries(folder):
                destination = target / file.relative_to(folder)
                if is_dir:
                    directories.add(destination)
                else:
                    copies[destination] = file
            for file, is_dir in entries(target):
                if (is_dir and file not in directories) or (not is_dir and file not in copies):
                    raise ValueError(f'Unexpected file or directory in managed skill: {file}')
    return copies, directories


def protected_difference(path, actual, expected):
    """Identify a mismatch without echoing arbitrary bytes from an unexpected version."""
    first = next((n for n, pair in enumerate(zip(expected, actual)) if pair[0] != pair[1]),
                 min(len(actual), len(expected)))
    return (f'Protected entrypoint differs: {path}; first differing byte offset {first}. '
            f'Canonical: {len(expected)} bytes, SHA-256 {hashlib.sha256(expected).hexdigest()}; '
            f'observed: {len(actual)} bytes, SHA-256 {hashlib.sha256(actual).hexdigest()}. '
            'Resolve through INBOX.')


def ensure(root):
    print(WARNING, flush=True)
    root = ordinary_directory(Path(root), root)
    with root_lock(root):
        marker = ordinary_path(root / PUBLICATION_MARKER)
        if marker.exists():
            raise ValueError(f'Unfinished publication: {marker}; resume the approved INBOX request.')
        script = ordinary_path(__file__)
        if not script.is_file():
            raise ValueError(f'Unsafe checker path: {script}')
        root = Path(os.path.normpath(root))
        common, project = root / 'harness/common', root / 'harness/project'
        if not ordinary_directory(common, root).is_dir():
            raise ValueError('harness/common is required; project-only is unsupported.')
        ordinary_directory(project, root)
        installed = common / 'checks/ensure_entrypoint_links.py'
        installed_bytes = require_file(installed, root)[0]
        if script != installed and require_file(script, root)[0] != installed_bytes:
            raise ValueError(f'Different checker version; run the installed checker directly: {installed}')
        # This structural symlink guard never opens inbox/evidence contents.
        ordinary_tree(root / 'harness')
        categories = load_project_skeleton(common, root)
        create_project = not project.exists()
        for package in [common] + ([] if create_project else [project]):
            if not require_file(package / 'INDEX.md', root)[0].decode('utf-8').strip():
                raise ValueError(f'Empty map: {package / "INDEX.md"}')

        copies = rule_destinations(root)
        rule_sources = set(copies.values())
        skills, directories = skill_destinations(root)
        copies.update(skills)
        for name in PROTECTED:
            copies[root / name] = common / 'base' / (name.split('.')[0] + '.template')

        originals, sources, repairs = {}, {}, []
        for target, source in copies.items():
            if source not in sources:
                sources[source] = require_file(source, root)
            expected = sources[source][0]
            if source in rule_sources or source.name == 'SKILL.md':
                if not expected.decode('utf-8').strip():
                    raise ValueError(f'Empty canonical file: {source}')
            if target == root / 'CLAUDE.md' and expected:
                raise ValueError(f'Canonical CLAUDE template must be empty: {source}')
            if target == root / 'AGENTS.md' and not expected.decode('utf-8').strip():
                raise ValueError(f'Empty canonical AGENTS template: {source}')
            actual = originals[target] = snapshot_input(target, root)
            if actual is not None and actual[0] == expected:
                continue
            if target.parent == root and actual is not None:
                raise ValueError(protected_difference(target, actual[0], expected))
            repairs.append(target)

        for folder in directories:
            ordinary_directory(folder, root)
        for source, snapshot in sources.items():
            if snapshot_input(source, root) != snapshot:
                raise ValueError(f'Canonical file changed during checking: {source}')
        for target, snapshot in originals.items():
            if snapshot_input(target, root) != snapshot:
                raise ValueError(f'Working file changed during checking: {target}')

        changed = []
        try:
            if create_project:
                create_project_skeleton(project, categories)
                changed.append(project)
            if repairs:
                print('Восстановление рабочих файлов из канонических источников.', flush=True)
            for folder in sorted(directories, key=lambda p: (len(p.parts), p)):
                if not ordinary_directory(folder, root).exists():
                    folder.mkdir(parents=True, exist_ok=True)
                    changed.append(folder)
            for target in repairs:
                source = copies[target]
                expected = sources[source]
                if snapshot_input(source, root) != expected:
                    raise ValueError(f'Canonical file changed before recovery: {source}')
                ordinary_directory(target.parent, root).mkdir(parents=True, exist_ok=True)
                replace_input(target, originals[target], expected[0], root, expected[1][-1])
                changed.append(target)
                if require_file(target, root)[0] != expected[0]:
                    raise ValueError(f'Incomplete recovery: {target}')
        except (OSError, ValueError) as error:
            if changed:
                raise ValueError(f'{error}; already updated: {", ".join(map(str, changed))}') from error
            raise
        return changed


def main():
    if len(sys.argv) > 2:
        print('Usage: python3 ensure_entrypoint_links.py [project-root]', file=sys.stderr)
        return 2
    try:
        changed = ensure(Path(sys.argv[1]) if len(sys.argv) == 2 else Path.cwd())
    except (ImportError, OSError, UnicodeError, ValueError) as error:
        print(f'Entrypoint check failed: {error}', file=sys.stderr)
        return 2
    if changed:
        print('Entrypoint check completed. Изменены: ' + ', '.join(map(str, changed)))
        print('Начните новую сессию: восстановленный контекст должен загрузиться до задачи.')
        return RESTART_REQUIRED
    print('Entrypoint check completed')
    return 0


if __name__ == '__main__':
    sys.exit(main())
