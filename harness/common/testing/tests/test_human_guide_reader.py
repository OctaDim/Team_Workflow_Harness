"""Check the observer contract using known fixture content and real offline CLI invocations."""
import copy
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

import pytest


CHECK = Path(__file__).absolute().parents[2] / 'checks/check_human_guide_search.py'
AUDIT = runpy.run_path(str(CHECK))['audit']
COMMON_MAP = 'harness/common/INDEX.md'
PROJECT_MAP = 'harness/project/INDEX.md'
ENTRY_RULE = '.claude/rules/sub/config.md'
SKILL = 'harness/common/skills/config/SKILL.md'
ALIAS = '.agents/skills/config/SKILL.md'
BODY = '---\nname: config\ndescription: Use before edits.\n---\n# Конфигурация\nСохрани значение.\n'
OWNER = f'Before changing configuration open /{SKILL}.\n'
ENTRY = 'AGENTS.md'
ALWAYS = '.claude/rules/start.md'


def put(root, path, text):
    file = root / path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_bytes(text.encode())


@pytest.fixture
def root(tmp_path):
    for p, value in {
        ENTRY: 'Read all mandatory rules.\n', 'CLAUDE.md': '',
        COMMON_MAP: 'Common\n', PROJECT_MAP: 'Project\n', ENTRY_RULE: OWNER, ALWAYS: 'Proceed.\n',
        'harness/project/rules/sub/config.md': OWNER, 'harness/common/rules/start.md': 'Proceed.\n',
        SKILL: BODY, ALIAS: BODY, '.claude/skills/config/SKILL.md': BODY,
        'harness/common/rules/README.human.md': 'Human text',
    }.items():
        put(tmp_path,p,value)
    return tmp_path


def read(root, path, method='read'):
    return dict(type=method,path=path,text=(root/path).read_bytes().decode())


def observe(root, index='required', client='codex', mode='common'):
    paths = [ENTRY_RULE, ALWAYS]
    events = [read(root, ENTRY if client=='codex' else 'CLAUDE.md', 'native')]
    if client=='claude':
        events.extend(read(root,p,'native') for p in paths)
    events.append(dict(type='listing',paths=paths))
    if client=='codex':
        events.extend(read(root,p) for p in paths)
    if index=='required':
        events.extend(read(root,p) for p in (COMMON_MAP,PROJECT_MAP))
    events.append(dict(type='action',id='explain',observed='the value is 2'))
    return {'client':client,'mode':mode,'scenario':'explain','index':index,'completed':True,
            'startup_visible':True,'events':events,'actions':[{'id':'explain','expected':'the value is 2'}]}


@pytest.mark.parametrize('index',['required','on-demand'])
@pytest.mark.parametrize('client',['codex','claude'])
@pytest.mark.parametrize('mode',['common','both'])
def test_six_lines_and_delivery_method(root,index,client,mode):
    result = AUDIT(root, observe(root,index,client,mode))
    assert result['rule_reading_pass'], result
    assert set(result['first_reads'].values())==({'native'} if client=='claude' else {'read'})
    assert len(result['rule_read_report'])==6
    assert result['delivery_methods']['CLAUDE.md' if client=='claude' else ENTRY]==['native']
    assert (COMMON_MAP in result['delivery_methods'])==(index=='required')
    assert result['observed_actions']==['explain']


@pytest.mark.parametrize('mutation', ['no-native','truncated-entry','no-task','wrong-answer',
                                     'parallel','unclassified','removed-file',
                                     'stale','incomplete-rules','early-map','wrong-map-order',
                                     'missing-map','leaked-human','unfinished'])
