"""Run a paired U4 native cell in a disposable Linux mount namespace.

Prepare and bootstrap common-only and common-project with prepare_u2_fixtures.py.
Pass the prepared root, a client, map policy, task and repeat number. Each call
creates a fresh workspace and clean profile; no agent trace is written to the
repository. Record only the sanitized summary outside the tested workspace.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time


OWNER = Path('harness/common/rules/comm-instruction-order.md')
MANDATORY = 'После сверки до задачи прочитай [INDEX.md](/harness/common/INDEX.md), затем [INDEX.md](/harness/project/INDEX.md).'
OPTIONAL = 'При необходимости навигации прочитай [INDEX.md](/harness/common/INDEX.md), затем [INDEX.md](/harness/project/INDEX.md).'
PROMPTS = {
    'answer': 'Сколько минут в трёх часах? Ответь по-русски.',
    'history': 'Какое значение параметра cache_ttl указано в действующей спецификации приложения? Укажи файл, из которого получен ответ.',
    'explain': 'Объясни, какое значение тайм-аута сейчас задано в конфигурации приложения app.toml. Ответь по-русски.',
    'change': 'Измени общее значение timeout в app.toml с 20 на 25 секунд. Работай только с этим параметром. Коммит не нужен.',
}
ERRORS = {
    'login_required': ('not logged in', 'not authenticated', 'missing authentication', 'please run /login', 'authentication required'),
    'unauthorized': ('unauthorized', '401 unauthorized', 'invalid authentication'),
    'dns': ('dns error', 'failed to lookup address', 'name or service not known', 'temporary failure in name resolution'),
    'connection': ('unable to connect', 'error sending request', 'connection refused', 'error connecting', 'network is unreachable', 'stream disconnected'),
    'quota': ('insufficient_quota', 'rate limit', 'usage limit'),
    'scope': ('operation not permitted', 'permission denied', 'read-only file system'),
    'unavailable_model': ('model is not available', 'model is not supported'),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fixture_versions(work):
    paths = [OWNER, Path('AGENTS.md'), Path('harness/common/checks/ensure_entrypoint_links.py'),
             Path('harness/common/skills/comm-process-harness-inbox/references/workflow.md'),
             Path('harness/common/skills/comm-validate-harness-instructions/references/validation.md')]
    return {str(path):digest((work/path).read_bytes()) for path in paths}


# Local diagnostics run without login and with AF_INET/AF_INET6 sockets denied.
# libseccomp's filter survives exec and applies to subprocesses.
LOCAL_ONLY = r"""
import ctypes as c, errno, os, socket, sys
lib = c.CDLL('libseccomp.so.2')
lib.seccomp_init.argtypes = [c.c_uint32]
lib.seccomp_init.restype = c.c_void_p
lib.seccomp_syscall_resolve_name.argtypes = [c.c_char_p]
class Compare(c.Structure):
    _fields_ = [('arg', c.c_uint), ('op', c.c_int), ('value', c.c_uint64), ('second', c.c_uint64)]
lib.seccomp_rule_add_array.argtypes = [c.c_void_p,c.c_uint32,c.c_int,c.c_uint,c.POINTER(Compare)]
lib.seccomp_load.argtypes = [c.c_void_p]
ctx = lib.seccomp_init(0x7fff0000)
assert ctx
for family in (socket.AF_INET, socket.AF_INET6):
    cmp = Compare(0, 4, family, 0)
    assert lib.seccomp_rule_add_array(ctx, 0x50000 | errno.EPERM,
        lib.seccomp_syscall_resolve_name(b'socket'), 1, c.byref(cmp)) == 0
assert lib.seccomp_load(ctx) == 0
for family in (socket.AF_INET, socket.AF_INET6):
    try:
        socket.socket(family)
    except PermissionError:
        continue
    raise RuntimeError('offline diagnostic cannot run')
