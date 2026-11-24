"""Check the harness installation and recover working files from its published packages."""
import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from contextlib import contextmanager, nullcontext
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
RULE_MISMATCH = 4
ENTRYPOINT_REPAIR_REQUIRED = 5
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


def decode_text(path, raw):
    try:
        return raw.decode('utf-8')
    except UnicodeDecodeError as error:
        raise ValueError(f'Invalid UTF-8 in {path} at byte {error.start}') from error


def load_project_skeleton(common, root):
    path = common / 'base/project-skeleton.json'
    raw, _ = require_file(path, root)
    try:
        template = json.loads(decode_text(path, raw))
    except json.JSONDecodeError as error:
        raise ValueError(f'Invalid JSON in {path}: {error}') from error
    categories = template.get('categories') if isinstance(template, dict) else None
    if not isinstance(categories, dict) or not categories:
        raise ValueError(f'Project skeleton requires nonempty categories: {path}')
    for name, detail in categories.items():
        if (not re.fullmatch(r'[a-z0-9][a-z0-9_-]*(?:/[a-z0-9][a-z0-9_-]*)*', name)
                or not isinstance(detail, dict)
                or any(not isinstance(detail.get(k), str) or not detail[k].strip()
                       for k in ('purpose', 'example'))):
            raise ValueError(f'Invalid project skeleton category in {path}: {name}')
    return categories


def create_project_skeleton(project, categories):
    """Create only the missing project. A failure never exposes a partial skeleton."""
    with tempfile.TemporaryDirectory(prefix='.project-skeleton-', dir=project.parent) as temporary:
        staging = Path(temporary)
        (staging / HUMAN).write_text(
            '# Проектный harness\n\nЗдесь сохраняются материалы проекта. Например, '
            'согласованный контракт можно поместить в base/project-contract.md.\n',
            encoding='utf-8')
        rows = ['# Проектный harness', '', '| Назначение | Открой каталог |', '|---|---|']
        for name, detail in categories.items():
            directory = staging / name
            directory.mkdir(parents=True, exist_ok=True)
            (directory / HUMAN).write_text(f'# {name}\n\n{detail["purpose"]}\n\n'
                                           f'Пример: {detail["example"]}\n', encoding='utf-8')
            label = MAP_LABELS.get(name, detail['purpose'])
            rows.append(f'| {label} | [{directory.name}]({name}) |')
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


class RuleMismatch(ValueError):
    """The working always loaded rules differ from their published sources."""


def rule_destinations(root):
    sources = canonical_rules(root)
    native = ordinary_directory(root / '.claude/rules', root)
    copies = {native / name: source for name, source in sources.items()}
    for file, is_dir in entries(native):
        if not is_dir and file.suffix.lower() == '.md' and file not in copies:
            raise RuleMismatch(f'Unmanaged native rule: {file}; stop and resolve through INBOX.')
    return copies


def rule_snapshots(root, *, collect_read_errors=False):
    """Collect matching sources and working copies without modifying either tree."""
    snapshots = {}
    differences = []
    for target, source in rule_destinations(root).items():
        expected = require_file(source, root)
        if not decode_text(source, expected[0]).strip():
            raise ValueError(f'Empty canonical rule: {source}')
        try:
            actual = snapshot_input(target, root)
        except PermissionError as error:
            if not collect_read_errors:
                raise
            differences.append(f'Cannot read rule copy: {target} ({error.strerror})')
            continue
        snapshots[target] = (source, expected, actual)
        if actual is None or actual[0] != expected[0]:
            reason = 'absent' if actual is None else 'bytes differ'
            differences.append(f'Missing or different rule copy: {target} ({reason}; canonical: {source})')
    return snapshots, differences


def check_rule_copies(root):
    """Verify published rule copies without writing files or loading client entrypoints."""
    check_publication_marker(root)
    snapshots, differences = rule_snapshots(root, collect_read_errors=True)
    check_publication_marker(root)
    if differences:
        raise RuleMismatch('\n'.join(differences))
    return len(snapshots)