def test_incomplete_or_wrong_evidence_never_passes(root,mutation):
    t=observe(root);events=t['events']
    if mutation=='no-native': t['startup_visible']=False
    if mutation=='truncated-entry': events.pop(0)
    if mutation=='no-task': events.pop()
    if mutation=='wrong-answer': events[-1]['observed']='something else'
    if mutation=='parallel': events[3].update(start=2,end=4)
    if mutation=='unclassified':events.insert(-1,dict(type='unobserved',reason='incomplete payload'))
    if mutation=='removed-file':events.insert(-1,dict(type='invalidate',path=ENTRY_RULE))
    if mutation=='stale': events[2]['text']='# A previous version\n'
    if mutation=='incomplete-rules':events.pop(2)
    if mutation=='early-map':events.insert(2,events.pop(4))
    if mutation=='wrong-map-order':events[4],events[5]=events[5],events[4]
    if mutation=='missing-map':events.pop(4)
    if mutation=='leaked-human':events.insert(3,dict(type='read',path='.claude/rules/README.human.md',text=''))
    if mutation=='unfinished':t['completed']=False
    result=AUDIT(root,t)
    assert not result['rule_reading_pass']
    if mutation=='no-native':
        assert result['status']=='не проверено'
        assert 'не проверено' in result['rule_read_report'][0]
    if mutation=='leaked-human': assert 'Human text' not in str(result)


@pytest.mark.parametrize('mode,repeat_path', [
    ('common', ENTRY_RULE),
    ('both', 'harness/project/rules/sub/config.md'),
])
def test_repeated_rule_read_is_counted_without_failing_the_trace(root, mode, repeat_path):
    trace = observe(root, mode=mode)
    trace['events'].insert(4, read(root, repeat_path))
    result = AUDIT(root, trace)
    assert result['rule_reading_pass'], result
    assert result['duplicate_reads'] == {ENTRY_RULE: 1}
    assert result['observed_actions'] == ['explain']


def config_case(root):
    t=observe(root)
    t['actions'].append(dict(id='write',expected='value=3'))
    t['links']=[dict(owner=ENTRY_RULE,path=SKILL,condition='change',before='write')]
    t['expected_conditions']=['change']
    t['events'].extend([dict(type='condition',id='change'), read(root,ALIAS),
                        dict(type='action',id='write',observed='value=3')])
    return t


@pytest.mark.parametrize('client', ['codex', 'claude'])
def test_single_return_without_listing_and_unconditional_skill(root, client):
    trace = observe(root, client=client)
    method = 'native' if client == 'claude' else 'read'
    trace['events'][1:4] = [
        dict(type=method, files=[dict(path=p, text=(root/p).read_text()) for p in (ENTRY_RULE, ALWAYS)]),
        read(root, SKILL)]
    trace['links'] = [dict(owner=ENTRY_RULE, path=SKILL, condition=None)]
    result = AUDIT(root, trace)
    assert result['rule_reading_pass'], result
    assert not result['rule_listing_completed']
    assert set(result['first_reads']) == {ENTRY_RULE, ALWAYS}


def test_native_skill_already_in_context_and_optional_listing(root):
    trace = observe(root)
    trace['links'] = [dict(owner=ENTRY_RULE, path=SKILL, condition=None)]
    trace['events'].insert(1, read(root, SKILL, 'native'))
    assert AUDIT(root, trace)['rule_reading_pass']
    trace['events'].pop(1)
    trace['events'].insert(3, trace['events'].pop(1))
    trace['events'].insert(4, read(root, SKILL))
    assert AUDIT(root, trace)['rule_reading_pass']


def test_partial_rule_in_batch_must_be_completed_before_action(root):
    trace = observe(root, index='on-demand')
    content = (root/ALWAYS).read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    files = [dict(path=ENTRY_RULE, text=OWNER),
             dict(path=ALWAYS, text=content[:2].decode(), offset=0, sha256=digest)]
    trace['events'][1:4] = [dict(type='read', files=files)]
    critical = AUDIT(root, trace)
    assert critical['status'] == 'ошибка' and ALWAYS in critical['missing_rule_paths']
    assert 'критическая ошибка' in critical['rule_read_report'][-1]
    trace['events'].insert(-1, dict(type='read', path=ALWAYS, text=content[2:].decode(),
                                    offset=2, sha256=digest))
    assert AUDIT(root, trace)['rule_reading_pass']
    trace['events'][-2]['sha256'] = '0'*64
    assert not AUDIT(root, trace)['rule_reading_pass']


