"""Reuse 2026-10-06 native probe; copy every candidate skill for routing tests."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time

REQUEST = Path(__file__).resolve().parent
CANDIDATE = REQUEST / 'candidate'
REPO = REQUEST.parents[3]
assert REPO / 'harness/common/inbox' == REQUEST.parent, 'Native probes must mask the entire repository'
SKILL = 'comm-create-lazy-claude-codex-skills'
COMMON_TASK = '''Read-only. До чтения файлов перечисли в первом сообщении имена и описания локальных навыков, предоставленных нативным каталогом этой сессии. Не ищи их на диске ради этого перечисления; если каталог отсутствует, скажи это. Первой командой выполни обязательный старт. Не читай тела README.human.md. Подготовь в ответе проект обновления агентских инструкций для Codex и Claude: переносим common в новый проект; для существующего project с docs/epl-import предлагают общую specs/, но решение пользователя и отдельное подтверждение пользы всем проектам ещё не получены. Инструкция должна определить два режима установки, поведение project-only, источник каркаса, допустимость включения specs/ сейчас и публикации при неуспехе проверки Claude. Ничего не изменяй кроме разрешённых действий стартовой проверки. Верни краткий проект инструкции, условия проверки/публикации и пути прочитанных инструкций.'''
PROMPTS = {
    'implicit': COMMON_TASK,
    'explicit': f'Используй локальный скилл {SKILL}, прочитай его собственный references/validation-and-publication.md. ' + COMMON_TASK,
}


def file_state(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}


def probe(agent, mode, invocation, analysis_cli=None, sandbox='read-only', capture_files=False, timeout_seconds=150):
    with tempfile.TemporaryDirectory(prefix='two-modes-native-') as temporary:
        outer = Path(temporary)
        root = outer / 'workspace'
        root.mkdir()
        for package in (['common'] if mode == 'common' else ['common', 'project']):
            shutil.copytree(CANDIDATE / 'harness' / package, root / 'harness' / package,
                            ignore=shutil.ignore_patterns('inbox', '__pycache__'))
        for native in ['.agents/skills', '.claude/skills']:
            shutil.copytree(CANDIDATE / native, root / native)
        shutil.copytree(CANDIDATE / '.claude/rules', root / '.claude/rules',
                        ignore=shutil.ignore_patterns('README.human.md'))
        for name in ('AGENTS.md', 'CLAUDE.md'):
            if (CANDIDATE / name).is_file():
                shutil.copyfile(CANDIDATE / name, root / name)
        startup = subprocess.run(['python3', '-B', str(root / 'harness/common/checks/ensure_entrypoint_links.py'), str(root)],
                                 capture_output=True, text=True)
        if startup.returncode:
            return {'agent': agent, 'mode': mode, 'invocation': invocation, 'exit_code': startup.returncode,
                    'status': 'not-verified', 'reason': 'Fixture startup failed', 'stderr': startup.stderr}
        runtime = outer / 'runtime'
        runtime.mkdir()
        tool_environment = []
        if analysis_cli:
            tool_root = outer / 'plugin-eval'
            shutil.copytree(Path(analysis_cli).resolve().parent.parent, tool_root,
                            ignore=shutil.ignore_patterns('README.human.md', '__pycache__', '.git'))
            tool_bin = outer / 'bin'
            tool_bin.mkdir()
            (tool_bin / 'plugin-eval').symlink_to(tool_root / 'scripts/plugin-eval.js')
            tool_environment = ['--setenv', 'PATH', str(tool_bin) + ':' + os.environ['PATH']]
        source_home = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
        if agent == 'codex':
            auth = source_home / 'auth.json'
            if auth.is_file():
                shutil.copyfile(auth, runtime / 'auth.json')
            command = ['codex', 'exec', '--ignore-user-config', '--ephemeral', '--skip-git-repo-check',
                       '-s', sandbox, '-C', str(root), '-c', 'features.multi_agent=false', '--json', PROMPTS[invocation]]
            environment = ['--setenv', 'CODEX_HOME', str(runtime)]
        else:
            auth = Path.home() / '.claude/.credentials.json'
            if auth.is_file():
                shutil.copyfile(auth, runtime / '.credentials.json')
            command = ['claude', '-p', '--no-session-persistence', '--output-format', 'stream-json', '--verbose',
                       '--setting-sources', 'project', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
                       '--permission-mode', 'dontAsk', '--tools', 'Read,Glob,Grep,Bash,Skill',
                       '--allowedTools', 'Read,Glob,Grep,Bash,Skill', '--', PROMPTS[invocation]]
            environment = ['--setenv', 'CLAUDE_CONFIG_DIR', str(runtime)]
        isolation = ['bwrap', '--ro-bind', '/', '/', '--tmpfs', '/tmp', '--bind', str(outer), str(outer),
                     '--dev-bind', '/dev', '/dev', '--proc', '/proc', '--chdir', str(root), '--tmpfs', str(REPO)]
        hidden = [REPO]
        for folder in [Path.home() / '.agents', source_home / 'skills', source_home / 'plugins',
                       source_home / 'agents', source_home / 'rules', source_home / 'memories', Path.home() / '.claude']:
            if folder.is_dir():
                isolation += ['--tmpfs', str(folder)]
                hidden.append(folder)
        for file in [source_home / 'AGENTS.md', source_home / 'AGENTS.override.md']:
            if file.is_file():
                isolation += ['--ro-bind', '/dev/null', str(file)]
        check = subprocess.run(isolation + ['--', 'python3', '-c',
            'from pathlib import Path; import sys; assert not any(any(Path(p).iterdir()) for p in sys.argv[1:])'] +
            [str(p) for p in hidden], capture_output=True, text=True)
        if check.returncode:
            return {'agent': agent, 'mode': mode, 'invocation': invocation, 'status': 'not-verified',
                    'reason': 'OS isolation failed', 'stderr': check.stderr}
        started = time.monotonic()
        before = file_state(root) if capture_files else None
        process = subprocess.Popen(isolation + environment + tool_environment + ['--'] + command,
                                   stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True, start_new_session=True)
        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
            code = process.returncode
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
            code = 'timeout'
        events = []
        for line in stdout.splitlines():
            try:
                events.append(json.loads(line))
            except ValueError:
                pass
        response = '\n'.join(item.get('item', {}).get('text', '') for item in events
                             if item.get('item', {}).get('type') == 'agent_message') if agent == 'codex' else '\n'.join(
                                 str(item.get('result', '')) for item in events if item.get('type') == 'result')
        filename = f'{agent}-{mode}-{invocation}'
        raw = {'command': command, 'cwd': str(root), 'isolation_probe': 'passed',
               'masked_paths': [str(path) for path in hidden], 'exit_code': code,
               'elapsed_seconds': round(time.monotonic() - started, 2), 'stdout': stdout, 'stderr': stderr}
        if capture_files:
            after = file_state(root)
            raw['file_changes'] = {p: {'before': before.get(p), 'after': after.get(p)}
                                   for p in sorted(before.keys() | after.keys()) if before.get(p) != after.get(p)}
            raw['changed_text'] = {p: (root / p).read_text() for p in raw['file_changes']
                                   if p.endswith('.md') and Path(p).name != 'README.human.md' and (root / p).is_file()}
        (REQUEST / f'{filename}-events.json').write_text(json.dumps(raw, ensure_ascii=False, indent=2) + '\n')
        (REQUEST / f'{filename}-response.txt').write_text(response)
        # These are observations; success requires manual review of discovery, resource reads and behavior.
        return {'agent': agent, 'mode': mode, 'invocation': invocation, 'exit_code': code,
                'elapsed_seconds': raw['elapsed_seconds'], 'isolation_probe': 'passed',
                'completed': any(e.get('type') == 'turn.completed' for e in events) if agent == 'codex'
                    else any(e.get('type') == 'result' and not e.get('is_error', True) for e in events),
                'resource_name_in_events': 'references/validation-and-publication.md' in stdout,
                'response_file': f'{filename}-response.txt', 'events_file': f'{filename}-events.json'}


if __name__ == '__main__':
    import sys
    if '--self-test' in sys.argv:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assert file_state(root) == {}
            (root / 'note.md').write_text('before')
            before = file_state(root)
            (root / 'note.md').write_text('after')
            assert before['note.md'] != file_state(root)['note.md']
            (root / 'note.md').unlink()
            assert file_state(root) == {}
            source = root / 'captured-rules'
            source.mkdir()
            (source / 'README.human.md').write_text('fixture guide')
            (source / 'comm-example.md').write_text('actual rule')
            target = root / 'installed-rules'
            shutil.copytree(source, target, ignore=shutil.ignore_patterns('README.human.md'))
            assert {p.name for p in target.iterdir()} == {'comm-example.md'}
        print('File mutation observation self-check PASS')
        raise SystemExit(0)
    results = []
    # Probe the first mode before spending sessions on an agent that cannot authenticate.
    for mode in ['common', 'both']:
        agents = ['codex', 'claude'] if mode == 'common' else [agent for agent in ['codex', 'claude']
            if any(r['agent'] == agent and r.get('completed') for r in results)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            pending = [executor.submit(probe, agent, mode, invocation) for agent in agents for invocation in PROMPTS]
            for future in concurrent.futures.as_completed(pending):
                result = future.result()
                results.append(result)
                (REQUEST / 'native-summary.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
                print(json.dumps(result, ensure_ascii=False), flush=True)