def startup_snapshot(root):
    """Capture the published startup set and all safely readable working copies."""
    check_publication_marker(root)
    base = root / 'harness/common/base'
    native = root / '.claude/rules'
    sources = canonical_rules(root)
    copies = {root / name: base / Path(name).with_suffix('.template') for name in PROTECTED}
    copies.update({native / relative: source for relative, source in sources.items()})
    snapshots = {}
    differences = {}
    unavailable = 'недоступен для чтения'
    for target, source in copies.items():
        try:
            expected = require_file(source, root)
        except (OSError, ValueError):
            differences[source] = unavailable
            continue
        try:
            observed = snapshot_input(target, root)
        except (OSError, ValueError):
            differences[target] = unavailable
            continue
        snapshots[target] = (source, expected, observed)
        if observed is None:
            differences[target] = 'отсутствует'
        elif hashlib.sha256(observed[0]).digest() != hashlib.sha256(expected[0]).digest():
            differences[target] = 'отличается от канона'

    try:
        for path, is_dir in entries(native):
            if not is_dir and path.suffix.lower() == '.md' and path.name != HUMAN and path not in copies:
                differences[path] = 'лишний'
    except OSError as error:
        differences[Path(error.filename) if error.filename else native] = unavailable
    except ValueError:
        differences[native] = unavailable
    check_publication_marker(root)
    return snapshots, differences


def print_startup_differences(root, differences):
    for path, status in sorted(differences.items()):
        print(f'{path.relative_to(root).as_posix()}\t{status}')


def startup_git(root, env, *args, data=None, allowed=(0,)):
    result = subprocess.run(['git', '--no-replace-objects', *args], cwd=root, env=env,
                            input=data, capture_output=True, check=False)
    if result.returncode not in allowed:
        reason = os.fsdecode(result.stderr).strip()
        raise ValueError(f'Резервный коммит: git {args[0]}: {reason or result.returncode}')
    return result.stdout


def backup_startup_files(root, originals):
    """Commit the exact recovery bytes without writing the user's index or branch."""
    env = {name: value for name, value in os.environ.items() if not name.startswith('GIT_')}

    def git(*args, data=None, allowed=(0,)):
        return startup_git(root, env, *args, data=data, allowed=allowed)

    git_root = Path(os.fsdecode(git('rev-parse', '--show-toplevel').rstrip(b'\r\n')))
    if not os.path.samefile(root, git_root):
        raise ValueError(f'Резервный коммит требует отдельного Git-корня проекта: {root}')
    paths = {path.relative_to(root).as_posix(): original for path, original in originals.items()}
    parent = git('rev-parse', '--verify', '--quiet', 'HEAD', allowed=(0, 1)).decode().strip()
    with tempfile.TemporaryDirectory(prefix='harness-backup-index-') as directory:
        env['GIT_INDEX_FILE'] = str(Path(directory) / 'index')
        git('read-tree', parent or '--empty')
        for path, (contents, attributes) in paths.items():
            blob = git('hash-object', '-w', '--stdin', data=contents).decode().strip()
            mode = '100755' if attributes[-1] & stat.S_IXUSR else '100644'
            git('update-index', '--add', '--cacheinfo', mode, blob, path)
        tree = git('write-tree').decode().strip()
        parent_args = ('-p', parent) if parent else ()
        commit = git('commit-tree', tree, *parent_args, '-m', 'Back up managed harness files').decode().strip()
        changed = git('diff-tree', '--root', '--no-commit-id', '-r', '--name-only', '-z', commit)
        if not set(filter(None, os.fsdecode(changed).split('\0'))) <= paths.keys():
            raise ValueError(f'Резервный коммит содержит посторонние пути: {commit}')
        for path, (contents, _) in paths.items():
            copied = git('cat-file', 'blob', f'{commit}:{path}')
            if hashlib.sha256(copied).digest() != hashlib.sha256(contents).digest():
                raise ValueError(f'Неверные байты резервного коммита {commit}: {path}')
        git('update-ref', f'refs/harness/backups/{commit}', commit)
    return commit, sorted(paths)