def test_inaccessible_rule_stops_before_task(root):
    trace = observe(root, index='on-demand')
    trace.update(expected_stop=ALWAYS, actions=[])
    trace['events'][3:] = [dict(type='error', path=ALWAYS),
                            dict(type='stop', path=ALWAYS, reason='permission denied')]
    assert AUDIT(root, trace)['rule_reading_pass']


@pytest.mark.parametrize('reference', ['config', SKILL])
@pytest.mark.parametrize('trigger', ['unconditional', 'at-start', 'mid-task', 'inactive'])
def test_when_each_textual_reference_is_due(root, reference, trigger):
    owner = ('До первого действия прочитай файл ' if trigger == 'unconditional' else 'Перед правкой прочитай файл ') + reference
    for path in (ENTRY_RULE, 'harness/project/rules/sub/config.md'):
        put(root, path, owner)
    trace = observe(root, index='on-demand')
    write = dict(type='action', id='write', observed='value=3')
    trace['events'].insert(1, dict(type='metadata', path=SKILL, name='config', description='Use before edits.'))
    trace['links'] = [dict(owner=ENTRY_RULE, path=SKILL, condition=None if trigger=='unconditional' else 'change',
                           before='explain' if trigger=='inactive' else 'write')]
    if trigger == 'unconditional':
        trace['events'].insert(4, read(root, SKILL))
    elif trigger != 'inactive':
        if trigger == 'at-start':
            trace['actions'].clear()
            trace['events'].pop()
        trace['expected_conditions'] = ['change']
        trace['actions'].append(dict(id='write', expected='value=3'))
        trace['events'].extend([dict(type='condition', id='change'), read(root, SKILL), write])
    assert AUDIT(root, trace)['rule_reading_pass']
    if trigger != 'inactive':
        trace['events'] = [e for e in trace['events'] if e.get('path') != SKILL or e['type']=='metadata']
        assert not AUDIT(root, trace)['rule_reading_pass']


def test_condition_when_discovered_mid_task(root):
    t=config_case(root)
    assert AUDIT(root,t)['rule_reading_pass']
    for pos in [1,4,-4]:
        wrong=copy.deepcopy(t)
        wrong['events'].insert(pos,wrong['events'].pop(-2))
        assert not AUDIT(root,wrong)['rule_reading_pass']
    missing=copy.deepcopy(t);del missing['events'][-3:-1]
    assert not AUDIT(root,missing)['rule_reading_pass']
    no_read=copy.deepcopy(t);no_read['events'].pop(-2)
    assert not AUDIT(root,no_read)['rule_reading_pass']
    # Metadata before an explanation is sufficient; it is no proof of delivery.
    inactive=observe(root)
    inactive['links']=[dict(owner=ENTRY_RULE,path=SKILL,condition='change',before='explain')]
    inactive['expected_catalog']=[SKILL]
    inactive['events'].insert(-1,dict(type='metadata',path=ALIAS,name='config',description='Use before edits.'))
    result=AUDIT(root,inactive)
    assert result['rule_reading_pass'] and SKILL not in result['delivery_methods']
    inactive['events'].insert(-1,read(root,ALIAS))
    assert not AUDIT(root,inactive)['rule_reading_pass']


def test_version_bound_chunks_and_invalidation(root):
    t=config_case(root)
    first, second=BODY.split('Сохрани',1)
    second='Сохрани'+second
    digest=hashlib.sha256(BODY.encode()).hexdigest()
    chunks=[dict(type='read',path=ALIAS,text=first,offset=0,sha256=digest),
            dict(type='read',path=SKILL,text=second,offset=len(first.encode()),sha256=digest)]
    t['events'][-2:-1]=chunks
    assert AUDIT(root,t)['rule_reading_pass']
    for fault in ('gap','no-version','wrong-version','changed','overlap','duplicated'):
        bad=copy.deepcopy(t)
        if fault=='gap':bad['events'].pop(-2)
        if fault=='no-version':del bad['events'][-2]['sha256']
        if fault=='wrong-version':bad['events'][-2]['sha256']='0'*64
        if fault=='changed':bad['events'].insert(-2,dict(type='invalidate',path=SKILL))
        if fault=='overlap':bad['events'][-2]=bad['events'][-3]
        if fault=='duplicated':bad['events'].insert(-1,read(root,ALIAS))
        assert not AUDIT(root,bad)['rule_reading_pass'],fault
    t['events'].insert(-1,dict(type='invalidate',path=SKILL))
    t['events'].insert(-1,read(root,ALIAS))
    assert AUDIT(root,t)['rule_reading_pass']


