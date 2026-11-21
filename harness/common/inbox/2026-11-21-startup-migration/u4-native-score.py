"""Summarize observable evidence in the completed Codex JSONL trace without copying file bodies."""
import argparse
import json
import re
from pathlib import Path



def rollout_outputs(value):
    """Decode the text actually received, including code-mode's serialized shell result."""
    if isinstance(value, list):
        return '\n'.join(rollout_outputs(node) for node in value)
    if isinstance(value, dict):
        if 'output' in value:
            return rollout_outputs(value['output'])
        if value.get('type') in ('input_text','output_text','text'):
            return rollout_outputs(value.get('text',''))
        if 'value' in value:
            return rollout_outputs(value['value'])
        return ''
    if isinstance(value,str) and value.lstrip().startswith(('{','[')):
        try:
            return rollout_outputs(json.loads(value))
        except ValueError:
            pass
    return value if isinstance(value,str) else ''


def inspect_rollout(work, directory, task, rules, skills, maps):
    paths = list((directory / 'client/.codex/sessions').glob('**/rollout-*.jsonl'))
    if len(paths) != 1:
        return None
    events = [json.loads(line) for line in paths[0].read_text().splitlines()]
    bodies = {**rules, **skills, **maps}
    reads = {k:[] for k in bodies}
    calls = {}
    usage, startup_checks, listings, grouped = [], [], [], []
    standalone_listings = []
    initial_rules = set()
    boundary = write = final_at = None
    last_answer = ''
    stale = False
    for i,event in enumerate(events):
        p = event['payload']
        k = p.get('type')
        if event['type'] == 'token_usage_record':
            usage.append((i,p.get('turn_token_usage')))
        if event['type'] != 'response_item':
            continue
        if k == 'message' and p.get('role') in ('developer','user','system') and not calls:
            text = rollout_outputs(p.get('content',[]))
            initial_rules.update(path for path,body in rules.items() if body in text)
        if k == 'message' and p.get('role')=='assistant' and p.get('phase')=='final_answer':
            final_at = i
            last_answer = rollout_outputs(p.get('content',[]))
        if k in ('custom_tool_call','function_call'):
            cmd = str(p.get('input',p.get('arguments','')))
            calls[p['call_id']] = (i,cmd)
            if task == 'history' and boundary is None and re.search(r'cache_ttl|cache[-_]settings|harness/project/specs(?:/|\W)',cmd):
                boundary = i
            if task in ('explain', 'change') and boundary is None and re.search(r'app\.toml|git status|git ls-files',cmd):
                boundary = i
            if task == 'change':
                if write is None and 'app.toml' in cmd and re.search(r'apply_patch|sed -i|write_text|write_bytes|>\s*app\.toml|tee\s+app\.toml',cmd):
                    write = i
        if k not in ('custom_tool_call_output','function_call_output'):
            continue
        ci,cmd = calls.get(p['call_id'],(-1,''))
        body = rollout_outputs(p.get('output',''))
        fully = [key for key,text in bodies.items() if text in body]
        for key in fully:
            reads[key].append(i)
        batch = [key for key in fully if key in rules]
        if len(batch) > 1:
            grouped.append(len(batch))
        if re.search(r'python3\s+(?:-B\s+)?harness/common/checks/ensure_entrypoint_links\.py',cmd) and 'Entrypoint check completed' in body and 'Entrypoint check completed. Изменены:' not in body:
            startup_checks.append(i)
        if '.claude/rules' in cmd and all(k.split('/')[-1] in body for k in rules) and not batch and 'rg --files' in cmd and '--hidden' in cmd and '--no-ignore' in cmd:
            listings.append(i)
            # Conservative evidence of a stand-alone command, without a second shell operation.
            if not any(x in cmd for x in (' && ', '; ', '\\n', '|', 'namei', 'ls -', 'python3', 'cat ')) and '*.md' in cmd:
                standalone_listings.append(i)
        if task == 'history' and ('cache_ttl = 15' in body or 'old-cache-settings.md' in body):
            stale = True
    if task == 'answer':
        boundary = final_at
    def confirmed_before(keys,limit):
        return [k for k in keys if limit is not None and (k in initial_rules or any(i < limit for i in reads[k]))]
    counters = None
    if boundary is not None:
        record = next(((i,v) for i,v in usage if i > boundary),None)
        if record and not any(boundary < c < record[0] for c,_ in calls.values()):
            counters = record[1]
    return {'expected':len(rules),'rule_texts_before':len(confirmed_before(rules,boundary)),
            'rule_texts_anytime':sum(k in initial_rules or bool(reads[k]) for k in rules),'multi_rule_returns':grouped,
            'repeated_complete_rules':[k for k in rules if len(reads[k])>1],
            'missing_rules_before_task':sorted(set(rules) - set(confirmed_before(rules,boundary))) if boundary is not None else None,
            'complete_listing_events':listings,'standalone_listing_events':standalone_listings,
            'complete_rules_in_recorded_initial_messages':sorted(initial_rules),
            'checker_success_events':startup_checks,
            'confirmed_skill_bodies_before':confirmed_before(skills,boundary),
            'confirmed_skill_bodies_anytime':[k for k in skills if reads[k]],
            'maps_before':confirmed_before(maps,boundary),'maps_anytime':[k for k in maps if reads[k]],
            'first_dependent_rollout_index':boundary,'first_config_write_rollout_index':write,
            'config_skill_full_before_write':('comm-separate-application-config' in confirmed_before(skills,write)) if write is not None else None,
            'counter_at_first_dependent_request':counters,
            'counter_at_last_request':usage[-1][1] if usage else None,'final_observed':final_at is not None,
            'stale_material_read':stale}


