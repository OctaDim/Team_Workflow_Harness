"""Characterize the unchanged common checker and archived shim in temporary roots."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
COMMON = ROOT / 'harness/common'
CHECKER = COMMON / 'checks/ensure_entrypoint_links.py'
LEGACY = COMMON / 'inbox/2026-10-07-harness-direct-change-confirmation/candidate/harness/project/checks/ensure_entrypoint_links.py'
CASES = ('clean', 'crlf', 'missing-common', 'missing-start', 'symlink-common',
         'symlink-checks', 'symlink-checker', 'replaced-checker')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root):
    return {p.relative_to(root).as_posix(): digest(p) for p in root.rglob('*')
            if p.is_file() and not p.is_symlink()}


def probe(mode, case, entrypoint):
    with tempfile.TemporaryDirectory(prefix='entrypoint-equivalence-') as temporary:
        root = Path(temporary)
        common = root / 'harness/common'
        shutil.copytree(COMMON, common, ignore=shutil.ignore_patterns('inbox', 'evidence', '__pycache__'))
        if mode == 'common+project':
            project = root / 'harness/project'
            project.mkdir()
            for name in ('START.md', 'INDEX.md'):
                (project / name).write_text('# Existing project\n', encoding='utf-8')
            (project / 'sentinel').write_bytes(b'preserve existing project\n')
            if entrypoint == 'legacy':
                (project / 'checks').mkdir()
                shutil.copyfile(LEGACY, project / 'checks/ensure_entrypoint_links.py')
        if case == 'crlf':
            (root / 'AGENTS.md').write_bytes(b'# User settings\r\nKeep this setting.\r\n')
        marker = root / 'external-code-executed'
        payload = 'from pathlib import Path\nPath(' + repr(str(marker)) + ').touch()\n'
        if case == 'missing-common':
            shutil.rmtree(common)
        elif case == 'missing-start':
            (common / 'START.md').unlink()
        elif case.startswith('symlink-'):
            relative = {'symlink-common': 'harness/common', 'symlink-checks': 'harness/common/checks',
                        'symlink-checker': 'harness/common/checks/ensure_entrypoint_links.py'}[case]
            target = root / relative
            external = root / 'external'
            if case == 'symlink-checker':
                external.write_text(payload, encoding='utf-8')
                target.unlink()
            else:
                checker = external / ('checks/ensure_entrypoint_links.py' if case == 'symlink-common'
                                      else 'ensure_entrypoint_links.py')
                checker.parent.mkdir(parents=True)
                checker.write_text(payload, encoding='utf-8')
                target.rename(target.with_name(target.name + '-original'))
            target.symlink_to(external, target_is_directory=case != 'symlink-checker')
        elif case == 'replaced-checker':
            (common / 'checks/ensure_entrypoint_links.py').write_text(payload, encoding='utf-8')
        script = {'legacy': root / 'harness/project/checks/ensure_entrypoint_links.py',
                  'common': common / 'checks/ensure_entrypoint_links.py',
                  'trusted-common': CHECKER}[entrypoint]
        command = [sys.executable, '-I', '-B', str(script)]
        before = snapshot(root)
        result = subprocess.run(command, cwd=root, env=dict(os.environ, PATH='/no-git-in-this-test'),
                                capture_output=True, text=True, timeout=20)
        after = snapshot(root)
        record = dict(mode=mode, case=case, entrypoint=entrypoint, command=command,
                      exit=result.returncode, stdout=result.stdout, stderr=result.stderr,
                      marker_executed=marker.exists(),
                      changed=[p for p in sorted(before.keys() | after.keys()) if before.get(p) != after.get(p)],
                      agents_created=(root / 'AGENTS.md').exists(),
                      project_sentinel_preserved=(root / 'harness/project/sentinel').read_bytes() == b'preserve existing project\n'
                      if mode == 'common+project' else None)
        if case in ('clean', 'crlf'):
            assert result.returncode == 0, record
            inputs = {name: (root / name).read_bytes() for name in ('AGENTS.md', 'CLAUDE.md')}
            repeat = subprocess.run(command, cwd=root, env=dict(os.environ, PATH='/no-git-in-this-test'),
                                    capture_output=True, text=True, timeout=20)
            assert repeat.returncode == 0 and inputs == {name: (root / name).read_bytes() for name in inputs}
            assert 'будут автоматически восстановлены' not in repeat.stdout
            record['repeat_unchanged'] = True
            if case == 'crlf':
                assert inputs['AGENTS.md'].startswith(b'# User settings\r\nKeep this setting.\r\n')
                assert b'\n' not in inputs['AGENTS.md'].replace(b'\r\n', b'')
        if case in ('symlink-common', 'symlink-checks', 'symlink-checker'):
            if entrypoint == 'legacy':
                assert result.returncode == 2 and not marker.exists() and not record['agents_created'], record
            elif entrypoint == 'common':
                assert result.returncode == 0 and marker.exists() and not record['agents_created'], record
        if entrypoint == 'trusted-common' and case == 'symlink-common':
            assert result.returncode == 2 and not marker.exists(), record
        if case == 'replaced-checker' and entrypoint != 'trusted-common':
            assert marker.exists(), record
        if case in ('missing-common', 'missing-start'):
            assert result.returncode == 2 and not record['agents_created'], record
        assert record['project_sentinel_preserved'] is not False, record
        return record


def main():
    original = digest(CHECKER)
    records = [probe(mode, case, entrypoint)
               for mode in ('common-only', 'common+project') for case in CASES
               for entrypoint in ('legacy', 'common', 'trusted-common')
               if entrypoint != 'legacy' or mode == 'common+project']
    assert digest(CHECKER) == original
    print(json.dumps(dict(common_sha256=original, legacy_sha256=digest(LEGACY),
                          self_checks='passed', launch_guard_equivalent=False, runs=records),
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