@pytest.mark.parametrize('position', ['before-other-rule', 'after-other-rule', 'after-index'])
def test_unconditional_skill_is_due_before_the_first_action(root, position):
    second = f'Before the first action read {SKILL}.\n'
    put(root, ALWAYS, second)
    put(root, 'harness/common/rules/start.md', second)
    trace = observe(root)
    trace['links'] = [dict(owner=owner, path=SKILL, condition=None) for owner in (ENTRY_RULE, ALWAYS)]
    events = trace['events']
    other_reads = events[3:-1]
    split = {'before-other-rule': 0, 'after-other-rule': 1, 'after-index': 3}[position]
    events[3:-1] = [*other_reads[:split], read(root, ALIAS), *other_reads[split:]]
    if position == 'after-other-rule':
        events.insert(2, events.pop(1))
    result = AUDIT(root, trace)
    assert result['rule_reading_pass'], result


@pytest.mark.parametrize('event_order', ['missing', 'late', 'stop', 'action-after-stop'])
def test_unconditional_skill_missing_at_action_requires_a_stop(root, event_order):
    trace = observe(root, index='on-demand')
    trace['links'] = [dict(owner=ENTRY_RULE, path=SKILL, condition=None)]
    events = trace['events']
    if event_order == 'late':
        events.append(read(root, ALIAS))
    if event_order in ('stop', 'action-after-stop'):
        trace.update(expected_stop=SKILL, actions=[])
        action = events.pop()
        events.extend([dict(type='error', path=ALIAS),
                       dict(type='stop', path=ALIAS, reason='permission denied')])
        if event_order == 'action-after-stop':
            events.append(action)
    result = AUDIT(root, trace)
    if event_order == 'stop':
        assert result['rule_reading_pass'], result
    else:
        assert result['status'] == 'ошибка', result
    if event_order in ('missing', 'late'):
        assert f'до действия отсутствует полный текст: {SKILL}' in result['rule_read_report'][-1]


def test_selected_native_skill_has_independent_expected_action(root):
    t=observe(root)
    t['task_skills']={SKILL:'explain'}
    t['events'][-1:-1]=[dict(type='select',path=ALIAS),read(root,SKILL,'native')]
    assert AUDIT(root,t)['rule_reading_pass']
    wrong=copy.deepcopy(t);wrong['task_skills']={}
    assert not AUDIT(root,wrong)['rule_reading_pass']
    t['events'].pop(-2)
    assert not AUDIT(root,t)['rule_reading_pass']


@pytest.mark.parametrize('mode', ['common', 'both'])
@pytest.mark.parametrize('index, before_index', [
    ('required', True),
    ('required', False),
    ('on-demand', True),
])
def test_first_skill_read_before_index_is_informational(root, mode, index, before_index):
    trace = observe(root, index=index, mode=mode)
    trace['task_skills'] = {SKILL: 'explain'}
    start = 4 if before_index else len(trace['events']) - 1
    trace['events'][start:start] = [dict(type='invoke', path=ALIAS), read(root, ALIAS)]
    result = AUDIT(root, trace)
    assert result['rule_reading_pass'], result
    assert result['skills_read_before_index'] == ([ALIAS] if before_index else [])
    if before_index:
        assert 'Информационное событие' in result['rule_read_report'][-1]
        assert ALIAS in result['rule_read_report'][-1]

    trace['events'].append(trace['events'].pop(start + 1))
    result = AUDIT(root, trace)
    assert not result['rule_reading_pass']
    assert 'до зависимого действия не получен' in result['rule_read_report'][-1]