def score(trace_directory, task):
    work = trace_directory / 'workspace'
    rules = {p.relative_to(work).as_posix(): p.read_text().rstrip('\n')
             for p in sorted((work / '.claude/rules').rglob('*.md')) if p.name != 'README.human.md'}
    skills = {p.parent.name: p.read_text().rstrip('\n') for p in (work / '.agents/skills').glob('*/SKILL.md')}
    maps = {f'harness/{pkg}/INDEX.md': (work / f'harness/{pkg}/INDEX.md').read_text().rstrip('\n')
            for pkg in ('common','project')}
    confirmed = {key: [] for key in [*rules, *skills, *maps]}
    commands = []
    answers = []
    first_dependent = None
    stale = False
    for i,line in enumerate((trace_directory / 'native-output.jsonl').read_text().splitlines()):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        item = e.get('item', {})
        if e.get('type') != 'item.completed':
            continue
        kind = item.get('type')
        if kind == 'agent_message':
            answers.append((i, item.get('text','')))
        if kind == 'file_change' and task == 'change' and first_dependent is None:
            if any('app.toml' in str(row.get('path','')) for row in item.get('changes', [])):
                first_dependent = i
        if kind != 'command_execution':
            continue
        command = item.get('command', '')
        body = item.get('aggregated_output','')
        commands.append({'event':i,'exit':item.get('exit_code')})
        if item.get('exit_code') != 0:
            continue
        for group in (rules, skills, maps):
            for key, text in group.items():
                if text in body:
                    confirmed[key].append(i)
        if task == 'history' and ('cache_ttl' in command or 'cache-settings' in command):
            if first_dependent is None:
                first_dependent = i
            if 'cache_ttl = 15' in body or 'old-cache-settings.md' in body:
                stale = True
        if task == 'explain' and 'app.toml' in command and first_dependent is None:
            first_dependent = i
        if task == 'change' and 'app.toml' in command and first_dependent is None:
            if re.search(r'\bsed\s+-i|(?:^|[^<])>\s*app\.toml|write_text|write_bytes|apply_patch|\btee\s+app\.toml',command):
                first_dependent = i
    if task == 'answer' and answers:
        first_dependent = answers[-1][0]
    final = answers[-1][1] if answers else ''
    expected = {'answer':'180','history':'45','explain':'20','change':'25'}[task]
    correct = bool(re.search(r'(?<!\d)'+expected+r'(?!\d)',final))
    if task == 'history':
        correct = correct and 'cache-settings.md' in final and not stale
    if task == 'change':
        correct = (work/'app.toml').read_text() == 'timeout = 25\n'
    before = lambda x: any(first_dependent is not None and j < first_dependent for j in confirmed[x])
    return {'rollout':inspect_rollout(work,trace_directory,task,rules,skills,maps), 'dependent_event_observed':first_dependent is not None, 'task_answer_or_edit_matches':correct,
            'commands_completed':len(commands), 'full_rule_bodies_before_task':sum(before(x) for x in rules),
            'full_rule_bodies_anytime':sum(bool(confirmed[x]) for x in rules), 'expected_rule_count':len(rules),
            'missing_full_rule_bodies': [x for x in rules if not confirmed[x]],
            'duplicate_full_bodies':{k:len(v) for k,v in confirmed.items() if len(v)>1},
            'skill_bodies_before_task':[x for x in skills if before(x)],
            'skill_bodies_anytime':[x for x in skills if confirmed[x]],
            'map_bodies_before_task':[x for x in maps if before(x)],
            'material_from_stale_trace_observed':stale}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace_directory',type=Path)
    parser.add_argument('task',choices=('answer','history','explain','change'))
    args=parser.parse_args()
    print(json.dumps(score(args.trace_directory,args.task),ensure_ascii=False))