def restore_startup_copies(root):
    """Restore only managed working copies after backing up existing revisions."""
    with root_lock(root):
        snapshots, differences = startup_snapshot(root)
        if any(status == 'недоступен для чтения' for status in differences.values()):
            print_startup_differences(root, differences)
            return RULE_MISMATCH
        if not differences:
            print('OK')
            return 0

        protected = {root / name for name in PROTECTED}
        extras = {path for path, status in differences.items() if status == 'лишний'}
        originals = {path: snapshots[path][2] for path in differences
                     if path not in extras and snapshots[path][2] is not None and
                     (path not in protected or snapshots[path][2][0])}
        originals.update({path: require_file(path, root) for path in extras})
        if originals:
            commit, paths = backup_startup_files(root, originals)
            print(f'Резервный коммит {commit}', flush=True)
            print('\n'.join(paths), flush=True)

        for target in differences:
            if target in extras:
                if snapshot_input(target, root) != originals[target]:
                    raise ValueError(f'Лишний файл изменился после резервного коммита: {target}')
                continue
            source, expected, observed = snapshots[target]
            if snapshot_input(source, root) != expected or snapshot_input(target, root) != observed:
                raise ValueError(f'Файл изменился до восстановления: {target}')
        for target in sorted(differences):
            if target in extras:
                if snapshot_input(target, root) != originals[target]:
                    raise ValueError(f'Лишний файл изменился до удаления: {target}')
                target.unlink()
                continue
            source, expected, observed = snapshots[target]
            if snapshot_input(source, root) != expected:
                raise ValueError(f'Канон изменился до восстановления: {source}')
            ordinary_directory(target.parent, root).mkdir(parents=True, exist_ok=True)
            replace_input(target, observed, expected[0], root, expected[1][-1])

        _, remaining = startup_snapshot(root)
        if remaining:
            print_startup_differences(root, remaining)
            return RULE_MISMATCH
        print('OK')
        print('Начните новую сессию после восстановления из опубликованного канона.')
        return RESTART_REQUIRED


def restore_rule_copies(root):
    """Restore managed always loaded rules only, after an explicit recovery request."""
    with root_lock(root):
        check_publication_marker(root)
        snapshots, _ = rule_snapshots(root)
        repairs = {target: state for target, state in snapshots.items()
                   if state[2] is None or state[1][0] != state[2][0]}
        if repairs:
            print('Восстановление рабочих always loaded правил из опубликованного канона.', flush=True)
        changed = []
        for target, (source, expected, actual) in repairs.items():
            try:
                if snapshot_input(source, root) != expected:
                    raise ValueError(f'Canonical file changed before recovery: {source}')
                ordinary_directory(target.parent, root).mkdir(parents=True, exist_ok=True)
                replace_input(target, actual, expected[0], root, expected[1][-1])
                changed.append(target)
            except (OSError, ValueError) as error:
                updated = ', '.join(map(str, changed)) or 'none'
                pending = ', '.join(str(path) for path in repairs if path not in changed)
                raise ValueError(f'{error}; already updated: {updated}; pending: {pending}') from error
        check_rule_copies(root)
        return changed


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


def protected_template(source, root):
    expected = require_file(source, root)
    if source.name == 'CLAUDE.template' and expected[0]:
        raise ValueError(f'Canonical CLAUDE template must be empty: {source}')
    if source.name == 'AGENTS.template' and not decode_text(source, expected[0]).strip():
        raise ValueError(f'Empty canonical AGENTS template: {source}')
    return expected


def parse_entrypoint_approvals(values):
    approvals = {}
    for value in values:
        name, *digests = value.split(':')
        if (name not in PROTECTED or name in approvals or len(digests) != 2 or
                any(not re.fullmatch(r'[0-9a-f]{64}', digest) for digest in digests)):
            raise ValueError(f'Invalid or duplicate approved entrypoint: {name}')
        approvals[name] = tuple(digests)
    return approvals