def test_observed_stop_on_failure(root):
    t=config_case(root);t['expected_stop']=SKILL;t['actions']=t['actions'][:1]
    t['events'][-2:]=[dict(type='error',path=ALIAS),dict(type='stop',path=ALIAS,reason='unreadable')]
    # The dependent action deliberately never happens in this scenario.
    t['blocked_action']='write'
    assert AUDIT(root,t)['rule_reading_pass']
    t['events'].append(dict(type='action',id='write',observed='value=3'))
    assert not AUDIT(root,t)['rule_reading_pass']


def test_stale_copy_and_name_collision(root):
    put(root,'harness/project/rules/sub/config.md','changed')
    with pytest.raises(ValueError,match='stale'):
        AUDIT(root,observe(root))
    put(root,'harness/project/rules/sub/config.md',OWNER)
    put(root,'harness/common/rules/sub/config.md',OWNER)
    with pytest.raises(ValueError,match='Conflicting'):
        AUDIT(root,observe(root))


def test_offline_cli_and_unknown_evidence(root,tmp_path):
    case=observe(root);trace=tmp_path/'record.json';result=tmp_path/'result.json'
    trace.write_text(json.dumps(case))
    command=[sys.executable,'-B',str(CHECK),'audit',str(root),str(trace),'--output',str(result)]
    proc=subprocess.run(command,capture_output=True,text=True)
    assert proc.returncode==0,proc.stderr
    assert json.loads(result.read_text())['status']=='проверено'
    case['completed']=False;trace.write_text(json.dumps(case));result.unlink()
    proc=subprocess.run(command,capture_output=True,text=True)
    assert proc.returncode==1 and json.loads(result.read_text())['status']=='не проверено'


def test_native_command_adapter_does_not_credit_hidden_payloads(tmp_path):
    probe = runpy.run_path(str(CHECK))
    marker, paths, links = probe['diagnostic_fixture'](tmp_path,'common','search','Exclude human files.\n')
    def shell(command, output, identifier):
        return [{'type':'item.started','item':{'id':identifier,'type':'command_execution'}},
                {'type':'item.completed','item':{'id':identifier,'type':'command_execution','command':command,
                                                 'aggregated_output':output,'exit_code':0}}]
    rules = sorted(probe['snapshot_inputs'](tmp_path,'codex')[1])
    listing = "rg --files --hidden --no-ignore .claude/rules -g '*.md' -g '!README.human.md'"
    import shlex
    events = shell(listing,'\n'.join(rules),0)
    for i,p in enumerate(rules,1):
        events.extend(shell('cat '+shlex.quote(p),(tmp_path/p).read_text(),i))
    content = "rg -n 'заявка' harness -g '!README.human.md'"
    events.extend(shell(content,'\n'.join(p+':1:заявка' for p in paths),7))
    events.append({'type':'turn.completed'})
    def report():
        return probe['observe_codex'](events,tmp_path,'search',marker,paths,links,'common')
    observed=report()
    assert observed['all_machine_matches_present'] and observed['searches_exclude_human_guides']
    assert observed['native_completed'] and observed['status']=='не проверено'
    assert set(observed['first_reads'])==set(rules)
    # The actual command adapter can identify complete files inside a single
    # return, even without a listing and with a truncated final body.
    joined = shell('cat -- '+' '.join(shlex.quote(p) for p in rules),
                   ''.join((tmp_path/p).read_text() for p in rules), 2)
    events[:] = joined + events[-3:]
    assert set(report()['first_reads']) == set(rules)
    joined[-1]['item']['aggregated_output'] = (tmp_path/rules[0]).read_text() + '[truncated]'
    assert set(report()['first_reads']) == {rules[0]}
    events[-2]['item']['aggregated_output']+='\nREADME.human.md:1:'+marker
    observed=report()
    assert observed['human_canary_in_any_native_event'] and observed['human_body_line_in_tool_output']
    assert observed['status']=='ошибка' and marker not in json.dumps(observed)


def test_metadata_contract_fails_closed(root):
    t=observe(root);t['expected_catalog']=[SKILL]
    assert not AUDIT(root,t)['rule_reading_pass']
    t['events'].insert(1,dict(type='metadata',path=SKILL,name='config',description='Wrong'))
    assert not AUDIT(root,t)['rule_reading_pass']
