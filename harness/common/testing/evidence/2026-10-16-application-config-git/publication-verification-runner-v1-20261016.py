import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path('/home/octadim/MyProjects/Multi_User_RAG_Assist_System')
E = ROOT / 'harness/common/testing/evidence/2026-10-16-application-config-git'
C = ROOT / 'harness/common/inbox/2026-10-16-application-config-git/candidate'
spec = importlib.util.spec_from_file_location('config_native', E / 'native-validation-v3.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)
native.ordinary(ROOT / 'harness')
out = E / 'prepublication-v1-20261016.json'
assert not out.exists()
records = []

def run(command, cwd=ROOT, expected=0):
    r = subprocess.run(command, cwd=cwd, text=True, capture_output=True,
                       env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    records.append(dict(command=[str(x) for x in command], cwd=str(cwd),
                        exit_code=r.returncode, stdout=r.stdout, stderr=r.stderr))
    assert r.returncode == expected, (command, r.returncode, r.stderr)
    return r

def save():
    with out.open('x') as f:
        json.dump(dict(timestamp=datetime.now(ZoneInfo('Europe/Minsk')).isoformat(),
                       records=records), f, ensure_ascii=False, indent=2)

try:
    expected = {'rules/comm-application-config-git.md': 'f83eb86bea352f1cdc487d1c28c9075af132b8b8adad8a8ec0de1aaefac40333',
                'skills/comm-separate-application-config/SKILL.md': 'e9c43d44cb7a3714f7a18e71587af732ef72cf009d1e04957261506335732af0'}
    for p, h in expected.items():
        assert hashlib.sha256((C/p).read_bytes()).hexdigest() == h
    records.append(dict(check='approved v1 hashes unchanged', status='passed', hashes=expected))
    run([str(ROOT/'backend/.venv/bin/python'), '/home/octadim/.codex/skills/.system/skill-creator/scripts/quick_validate.py', str(C/'skills'/native.NAME)])
    entry = '/home/octadim/.codex/plugins/cache/openai-curated-remote/plugin-eval/0.1.2/scripts/plugin-eval.js'
    for target in (C/'skills'/native.NAME, C/'rules'):
        for action in ('start', 'analyze'):
            r = run(['node', 'harness/common/scripts/plugin_eval_without_human.mjs', entry, action, str(target), '--format', 'json'])
            json.loads(r.stdout)
    for mode in ('common', 'both'):
        with tempfile.TemporaryDirectory(prefix='config-publication-install-') as d:
            root = Path(d)
            startup = native.prepare(root, mode, False)
            for folder in ('.agents/skills', '.claude/skills'):
                assert native.state(root/'harness/common/skills') == native.state(root/folder)
            for p in (root/'harness/common/rules').glob('*.md'):
                if p.name != 'README.human.md':
                    assert p.read_bytes() == (root/'.claude/rules'/p.name).read_bytes()
            records.append(dict(check='two starts, project preserved, full native equality', mode=mode, status='passed', startup=startup))
            damaged = root/'.claude/rules'/native.RULE
            damaged.write_text('deliberately different ordinary rule copy\n')
            before = native.state(root)
            r = subprocess.run(['python3', '-B', 'harness/common/checks/ensure_entrypoint_links.py'], cwd=root, capture_output=True, text=True)
            assert r.returncode != 0 and 'Different rule bytes' in r.stdout+r.stderr
            assert native.state(root) == before
            records.append(dict(check='damaged copy rejected without writes', mode=mode, status='passed', stdout=r.stdout, stderr=r.stderr))
    with tempfile.TemporaryDirectory(prefix='config-publication-project-only-') as d:
        root = Path(d)
        for folder in ('harness/project/rules', '.claude/rules'):
            (root/folder).mkdir(parents=True)
            (root/folder/'proj-example.md').write_text('ordinary\n')
        before = native.state(root)
        cspec = importlib.util.spec_from_file_location('entrypoint_checks', ROOT/'harness/common/checks/ensure_entrypoint_links.py')
        checker = importlib.util.module_from_spec(cspec)
        cspec.loader.exec_module(checker)
        try:
            checker.check_rule_copies(root)
            raise AssertionError('project-only accepted')
        except ValueError as e:
            assert 'common' in str(e)
        assert native.state(root) == before
        records.append(dict(check='project-only rejected without writes', status='passed'))
    with tempfile.TemporaryDirectory(prefix='config-publication-git-') as d:
        root = Path(d)
        native.prepare(root, 'common', False)
        unrelated = native.git(root, 'ls-files', '--stage', '--', 'unrelated.txt').stdout
        paths = ('backend/config/app.local.toml', 'frontend/config/app.local.toml')
        before = {p: (root/p).read_bytes() for p in paths}
        assert native.git(root, 'ls-files', '--error-unmatch', '--', paths[0]).returncode == 0
        native.git(root, 'check-ignore', '-v', '--no-index', '--', paths[0])
        records.append(dict(check='ignored backend local file remains tracked', status='passed'))
        with (root/'.gitignore').open('a') as f:
            f.write('/frontend/config/app.local.toml\n')
        for section in ('backend', 'frontend'):
            (root/section/'config/app.example.toml').write_text('[app]\nvalue = "REPLACE_ME"\n')
        native.git(root, 'rm', '--cached', '--', *paths)
        native.git(root, 'add', '--', '.gitignore', 'backend/config/app.example.toml', 'frontend/config/app.example.toml')
        for p in paths:
            native.git(root, 'check-ignore', '-v', '--no-index', '--', p)
            r = subprocess.run(['git','-C',str(root),'ls-files','--error-unmatch','--',p],capture_output=True)
            assert r.returncode == 1 and (root/p).read_bytes() == before[p]
        for p in ('backend/config/app.example.toml', 'frontend/config/app.example.toml', 'backend/config/limits.toml'):
            r = subprocess.run(['git','-C',str(root),'check-ignore','-v','--no-index','--',p],capture_output=True)
            assert r.returncode == 1
            native.git(root, 'ls-files', '--error-unmatch', '--', p)
        assert unrelated == native.git(root, 'ls-files', '--stage', '--', 'unrelated.txt').stdout
        records.append(dict(check='local files ignored/untracked/preserved, templates/defaults visible, unrelated index preserved', status='passed'))
    run([str(ROOT/'backend/.venv/bin/python'), '-m', 'pytest', '-c', 'harness/common/testing/pytest.ini',
         'harness/common/testing/tests/test_rule_copies.py::TestRuleCopies::test_installed_rule_copies',
         'harness/common/testing/tests/test_human_guide_reader.py', 'harness/common/testing/tests/test_skills_first_knowledge.py',
         '-q', '-p', 'no:cacheprovider'])
    run(['git', 'diff', '--check'])
    records.append(dict(check='prepublication checks completed', status='passed'))
finally:
    save()
print(json.dumps({'record': str(out), 'checks': len(records), 'status': 'passed'}))
