"""Check native execution evidence; behavioral answers still require manual review."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILLS = {'inbox': ('comm-process-harness-inbox', 'workflow.md'),
          'install': ('comm-install-harness', 'checks.md'),
          'authoring': ('comm-create-lazy-claude-codex-skills', 'content-contract.md')}


def review():
    observations = []
    for mode in ['common', 'both']:
        for task in ['unrelated', *SKILLS]:
            for invocation in (['implicit'] if task == 'unrelated' else ['implicit', 'explicit']):
                name = f'codex-{mode}-green-{task}-{invocation}'
                raw = json.loads((HERE / f'{name}-events.json').read_text())
                events = []
                for line in raw['stdout'].splitlines():
                    try:
                        events.append(json.loads(line))
                    except ValueError:
                        pass
                items = [e.get('item', {}) for e in events if e.get('type') == 'item.completed']
                commands = [i.get('command', '') for i in items if i.get('type') == 'command_execution']
                assert raw['exit_code'] == 0, name
                assert any(e.get('type') == 'turn.completed' for e in events), name
                assert raw['isolation_probe'] == 'passed', name
                assert raw.get('file_changes') == {}, (name, raw.get('file_changes'))
                assert commands and 'ensure_entrypoint_links.py' in commands[0], name
                command_text = '\n'.join(commands)
                if task == 'unrelated':
                    assert '/SKILL.md' not in command_text and '/references/' not in command_text, name
                else:
                    skill, resource = SKILLS[task]
                    assert f'{skill}/SKILL.md' in command_text, name
                    assert f'{skill}/references/{resource}' in command_text, name
                messages = [i.get('text', '') for i in items if i.get('type') == 'agent_message']
                assert messages and all(skill in messages[0] for skill, _ in SKILLS.values()), name
                observations.append({'mode': mode, 'task': task, 'invocation': invocation,
                                     'execution_checks': 'passed', 'commands': commands,
                                     'events_file': f'{name}-events.json',
                                     'response_file': f'{name}-response.txt'})
    return observations


if __name__ == '__main__':
    result = review()
    (HERE / 'native-execution-review.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(f'{len(result)}/14 native execution checks passed; manual behavior review required.')
