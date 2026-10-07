"""Reject incomplete/unsafe native traces; do not call the external agent in pytest."""
import runpy
from pathlib import Path

import pytest


def test_rule_reader_rejects_globs_missing_files_and_combined_calls():
    script = Path(__file__).with_name('check_human_guide_search.py')
    if not script.is_file():
        root = next(p for p in Path(__file__).resolve().parents
                    if (p / 'harness/common/checks/ensure_entrypoint_links.py').is_file())
        script = root / 'harness/common/checks/check_human_guide_search.py'
    try:
        assess = runpy.run_path(str(script))['assess_rule_reading']
    except (SystemExit, KeyError):
        pytest.fail('The check cannot assess a completed bulk-rule-reading trace')
    paths = ['.claude/rules/comm-a.md', '.claude/rules/nested/personal space.md']
    bodies = dict(zip(paths, ['# First rule\n', '# Nested rule\n']))
    listing = {'command': "rg --files --hidden --no-ignore .claude/rules -g '*.md' -g '!README.human.md'",
               'aggregated_output': '\n'.join(paths) + '\n', 'exit_code': 0}
    reading = {'command': "cat '.claude/rules/comm-a.md' '.claude/rules/nested/personal space.md'",
               'aggregated_output': '# First rule\n# Nested rule\n', 'exit_code': 0}
    skill = {'command': 'cat .agents/skills/example/SKILL.md',
             'aggregated_output': 'Skill body', 'exit_code': 0}
    assert assess([listing, reading, skill], bodies)['rule_reading_pass']
    startup_listing = dict(listing, command='cat harness/common/START.md; ' + listing['command'],
                           aggregated_output='# Startup boundary\n' + listing['aggregated_output'])
    assert assess([startup_listing, reading, skill], bodies)['rule_reading_pass']
    preliminary = [dict(listing, command=listing['command'].replace('--no-ignore ', '')),
                   dict(reading, command='cat .claude/rules/comm-a.md', aggregated_output='# First rule\n')]
    assert assess(preliminary + [listing, reading, skill], bodies)['rule_reading_pass']
    assert not assess([reading, skill], bodies)['rule_reading_pass']
    assert not assess([dict(listing, command=listing['command'].replace('--no-ignore ', '')), reading, skill], bodies)['rule_reading_pass']
    assert not assess([dict(listing, aggregated_output=paths[0]), reading, skill], bodies)['rule_reading_pass']
    assert not assess([listing, dict(reading, aggregated_output='# First rule\n'), skill], bodies)['rule_reading_pass']
    assert not assess([listing, dict(reading, command='cat .claude/rules/*.md'), skill], bodies)['rule_reading_pass']
    combined = dict(listing, command=listing['command'] + ' && ' + reading['command'],
                    aggregated_output=listing['aggregated_output'] + reading['aggregated_output'])
    assert not assess([combined, listing, reading, skill], bodies)['rule_reading_pass']
    assert not assess([listing, skill, reading], bodies)['rule_reading_pass']
    assert not assess([listing, dict(reading, exit_code=1), skill], bodies)['rule_reading_pass']
    assert not assess([], {})['rule_reading_pass']
