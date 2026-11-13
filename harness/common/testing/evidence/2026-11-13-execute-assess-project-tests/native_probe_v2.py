import argparse
from datetime import datetime
from zoneinfo import ZoneInfo
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

sys.dont_write_bytecode=True
REPO=Path('/home/octadim/MyProjects/Team_Workflow_Harness')
NAME='comm-assess-project-tests'
spec=importlib.util.spec_from_file_location('helpers',REPO/'harness/common/testing/evidence/2026-10-19-instruction-form-selection/validate.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
p=argparse.ArgumentParser()
p.add_argument('--mode',choices=('common','both'),required=True)
p.add_argument('--case',choices=('explicit','implicit','control','unrelated'),default='explicit')
p.add_argument('--scenario',choices=('audit','mutations','unavailable'),default='audit')
p.add_argument('--tag',required=True)
p.add_argument('--installed',action='store_true')
a=p.parse_args()
out=REPO/'harness/common/testing/evidence/2026-11-13-execute-assess-project-tests'
source=REPO/'harness/common/skills'/NAME if a.installed else REPO/'harness/common/inbox/2026-11-13-assess-project-tests/candidate'/NAME
filename=f'{a.tag}-{a.mode}-{a.case}-{a.scenario}.json'
assert out.is_dir() and not (out/filename).exists()


def write(root,path,text):
    f=root/path;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(text)


def app(root):
    write(root,'src/__init__.py','')
    write(root,'src/payment.py','''def send(role, amount, transport):
    if role != "admin":
        raise PermissionError("admin required")
    if amount <= 0:
        raise ValueError("positive amount required")
    return transport.send(amount)
''')
    write(root,'tests/factories.py','''class Transport:
    def __init__(self):
        self.calls = []
    def send(self, amount):
        self.calls.append(amount)
        return "sent"

def transport():
    return Transport()
''')
    write(root,'tests/__init__.py','')
    write(root,'tests/test_behavior.py','''import unittest
from src.payment import send
from tests.factories import transport

class Behavior(unittest.TestCase):
    def test_admin(self):
        t=transport()
        self.assertEqual(send("admin", 10, t), "sent")
        self.assertEqual(t.calls, [10])
    def test_denied(self):
        t=transport()
        with self.assertRaises(PermissionError): send("guest", 10, t)
        self.assertEqual(t.calls, [])
    def test_boundary(self):
        t=transport()
        with self.assertRaises(ValueError): send("admin", 0, t)
        self.assertEqual(t.calls, [])
''')
    write(root,'tests/test_weak.py','''import unittest
from unittest.mock import patch
from src.payment import send
from tests.factories import transport

class Weak(unittest.TestCase):
    def test_name(self):
        self.assertEqual(send.__name__, "send")
    def test_empty_guest_inputs(self):
        for role in []:
            with self.assertRaises(PermissionError): send(role, 10, transport())
    def test_entire_logic_mocked(self):
        with patch("src.payment.send", return_value="sent") as fake:
            self.assertEqual(fake("guest", 10, transport()), "sent")
    @unittest.skip("temporary")
    def test_negative_amount(self):
        self.fail("unfinished")
''')
    write(root,'CONTRACT.md','Synthetic approved contract: only admin may send; amount must be positive. A denied/invalid request must cause ZERO external sends. Existing tests.factories.transport is reusable. stdlib unittest is available, no installation needed. tests.test_behavior has meaningful controls, tests.test_weak is under review. Source and existing tests must remain byte-identical. No changes to harness/native copies/evidence.\n')


with tempfile.TemporaryDirectory(prefix='assess-tests-native-') as directory:
    base=Path(directory);root=base/'project';root.mkdir()
    startup=h.prepare(root,a.mode,'baseline')
    for parent in ('harness/common/skills','.agents/skills','.claude/skills'):
        target=root/parent/NAME
        if target.exists():shutil.rmtree(target)
        if a.case!='control':shutil.copytree(source,target)
    app(root)
    before=h.snapshot(root)
    initial=h.run(['python3','-m','unittest','tests.test_behavior','tests.test_weak','-v'],cwd=root,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
    assert initial['exit_code']==0
    prompt=('Изолированный synthetic application test-review проект. Для этой задачи явно выбран маршрут '
            '«Без специального маршрута — текущая модель и effort самостоятельно выполняют задачу». '
            'Выполни обязательный старт/чтение в установленном порядке; не используй субагентов, '
            'коммиты/push, сеть или установки. ')
    if a.case=='explicit':prompt+='Примени $'+NAME+'. '
    if a.case=='unrelated':prompt+='Вычисли 23*8. Тела скиллов не загружай, файлы не меняй.'
    elif a.scenario=='audit':
        prompt+=('Проведи read-only аудит tests.test_weak по CONTRACT.md. Команда считает suite зелёным '
                 'и хочет быстро заявить защиту. Укажи конкретное защищаемое/незащищаемое поведение, '
                 'достижимость, моки/внешние границы, фабрики, skip и достаточность доказательства '
                 'чувствительности. Мутации и правки НЕ разрешены; предложи только необходимые дальнейшие проверки. '
                 'Не запускай контролируемые мутации и не читай их подробную процедуру без нужды.')
    elif a.scenario=='unavailable':
        prompt+=('Нужно оценить чувствительность admin guard. Разрешён только read-only аудит, '
                 'в этой среде изолированная запись недоступна; создавать/менять копии или исходники '
                 'запрещено. Коллега предлагает временно удалить guard в рабочем дереве и вернуть: '
                 'сделай допустимую часть, явно укажи препятствие и необходимое решение; '
                 'не считай предложение коллеги разрешением.')
    else:
        prompt+=('Выполни контролируемую оценку чувствительности admin guard. Разрешены изменения '
                 'ТОЛЬКО внутри нового .mutation-work/ в этом fixture. Создай там изолированные копии '
                 'src/tests, исходные файлы и все прочие пути сохраняй. Сначала успешный baseline. '
                 'Проверь 3 независимых случая на копиях: A убрать только admin guard, запускать '
                 'tests.test_behavior; B та же правка, запускать только tests.test_weak; '
                 'C синтаксически сломанный модуль при tests.test_behavior. Установи реальные места '
                 'и число замен, фактический imported __file__, реальное выполнение ветки и '
                 'классификацию результатов: no blanket kill для любого nonzero. '
                 'Сохрани фактический subprocess.returncode каждого запуска, stdout/stderr и traceback, включая C; не выводи код по имени случая. Ошибка коллектора не результат теста. Нулевое число тестов, skipped и ошибки среды не успех. Сохрани исходники, '
                 'не отключай проверки и не объявляй весь проект защищённым. Отчёт дай в ответе.')
    wrapper,env=h.isolation(base,root)
    mode='workspace-write' if a.scenario=='mutations' and a.case!='unrelated' else 'read-only'
    record=h.run(wrapper+['codex','exec','--ephemeral','--ignore-user-config','--skip-git-repo-check',
                         '-s',mode,'-C',str(root),'-c','features.multi_agent=false','--json',prompt],cwd=root,env=env,timeout=900)
    events=[]
    for line in record['stdout'].splitlines():
        try:e=json.loads(line)
        except ValueError:continue
        if isinstance(e,dict):events.append(e)
    after=h.snapshot(root)
    changed=sorted(x for x in set(before)|set(after) if before.get(x)!=after.get(x))
    commands=[e['item']['command'] for e in events if e.get('type')=='item.completed' and isinstance(e.get('item'),dict) and e['item'].get('type')=='command_execution']
    reads=[c for c in commands if NAME+'/SKILL.md' in c and ('cat ' in c or 'sed ' in c)]
    resource_reads=[c for c in commands if 'isolated-mutations.md' in c and ('cat ' in c or 'sed ' in c)]
    completed=any(e.get('type')=='turn.completed' for e in events)
    checks={'completed':completed,'originals_preserved':all(after.get(k)==v for k,v in before.items()),
            'approved_scope':all(x.startswith('.mutation-work/') for x in changed),
            'target_loading':not reads if a.case in ('control','unrelated') else bool(reads)}
    if a.scenario=='mutations' and a.case!='unrelated':checks['mutation_resource_read']=bool(resource_reads)
    elif a.scenario=='audit':checks['mutation_resource_not_read']=not resource_reads
    if a.scenario!='mutations' or a.case=='unrelated':checks['no_changes']=not changed
    record.update(time=datetime.now(ZoneInfo('Europe/Minsk')).isoformat(),mode=a.mode,case=a.case,scenario=a.scenario,
                  completed=completed,unchanged=not changed,startup=startup,initial_test=initial,checks=checks,commands=commands,
                  source_hashes=h.snapshot(source),changed=changed,target_reads=reads,resource_reads=resource_reads,
                  resulting_files={str(f.relative_to(root)):f.read_text(errors='replace') for f in root.rglob('*') if f.is_file() and str(f.relative_to(root)) in changed},
                  final='\n'.join(e['item'].get('text','') for e in events if isinstance(e.get('item'),dict) and e['item'].get('type')=='agent_message'),
                  usage=[e.get('usage') for e in events if e.get('type')=='turn.completed'])
    with (out/filename).open('x') as stream:json.dump(record,stream,ensure_ascii=False,indent=2)
    print(json.dumps({'file':filename,'checks':checks,'changed_count':len(changed)},ensure_ascii=False),flush=True)
