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


@pytest.mark.parametrize('mutation', ['no-native','truncated-entry','no-task','wrong-answer','no-list',
                                     'incomplete-list','parallel','unclassified','removed-file',
                                     'repeated','stale','incomplete-rules','early-map','wrong-map-order',
                                     'missing-map','leaked-human','unfinished'])
def test_incomplete_or_wrong_evidence_never_passes(root,mutation):
    t=observe(root);events=t['events']
    if mutation=='no-native': t['startup_visible']=False
    if mutation=='truncated-entry': events.pop(0)
    if mutation=='no-task': events.pop()
    if mutation=='wrong-answer': events[-1]['observed']='something else'
    if mutation=='no-list': events.pop(1)
    if mutation=='incomplete-list': events[1]['paths'].pop()
    if mutation=='parallel': events[3].update(start=2,end=4)
    if mutation=='unclassified':events.insert(-1,dict(type='unobserved',reason='incomplete payload'))
    if mutation=='removed-file':events.insert(-1,dict(type='invalidate',path=ENTRY_RULE))
    if mutation=='repeated': events.insert(4,read(root,'harness/project/rules/sub/config.md'))
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


def config_case(root):
    t=observe(root)
    t['actions'].append(dict(id='write',expected='value=3'))
    t['links']=[dict(owner=ENTRY_RULE,path=SKILL,condition='change',before='write')]
    t['expected_conditions']=['change']
    t['events'].extend([dict(type='condition',id='change'), read(root,ALIAS),
                        dict(type='action',id='write',observed='value=3')])
    return t


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


def test_unconditional_acquired_immediately_or_already_present(root):
    t=observe(root)
    t['links']=[dict(owner=ENTRY_RULE,path=ALIAS,condition=None)]
    t['events'].insert(3,read(root,SKILL))
    assert AUDIT(root,t)['rule_reading_pass']
    bad=copy.deepcopy(t);bad['events'].insert(4,bad['events'].pop(3))
    assert not AUDIT(root,bad)['rule_reading_pass']
    second='Read immediately: '+SKILL+'\n'
    put(root,ALWAYS,second);put(root,'harness/common/rules/start.md',second)
    t['events'][4]=read(root,ALWAYS)
    t['links'].append(dict(owner=ALWAYS,path=SKILL,condition=None))
    assert AUDIT(root,t)['rule_reading_pass']


def test_selected_native_skill_has_independent_expected_action(root):
    t=observe(root)
    t['task_skills']={SKILL:'explain'}
    t['events'][-1:-1]=[dict(type='select',path=ALIAS),read(root,SKILL,'native')]
    assert AUDIT(root,t)['rule_reading_pass']
    wrong=copy.deepcopy(t);wrong['task_skills']={}
    assert not AUDIT(root,wrong)['rule_reading_pass']
    t['events'].pop(-2)
    assert not AUDIT(root,t)['rule_reading_pass']


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
    events[-2]['item']['aggregated_output']+='\nREADME.human.md:1:'+marker
    observed=report()
    assert observed['human_canary_in_any_native_event'] and observed['human_body_line_in_tool_output']
    assert observed['status']=='ошибка' and marker not in json.dumps(observed)


def test_metadata_contract_fails_closed(root):
    t=observe(root);t['expected_catalog']=[SKILL]
    assert not AUDIT(root,t)['rule_reading_pass']
    t['events'].insert(1,dict(type='metadata',path=SKILL,name='config',description='Wrong'))
    assert not AUDIT(root,t)['rule_reading_pass']
