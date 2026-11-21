"""Run the installed analyzer through the launcher; never print human bodies."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import pytest


LAUNCHER = Path(__file__).resolve().parents[2] / 'scripts/plugin_eval_without_human.mjs'


class TestHumanFilter:

    def test_installed_analyzer_and_read_guards(self):
        executable = shutil.which('plugin-eval')
        assert executable is not None, 'Install plugin-eval before this integration check'
        cli = Path(executable).resolve()
        plugin_files = [cli, *cli.parent.parent.joinpath('src').rglob('*.js')]
        digest = lambda files: {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        plugin_before = digest(plugin_files)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for kind in ('skill', 'rule', 'plugin'):
                target = root / kind
                target.mkdir()
                (target / 'details.md').write_text('Machine guidance.\n')
                if kind == 'skill':
                    (target / 'SKILL.md').write_text('---\nname: skill\ndescription: Use when testing a skill.\n---\nRead details.md.\n')
                elif kind == 'rule':
                    (target / 'comm-example.md').write_text('When testing, preserve the input.\n')
                else:
                    manifest = target / '.codex-plugin'
                    manifest.mkdir()
                    (manifest / 'plugin.json').write_text(json.dumps({'name': 'example', 'version': '1.0.0', 'description': 'Example plugin'}))
                nested = target / 'nested'
                nested.mkdir()
                for folder in (target, nested):
                    (folder / 'README.human.md').write_text('HUMAN_CANARY_DO_NOT_READ\n' * 400)
                before = digest((p for p in target.rglob('*') if p.is_file()))
                result = subprocess.run(['node', str(LAUNCHER), str(cli), 'analyze', str(target), '--format', 'json'], capture_output=True, text=True)
                assert result.returncode == 0, result.stderr
                report = json.loads(result.stdout)
                assert report['target']['kind'] == ('directory' if kind == 'rule' else kind)
                components = report['budgets']['deferred_cost_tokens']['components']
                assert any((c['path'].endswith('details.md') for c in components))
                assert not any((c['path'].endswith('README.human.md') for c in components))
                assert 'HUMAN_CANARY' not in result.stdout
                assert before == digest((p for p in target.rglob('*') if p.is_file()))
            human = root / 'skill' / 'README.human.md'
            alias = root / 'alias.md'
            alias.symlink_to(human)
            probe = root / 'probe.mjs'
            for source in (human, alias):
                probe.write_text("import fs from 'node:fs/promises';\nconsole.log(await fs.readFile(" + json.dumps(str(source)) + ", 'utf8'));\n")
                result = subprocess.run(['node', str(LAUNCHER), str(probe)], capture_output=True, text=True)
                assert result.returncode != 0
                assert ('README.human.md' if source == human else 'Symlink forbidden') in result.stderr
                if source == alias:
                    assert str(alias) in result.stderr
                assert 'HUMAN_CANARY' not in result.stdout + result.stderr
            protected = root / 'protected.txt'
            protected.write_text('unchanged')
            probe.write_text("import fs from 'node:fs/promises';\nawait fs.writeFile(" + json.dumps(str(protected)) + ", 'changed');\n")
            result = subprocess.run(['node', str(LAUNCHER), str(probe)], capture_output=True, text=True)
            assert result.returncode != 0
            assert protected.read_text() == 'unchanged'
        assert plugin_before == digest(plugin_files)
