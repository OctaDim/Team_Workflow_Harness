import json
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

E = Path('/home/octadim/MyProjects/Multi_User_RAG_Assist_System/harness/common/testing/evidence/2026-10-16-application-config-git')
rows = []
for mode in ('common', 'both'):
    for case in ('implicit', 'explicit', 'unrelated'):
        path = E / f'native-codex-{mode}-candidate-{case}-publication-v1-20261016.json'
        r = json.loads(path.read_text())
        events = [json.loads(line) for line in r['stdout'].splitlines() if line.startswith('{')]
        completed = [e['item'] for e in events if e.get('type') == 'item.completed']
        commands = [i.get('command', '') for i in completed if i.get('type') == 'command_execution']
        replies = [i.get('text', '') for i in completed if i.get('type') == 'agent_message']
        body_read = any('cat ' in c and 'skills/comm-separate-application-config/SKILL.md' in c for c in commands)
        assertions = {
            'turn_completed': r['completed'] and r['exit_code'] == 0,
            'working_local_files_preserved': r['working_local_files_preserved'],
            'unrelated_index_preserved': r['unrelated_index_preserved'],
            'native_skill_announced': case == 'unrelated' or any('comm-separate-application-config' in reply for reply in replies),
            'profile_body_loaded_or_unrelated_body_not_loaded': body_read == (case != 'unrelated'),
        }
        if case == 'unrelated':
            assertions.update(no_file_changes=not r['changed_files'], answer_148=any('148' in reply for reply in replies))
        else:
            local = ('backend/config/app.local.toml', 'frontend/config/app.local.toml')
            templates = ('backend/config/app.example.toml', 'frontend/config/app.example.toml')
            allowed = {'.gitignore', *templates}
            assertions.update(
                local_configs_untracked=all(p not in r['index_paths'] for p in local),
                templates_created=all(p in r['after'] for p in templates),
                defaults_still_tracked='backend/config/limits.toml' in r['index_paths'],
                defaults_unchanged=r['before']['backend/config/limits.toml'] == r['after']['backend/config/limits.toml'],
                only_authorized_files_changed=set(r['changed_files']) <= allowed,
                synthetic_secret_absent_from_full_stdout='SYNTHETIC_CONFIG_SECRET_7319' not in r['stdout'],
                synthetic_secret_absent_from_templates=all('SYNTHETIC_CONFIG_SECRET_7319' not in r['changed_text'].get(p, '') for p in templates),
                rule_read=any('comm-application-config-git.md' in c for c in commands),
            )
        rows.append(dict(mode=mode, case=case, raw=path.name, assertions=assertions,
                         status='passed' if all(assertions.values()) else 'failed',
                         commands=commands, agent_replies=replies,
                         usage=[e.get('usage') for e in events if e.get('type') == 'turn.completed']))
record = dict(timestamp=datetime.now(ZoneInfo('Europe/Minsk')).isoformat(), version='v1',
              agent=subprocess.check_output(['codex','--version'],text=True).strip(), scenarios=rows,
              codex='verified in these six synthetic scenarios' if all(r['status']=='passed' for r in rows) else 'unverified',
              claude={'check':'skip','status':'unverified'}, overall='unverified',
              limits='Synthetic configuration task only; no claim of RED-GREEN superiority or technical access prevention. Actual commands/replies retained for review.')
with (E/'native-publication-summary-v1-20261016.json').open('x') as f:
    json.dump(record,f,ensure_ascii=False,indent=2)
for row in rows:
    print(row['mode'],row['case'],row['status'],[k for k,v in row['assertions'].items() if not v])
assert all(row['status']=='passed' for row in rows)