def verify_entrypoint_backup(root, commit, approvals):
    """Git proves the backup bytes; the published templates supply recovery bytes."""
    if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', commit):
        raise ValueError('Backup commit must be a full Git object ID.')
    env = {name: value for name, value in os.environ.items() if not name.startswith('GIT_')}

    def git(*args):
        result = subprocess.run(['git', '--no-replace-objects', *args], cwd=root,
                                env=env, capture_output=True, check=False)
        if result.returncode:
            raise ValueError(f'Cannot verify backup commit {commit} in {root}.')
        return result.stdout

    git_root = Path(os.fsdecode(git('rev-parse', '--show-toplevel').rstrip(b'\r\n')))
    if not os.path.samefile(root, git_root) or git('rev-parse', '--verify', 'HEAD').strip() != commit.encode():
        raise ValueError(f'Backup commit must be HEAD of this installation: {root}')
    for name, (observed, _) in approvals.items():
        if hashlib.sha256(git('cat-file', 'blob', f'{commit}:{name}')).hexdigest() != observed:
            raise ValueError(f'Backup commit bytes differ from the approved version: {root / name}')


class EntrypointRepairRequired(ValueError):
    """A protected entrypoint can be repaired automatically before the next session."""


def check_start_entrypoints(root, backup_commit=None, approvals=None, *, no_repair=False):
    """Check protected inputs, repairing only empty/missing or explicitly backed-up files."""
    # The Windows writer lock can create a file. Read-only checks use snapshots instead.
    with nullcontext() if no_repair else root_lock(root):
        check_publication_marker(root)
        repairs = {}
        conflicts = []
        checked = []
        if backup_commit is not None:
            verify_entrypoint_backup(root, backup_commit, approvals)
        for name in PROTECTED:
            path = root / name
            source = root / 'harness/common/base' / path.with_suffix('.template').name
            expected = protected_template(source, root)
            actual = snapshot_input(path, root)
            if no_repair:
                checked.extend(((source, expected), (path, actual)))
            if backup_commit is not None:
                if name not in approvals:
                    continue
                observed, canonical = approvals[name]
                if hashlib.sha256(expected[0]).hexdigest() != canonical:
                    raise ValueError(f'Canonical entrypoint changed since approval: {source}')
                if actual is not None and actual[0] == expected[0]:
                    continue
                if actual is None or hashlib.sha256(actual[0]).hexdigest() != observed:
                    raise ValueError(f'Working entrypoint changed since approval: {path}')
                reason = f'резервный коммит {backup_commit} проверен'
            else:
                if actual is not None and actual[0] == expected[0]:
                    continue
                if actual is not None and actual[0]:
                    conflicts.append(protected_difference(path, actual[0], expected[0]))
                    continue
                reason = 'файл отсутствует' if actual is None else 'файл пуст'
            repairs[path] = (source, expected, actual, reason)

        if no_repair:
            for path, original in checked:
                if snapshot_input(path, root) != original:
                    raise ValueError(f'Entrypoint changed during checking: {path}')
            check_publication_marker(root)
            if repairs:
                needed = '\n'.join(f'{path} ({reason}); образец: {source}'
                                   for path, (source, _, _, reason) in repairs.items())
                notice = 'Защищённые входы требуют восстановления из канона:\n' + needed
                if not conflicts:
                    raise EntrypointRepairRequired(notice)
                conflicts.append(notice)
            repairs.clear()

        changed = []
        for path, (source, expected, actual, reason) in repairs.items():
            try:
                if snapshot_input(source, root) != expected:
                    raise ValueError(f'Canonical file changed before recovery: {source}')
                print(f'Восстановление защищённого входа {path} ({reason}) из {source}.', flush=True)
                replace_input(path, actual, expected[0], root, expected[1][-1])
                changed.append(path)
                if require_file(path, root)[0] != expected[0]:
                    raise ValueError(f'Incomplete recovery: {path}')
            except (OSError, ValueError) as error:
                updated = ', '.join(map(str, changed)) or 'none'
                pending = ', '.join(str(target) for target in repairs if target not in changed) or 'none'
                raise ValueError(f'{error}; already updated: {updated}; pending: {pending}') from error
        if conflicts:
            if changed:
                print('Начните новую сессию после разрешения оставшихся расхождений.', flush=True)
            raise ValueError('\n'.join(conflicts) + '\nПредложите явно согласовать через INBOX '
                             'резервный коммит и последующее восстановление этих входов из канона.')
        return changed


def check_publication_marker(root):
    marker = ordinary_path(root / PUBLICATION_MARKER)
    if marker.exists():
        raise ValueError(f'Unfinished publication: {marker}; resume the approved INBOX request.')


