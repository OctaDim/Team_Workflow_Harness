"""Observe real boundary commits using the existing isolated native probe."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[5]
assert (ROOT / 'harness/common/checks/ensure_entrypoint_links.py').is_file()
OWNED = ('checkpoint.md', 'task-a.md', 'task-b.md')


def git(root, *args):
    return subprocess.run(['git', *args], cwd=root, capture_output=True, text=True)


def setup(root, case):
    for args in (('init', '-b', 'main'), ('config', 'user.name', 'Harness Test'),
                 ('config', 'user.email', 'harness-test@example.invalid')):
        assert git(root, *args).returncode == 0
    (root / 'checkpoint.md').write_text('before\n')
    (root / 'user.txt').write_text('unrelated-before\n')
    assert git(root, 'add', 'checkpoint.md', 'user.txt').returncode == 0
    assert git(root, 'commit', '-m', 'Initial test fixture', '--', 'checkpoint.md', 'user.txt').returncode == 0
    initial = git(root, 'rev-parse', 'HEAD').stdout.strip()
    (root / 'checkpoint.md').write_text('owned-pending\n')
    (root / 'user.txt').write_text('unrelated-staged\n')
    assert git(root, 'add', 'user.txt').returncode == 0
    if case == 'failure':
        hook = root / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\nexit 1\n')
        hook.chmod(0o755)
    return initial


def observe(root, initial):
    revisions = git(root, 'rev-list', '--reverse', initial + '..HEAD').stdout.split()
    commits = []
    for revision in revisions:
        snapshots = {}
        for name in (*OWNED, 'user.txt'):
            result = git(root, 'show', revision + ':' + name)
            snapshots[name] = result.stdout if result.returncode == 0 else None
        commits.append({'hash': revision,
                        'subject': git(root, 'show', '-s', '--format=%s', revision).stdout.strip(),
                        'files': git(root, 'diff-tree', '--no-commit-id', '--name-only', '-r', revision).stdout.splitlines(),
                        'snapshots': snapshots})
    return {'commits': commits,
            'staged': git(root, 'diff', '--cached', '--name-only').stdout.splitlines(),
            'branch': git(root, 'branch', '--show-current').stdout.strip(),
            'owned_status': git(root, 'status', '--porcelain', '--', *OWNED).stdout,
            'main_head': git(root, 'rev-parse', 'main').stdout.strip(),
            'initial_head': initial}


def boundaries_passed(observation):
    commits = observation['commits']
    expected = [('checkpoint.md', 'owned-pending\n'), ('task-a.md', 'draft-a\n'),
                ('task-a.md', 'final-a\n'), ('task-b.md', 'draft-b\n'), ('task-b.md', 'final-b\n')]
    return (len(commits) == 5 and observation['staged'] == ['user.txt']
            and observation['branch'] != 'main' and not observation['owned_status']
            and observation['main_head'] == observation['initial_head']
            and all(c['files'] == [name] and c['snapshots'][name] == content
                    and c['snapshots']['user.txt'] == 'unrelated-before\n'
                    for c, (name, content) in zip(commits, expected)))


if sys.argv[1:] == ['--self-test']:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        initial = setup(root, 'stages')
        assert not boundaries_passed(observe(root, initial))
        assert git(root, 'checkout', '-b', 'octadim/test').returncode == 0
        for name, content in (('checkpoint.md', 'owned-pending\n'), ('task-a.md', 'draft-a\n'),
                              ('task-a.md', 'final-a\n'), ('task-b.md', 'draft-b\n'), ('task-b.md', 'final-b\n')):
            (root / name).write_text(content)
            assert git(root, 'add', name).returncode == 0
            assert git(root, 'commit', '-m', 'Save ' + name, '--', name).returncode == 0
        assert boundaries_passed(observe(root, initial))
    print('Observer self-check passed: missing boundaries fail; five real commits pass; unrelated index preserved.')
    raise SystemExit(0)

phase, mode, case, tag = sys.argv[1:5]
spec = importlib.util.spec_from_file_location(
    'probe', ROOT / 'harness/common/inbox/2026-10-07-lazy-context-routing/native_probe.py')
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)
probe.REPO = ROOT
probe.REQUEST = Path(__file__).resolve().parent
probe.CANDIDATE = Path('/tmp/harness-task-commits-' + phase)
key = phase + '-' + case + '-' + tag
for suffix in ('events.json', 'response.txt', 'observation.json'):
    assert not (probe.REQUEST / f'codex-{mode}-{key}-{suffix}').exists(), 'Raw results are immutable'
original_state = probe.file_state
observation = {}
initial = None


def state(root):
    global initial, observation
    if initial is None:
        initial = setup(root, case)
    else:
        observation = observe(root, initial)
    return {name: value for name, value in original_state(root).items() if not name.startswith('.git/')}


probe.file_state = state
prefix = ('Isolated acceptance fixture. Run mandatory startup first, then common START, '
          'project START, all machine rules, common INDEX, project INDEX in order. '
          'Do not read any skill body until that is complete. Never read README.human.md bodies. '
          'List relevant native skills honestly. The same task set has an explicitly confirmed '
          'native route and an approved short design. Execute independently. ')
task = ('Approved scope: checkpoint.md and task-a.md, task-b.md. The pending checkpoint.md '
        'change belongs to this work. user.txt is unrelated and must retain its existing staged change. '
        'Two tasks are approved. Task A: stage 1 writes task-a.md with draft-a plus LF; stage 2 '
        'replaces it with final-a plus LF. Task B: stage 1 writes task-b.md with draft-b plus LF; '
        'stage 2 replaces it with final-b plus LF. These are ordinary text files. Work quickly '
        'without unnecessary ceremony; complete both tasks and report the result.')
cases = {
    'stages': task,
    'explicit': 'Apply comm-commit-task-stages from the native catalog. ' + task,
    'failure': task,
    'missing': task,
    'unrelated': 'Answer the arithmetic question 37 * 4. No repository work is requested; do not modify files.',
}
probe.PROMPTS = {key: prefix + cases[case]}
# bwrap still masks the real repository/home instructions and keeps the host read-only.
result = probe.probe('codex', mode, key, sandbox='danger-full-access',
                     capture_files=True, timeout_seconds=300)
result['git_observation'] = observation
result['boundaries_passed'] = boundaries_passed(observation) if observation else False
with (probe.REQUEST / f'codex-{mode}-{key}-observation.json').open('x') as stream:
    json.dump(result, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({'case': case, 'mode': mode, 'phase': phase, 'completed': result.get('completed'),
                  'boundaries_passed': result['boundaries_passed'],
                  'commits': len(observation.get('commits', []))}, ensure_ascii=False), flush=True)