os.execvp(sys.argv[1], sys.argv[1:])
"""


def inspect_prompt(work, policy, task, repeat, output, code):
    result = {'client': 'codex', 'policy': policy, 'task': task, 'repeat': repeat,
              'local_only': True, 'exit': code, 'policy_sha256': digest((work / OWNER).read_bytes()),
              'model_answers': 0, 'session_usage': None, 'usage_before_task': None}
    if code:
        return result
    contents = []
    def collect(value):
        if isinstance(value, str):
            contents.append(value)
        elif isinstance(value, list):
            for entry in value:
                collect(entry)
        elif isinstance(value, dict):
            for val in value.values():
                collect(val)
    collect(json.loads(output))
    combined = '\n'.join(contents)
    names = set()
    descriptions = []
    bodies = []
    for file in (work / '.agents/skills').glob('*/SKILL.md'):
        text = file.read_text()
        metadata = text.split('---', 2)[1].splitlines()
        description = next(line.split(':', 1)[1].strip() for line in metadata if line.startswith('description:'))
        if any(description in string for string in contents):
            descriptions.append(file.parent.name)
        if any(text.strip() in string for string in contents):
            bodies.append(file.parent.name)
        if file.parent.name in combined:
            names.add(file.parent.name)
    result.update(native_catalogue={'project_expected': len(list((work / '.agents/skills').glob('*/SKILL.md'))),
                                     'project_named_in_prompt': sorted(names),
                                     'exact_description_count': len(descriptions),
                                     'full_skill_count': len(bodies)},
                  entrypoint_complete=any((work / 'AGENTS.md').read_text().strip() in s for s in contents),
                  full_rule_texts_in_prompt=sum(any(f.read_text().strip() in s for s in contents)
                      for f in (work / '.claude/rules').rglob('*.md') if f.name != 'README.human.md'))
    return result


def prepare(source, policy, base):
    work = base / 'workspace'
    def exclude(parent, names):
        relative = Path(parent).relative_to(source).as_posix()
        blocked = {'__pycache__', '.pytest_cache', '.git', '.venv'}
        if any(relative.endswith('/' + part) for part in ('inbox', 'handoffs', 'docs/plans', 'testing/evidence')):
            blocked.update(name for name in names if name != 'README.human.md')
        return blocked
    shutil.copytree(source, work, ignore=exclude)
    file = work / OWNER
    original = file.read_text()
    native = work / '.claude/rules' / OWNER.name
    assert native.read_bytes() == file.read_bytes()
    assert original.count(MANDATORY) == 1
    if policy == 'optional':
        file.write_text(original.replace(MANDATORY, OPTIONAL))
        native.write_bytes(file.read_bytes())
    (work / 'app.toml').write_text('timeout = 20\n')
    (work / 'harness/project/specs/cache-settings.md').write_text('# Текущая спецификация\n\ncache_ttl = 45\n')
    evidence = work / 'harness/project/testing/evidence/work'
    evidence.mkdir(exist_ok=True, parents=True)
    (evidence / 'old-cache-settings.md').write_text('# Снимок прежнего запуска\n\ncache_ttl = 15\n')
    return work


def mount_command(work, client, name, use_login):
    exe = Path(shutil.which(name)).resolve(strict=True)
    # Only system runtime, binaries, disposable project/profile are visible.
    argv = ['bwrap', '--die-with-parent', '--new-session', '--unshare-pid',
            '--ro-bind', '/usr', '/usr', '--ro-bind', '/etc', '/etc',
            '--symlink', 'usr/bin', '/bin', '--symlink', 'usr/lib', '/lib',
            '--symlink', 'usr/lib64', '/lib64', '--dev', '/dev', '--proc', '/proc',
            '--tmpfs', '/tmp', '--bind', str(client), '/profile',
            '--bind', str(work), '/workspace', '--chdir', '/workspace']
    # Some hosts keep the resolver target outside /etc (including WSL).
    resolver = Path('/etc/resolv.conf')
    if use_login and resolver.is_symlink():
        target = resolver.resolve(strict=True)
        argv += ['--ro-bind', str(target), str(target)]
    if name == 'codex':
        argv += ['--ro-bind', str(exe.parent), '/opt/client']
        # Keep actual login material with the CLI. Never copy it or parse it.
        # Child tool subprocesses receive no credential in their environment.
        existing = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'auth.json'
        if use_login and existing.is_file() and not existing.is_symlink():
            argv += ['--ro-bind', str(existing), '/profile/.codex/auth.json']
    else:
        argv += ['--ro-bind', str(exe), '/opt/client/claude']
    argv += ['--clearenv', '--setenv', 'PATH', '/opt/client:/usr/bin:/bin',
             '--setenv', 'LANG', 'C.UTF-8', '--setenv', 'HOME', '/profile',
             '--setenv', 'CODEX_HOME', '/profile/.codex',
             '--setenv', 'CLAUDE_CONFIG_DIR', '/profile/.claude', '--']
    return argv


def evaluate(root, client_name, policy, task, repeat, local_only=False):
    parent = Path(tempfile.mkdtemp(prefix='startup-u4-native-'))
    work = prepare(root, policy, parent)
    home = parent / 'client'
    (home / '.codex').mkdir(parents=True)
    (home / '.claude').mkdir()
    launch = mount_command(work, home, client_name, use_login=not local_only)
    prompt = PROMPTS[task]
    if client_name == 'codex':
        access = 'write' if task == 'change' else 'read'
        settings = (f'default_permissions = "u4"\napproval_policy = "never"\n'
                    '[permissions.u4.filesystem]\n":root" = "read"\n"/profile" = "deny"\n'
                    f'"/workspace" = "{access}"\n[permissions.u4.network]\nenabled = false\n')
        if not local_only:
            (home / '.codex/config.toml').write_text(settings)
            marker = home / '.codex/private-probe'
            marker.write_text('fake-canary')
            # Verify a dependent shell sees project data but cannot read the private profile.
            result = subprocess.run(launch + ['codex', 'sandbox', '-P', 'u4', '--', '/bin/sh', '-c',
                'test -r /workspace/AGENTS.md && ! cat /profile/.codex/private-probe >/dev/null 2>&1'],
                capture_output=True, timeout=20)
            if result.returncode:
                raise RuntimeError('Private profile isolation probe failed before any model call.')
        # Session counters stay under the disposable 0700 parent; never publish raw sessions.
        cmd = ['codex', 'exec', '--skip-git-repo-check',
               '-c', 'features.multi_agent=false', '--json', '-']
    else:
        cmd = ['claude', '-p', '--output-format', 'stream-json', '--verbose', '--no-session-persistence',
               '--setting-sources', 'project', '--strict-mcp-config', '--permission-mode', 'dontAsk',
               '--allowedTools', 'Read,Glob,Grep,Bash(python3 -B harness/common/checks/ensure_entrypoint_links.py),Bash(cat *),Bash(rg *),Bash(ls *)' + (',Edit' if task == 'change' else '')]
    if local_only:
        if client_name == 'codex':
            cmd = ['codex', 'debug', 'prompt-input', '-c', 'features.multi_agent=false', prompt]
        cmd = ['/usr/bin/python3', '-c', LOCAL_ONLY, *cmd]
    start = time.monotonic()
    stdout_path = parent / 'native-output.jsonl'
    stderr_path = parent / 'native-stderr.log'
    with stdout_path.open('w') as stdout, stderr_path.open('w') as error:
        proc = subprocess.Popen(launch + cmd, cwd=parent, stdin=subprocess.PIPE,
                                stdout=stdout, stderr=error, text=True)
        try:
            proc.communicate(prompt, timeout=360)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)
    output, stderr = stdout_path.read_text(), stderr_path.read_text()
    if local_only and client_name == 'codex':
        result = inspect_prompt(work, policy, task, repeat, output, proc.returncode)
        result['install'] = root.name
        result['fixture_sha256'] = fixture_versions(work)
        return result
    events = []
    for line in output.splitlines():
        try:
            event = json.loads(line)
            if isinstance(event, dict):
                events.append(event)
        except ValueError:
            continue
    messages = (output + stderr).lower()
    error_types = [key for key, needles in ERRORS.items() if proc.returncode and any(n in messages for n in needles)]
    if proc.returncode == -9:
        error_types.append('timeout')
    result = {'client': client_name, 'install': root.name, 'policy': policy, 'task': task, 'repeat': repeat,
              'policy_sha256': digest((work / OWNER).read_bytes()), 'prompt_sha256': digest(prompt.encode()),
              'exit': proc.returncode, 'seconds': round(time.monotonic() - start, 1), 'error_classes': error_types,
              'event_types': sorted({e.get('type', '') for e in events}),
              'model_answers': 0, 'actions': [], 'session_usage': None, 'usage_before_task': None,
              'fixture_sha256':fixture_versions(work)}
    for e in events:
        item = e.get('item', {})
        if e.get('type') == 'turn.completed':
            result['session_usage'] = e.get('usage')
        if e.get('type') == 'result' and not e.get('is_error'):
            result['session_usage'] = e.get('usage')
        if e.get('type') == 'item.completed' and item.get('type') == 'agent_message':
            result['model_answers'] += 1
        if e.get('type') == 'system' and e.get('subtype') == 'init':
            project_names = {p.parent.name for p in (work / '.claude/skills').glob('*/SKILL.md')}
            listed = set(e.get('skills', []))
            result['native_catalogue'] = {'project_expected': len(project_names),
                                          'project_listed': sorted(project_names & listed),
                                          'missing': sorted(project_names - listed),
                                          'additional_count': len(listed - project_names),
                                          'plugins_count': len(e.get('plugins', []))}
        if e.get('type') == 'assistant' and not e.get('is_api_error_message') and not e.get('error'):
            result['model_answers'] += int(any(x.get('type')=='text' for x in e.get('message', {}).get('content', [])))
        if e.get('type') == 'item.completed' and item.get('type') == 'command_execution':
            result['actions'].append({'kind': 'command', 'exit': item.get('exit_code')})
    # Store raw output only locally for manual scoring; caller gets sanitized JSON.
    # Parent was created by mkdtemp with mode 0700.
    result['local_trace'] = str(parent)
    result['local_only'] = local_only
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('client', choices=('codex', 'claude'))
    parser.add_argument('policy', choices=('mandatory', 'optional'))
    parser.add_argument('task', choices=tuple(PROMPTS))
    parser.add_argument('repeat', type=int, choices=(1, 2))
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--local-only', action='store_true', help='Block network sockets and omit all login material; inspect native initialization only.')
    group.add_argument('--model-run', action='store_true', help='Execute a native model session in the disposable workspace.')
    args = parser.parse_args()
    print(json.dumps(evaluate(args.root.resolve(), args.client, args.policy, args.task, args.repeat, args.local_only)))