def ensure(root):
    print(WARNING, flush=True)
    root = ordinary_directory(Path(root), root)
    with root_lock(root):
        check_publication_marker(root)
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
            index = package / 'INDEX.md'
            if not decode_text(index, require_file(index, root)[0]).strip():
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
                sources[source] = (protected_template(source, root) if target.parent == root
                                   else require_file(source, root))
            expected = sources[source][0]
            if source in rule_sources or source.name == 'SKILL.md':
                if not decode_text(source, expected).strip():
                    raise ValueError(f'Empty canonical file: {source}')
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

        missing_folders = [folder for folder in sorted(directories, key=lambda p: (len(p.parts), p))
                           if not folder.exists()]
        planned = ([project] if create_project else []) + missing_folders + repairs
        if planned:
            print('Восстановление рабочих файлов из канонических источников.', flush=True)
        changed = []
        try:
            if create_project:
                create_project_skeleton(project, categories)
                changed.append(project)
            for folder in missing_folders:
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
            completed = set(changed)
            remaining = [str(path) for path in planned if path not in completed]
            raise ValueError(f'{error}; already updated: {", ".join(map(str, changed)) or "none"}; '
                             f'pending: {", ".join(remaining) or "none"}') from error
        return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--check-rules', action='store_true', help='Compare rule copies without writing.')
    modes.add_argument('--check-startup', action='store_true',
                       help='Compare both protected inputs and all rules in one read-only pass.')
    modes.add_argument('--restore-startup', action='store_true',
                       help='Restore managed startup copies after verifying a backup commit.')
    modes.add_argument('--restore-rules', action='store_true', help='Recover managed rule copies only.')
    modes.add_argument('--check-start-entrypoints', action='store_true',
                       help='Check AGENTS.md and CLAUDE.md and recover missing or empty inputs.')
    modes.add_argument('--restore-start-entrypoints', metavar='BACKUP_COMMIT',
                       help='Restore only the confirmed protected entries backed up in this commit.')
    parser.add_argument('--no-repair', action='store_true',
                        help='With --check-start-entrypoints, compare without writing and report required repair.')
    parser.add_argument('--entrypoint', action='append', default=[], metavar='NAME:OBSERVED:CANONICAL',
                        help='File and both SHA-256 values approved for protected recovery.')
    parser.add_argument('project_root', nargs='?', type=Path, default=Path.cwd())
    args = parser.parse_args()
    if bool(args.entrypoint) != (args.restore_start_entrypoints is not None):
        parser.error('--entrypoint and --restore-start-entrypoints must be used together.')
    if args.no_repair and not args.check_start_entrypoints:
        parser.error('--no-repair requires --check-start-entrypoints.')
    root = args.project_root.absolute()
    try:
        if args.check_startup:
            _, differences = startup_snapshot(root)
            if not differences:
                print('OK')
                return 0
            print_startup_differences(root, differences)
            return RULE_MISMATCH
        if args.restore_startup:
            return restore_startup_copies(root)
        if args.check_rules:
            count = check_rule_copies(root)
            print(f'Rule copies match the published canon: {count}')
            return 0
        if args.check_start_entrypoints or args.restore_start_entrypoints is not None:
            changed = check_start_entrypoints(root, args.restore_start_entrypoints,
                                              parse_entrypoint_approvals(args.entrypoint),
                                              no_repair=args.no_repair)
        elif args.restore_rules:
            changed = restore_rule_copies(root)
        else:
            changed = ensure(root)
    except EntrypointRepairRequired as error:
        print(error, file=sys.stderr)
        return ENTRYPOINT_REPAIR_REQUIRED
    except (ImportError, OSError, UnicodeError, ValueError) as error:
        print(f'Entrypoint check failed: {error}', file=sys.stderr)
        return RULE_MISMATCH if (args.check_rules or args.restore_rules) and isinstance(error, RuleMismatch) else 2
    if changed:
        print('Entrypoint check completed. Изменены: ' + ', '.join(map(str, changed)))
        print('Начните новую сессию: восстановленный контекст должен загрузиться до задачи.')
        return RESTART_REQUIRED
    print('Entrypoint check completed')
    return 0


if __name__ == '__main__':
    sys.exit(main())
