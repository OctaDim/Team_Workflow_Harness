import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4] if Path(__file__).resolve().parent.name == '2026-10-07-rules-skills-instruction-order' else Path('/home/octadim/MyProjects/GLOBAL_HARNESS_ENVIRONMENT')
EXPECTED = ['harness/common/START.md', 'harness/project/START.md', '.claude/rules/', 'harness/common/INDEX.md', 'harness/project/INDEX.md']
LINK = re.compile(r'\[[^\]\n]+\]\((harness/(?:common|project)/(?:START|INDEX)\.md|\.claude/rules/?)\)')


# Fixed test fixture from the user candidate; this is not an active entrypoint.
CORRECT_ENTRY = '# Harness\n\nВ начале каждой сессии до выполнения задачи запусти из корня проекта:\n\n```sh\npython3 harness/common/checks/ensure_entrypoint_links.py\n```\n\nПри ошибке проверки остановись и сообщи причину. \nПрочитай в следующем порядке (точный порядок очень важен):\n- [harness/common/START.md](harness/common/START.md)\n- [harness/project/START.md](harness/project/START.md)\n- [.claude/rules](.claude/rules/) До выполнения задачи прочитай все Markdown-правила из .claude/rules и его подпапок, кроме README.human.md; соблюдай применимые требования правил.\n- [harness/common/INDEX.md](harness/common/INDEX.md)\n- [harness/project/INDEX.md](harness/project/INDEX.md)\n\n. Подробности открывай по задаче; README.human.md не читай.\nИндивидуальные инструкции не отменяют применимые канонические требования.\nAGENTS.md принадлежит пользователю; разрешено только восстановление указанных ниже\nссылок:\n- [harness/common/START.md](harness/common/START.md)\n- [harness/project/START.md](harness/project/START.md)\n- [.claude/rules](.claude/rules/) До выполнения задачи прочитай все Markdown-правила из .claude/rules и его подпапок, кроме README.human.md; соблюдай применимые требования.\n- [harness/common/INDEX.md](harness/common/INDEX.md)\n- [harness/project/INDEX.md](harness/project/INDEX.md)\n\nДинамическую память сохраняй внутри harness.\n'

def check(repo):
    candidate = CORRECT_ENTRY.encode('utf-8')
    cases = []
    for mode in ('common', 'both'):
        for scenario in ('new-entry', 'existing-correct-entry', 'repair-missing-start', 'repair-missing-rules'):
            with tempfile.TemporaryDirectory(prefix='instruction-order-generator-') as temporary:
                root = Path(temporary)
                files = ['harness/common/INDEX.md', 'harness/common/START.md', 'harness/common/base/project-skeleton.json', 'harness/common/checks/ensure_entrypoint_links.py']
                if mode == 'both':
                    files += ['harness/project/INDEX.md', 'harness/project/START.md']
                for relative in files:
                    target = root / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(repo / relative, target)
                project_before = {relative: (root / relative).read_bytes() for relative in files if relative.startswith('harness/project/')}
                if scenario != 'new-entry':
                    text = candidate.decode('utf-8')
                    if scenario == 'repair-missing-start':
                        text = text.replace('- [harness/common/START.md](harness/common/START.md)\n', '')
                    if scenario == 'repair-missing-rules':
                        text = ''.join(line for line in text.splitlines(keepends=True)
                                       if '](.claude/rules/)' not in line)
                    (root / 'AGENTS.md').write_bytes(text.encode('utf-8'))
                    (root / 'CLAUDE.md').write_text('@AGENTS.md\n')
                commands = []
                for iteration in range(2):
                    completed = subprocess.run([sys.executable, '-B', str(root / 'harness/common/checks/ensure_entrypoint_links.py')], cwd=root, capture_output=True, text=True)
                    commands.append({'iteration': iteration + 1, 'exit_code': completed.returncode, 'stdout': completed.stdout, 'stderr': completed.stderr})
                    if completed.returncode:
                        raise RuntimeError(completed.stderr or completed.stdout)
                    current = (root / 'AGENTS.md').read_bytes()
                    if iteration == 0:
                        first = current
                output = current.decode('utf-8')
                links = LINK.findall(output)
                ordered = bool(links) and len(links) % len(EXPECTED) == 0 and links == EXPECTED * (len(links) // len(EXPECTED))
                cases.append({'mode': mode, 'scenario': scenario, 'link_order': links, 'required_link_order': ordered,
                              'legacy_bootstrap_phrase_present': 'Затем прочитай INDEX.md и START.md' in output,
                              'idempotent': first == current, 'project_preserved': all((root / relative).read_bytes() == body for relative, body in project_before.items()),
                              'existing_correct_entry_preserved': current == candidate if scenario == 'existing-correct-entry' else None,
                              'generated_entry_text': output, 'commands': commands})
    return {'date': '2026-10-07', 'generator': 'harness/common/checks/ensure_entrypoint_links.py',
            'generator_sha256': hashlib.sha256((repo / 'harness/common/checks/ensure_entrypoint_links.py').read_bytes()).hexdigest(),
            'scope': 'Local generator diagnosis only; not native Codex/Claude validation of the proposed rule.', 'cases': cases}


if __name__ == '__main__':
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/tmp/instruction-order-generator-results.json')
    report = check(REPO)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    for case in report['cases']:
        print(case['mode'], case['scenario'], 'ORDER=' + ('PASS' if case['required_link_order'] else 'FAIL'), 'idempotent=' + str(case['idempotent']), 'project_preserved=' + str(case['project_preserved']))
    sys.exit(0 if all(case['required_link_order'] for case in report['cases']) else 1)
