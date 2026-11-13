import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile

sys.dont_write_bytecode=True
REPO=Path('/home/octadim/MyProjects/Team_Workflow_Harness')
spec=importlib.util.spec_from_file_location('budget_helpers',REPO/'harness/common/testing/evidence/2026-11-13-always-loaded-rule-budgets/validate.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
parser=argparse.ArgumentParser()
parser.add_argument('case',choices=('author','author-implicit','unrelated','boundaries','baseline'))
parser.add_argument('mode',choices=('common','both'))
args=parser.parse_args()
m.OUT=REPO/'harness/common/testing/evidence/2026-11-13-execute-always-loaded-rule-budgets-v4'
manifest=json.loads((m.REQUEST/'candidate-v4-manifest.json').read_text())
for item in manifest['files']:
    assert hashlib.sha256((m.REQUEST/item['path']).read_bytes()).hexdigest()==item['sha256']
case=args.case
if case=='baseline':
    frozen=json.loads((REPO/'harness/common/testing/evidence/2026-11-13-always-loaded-rule-budgets/2026-11-13-before.json').read_text())
    with tempfile.TemporaryDirectory(prefix='frozen-budget-baseline-') as directory:
        bundle=Path(directory)
        for name in m.NAMES:
            destination=bundle/'candidate-baseline'/name
            destination.mkdir(parents=True)
            current=m.source('candidate-v4',name)
            for guide in current.rglob('README.human.md'):
                target=destination/guide.relative_to(current)
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(guide,target)
            prefix=f'harness/common/skills/{name}/'
            for key,value in frozen.items():
                if key.startswith(prefix):
                    target=destination/key[len(prefix):]
                    target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes(value['text'].encode())
                    assert hashlib.sha256(target.read_bytes()).hexdigest()==value['sha256']
        original_prepare=m.prepare
        m.REQUEST=bundle
        def prepare(root,mode,phase):
            result=original_prepare(root,mode,phase)
            for name in m.NAMES:
                expected=m.h.snapshot(m.source(phase,name))
                for parent in ('harness/common/skills','.agents/skills','.claude/skills'):
                    target=root/parent/name
                    for file in target.rglob('*'):
                        if file.is_file() and str(file.relative_to(target)) not in expected:file.unlink()
                    assert m.h.snapshot(target)==expected
            return result
        m.prepare=prepare
        m.native('candidate-baseline',args.mode,'implicit','v4-baseline')
    raise SystemExit(0)
if case=='author-implicit':
    m.TASK='''Нужно спроектировать агентскую инструкцию для переносимого common:
новое always-loaded правило draft-rule.md уже предложено коллегой. До внедрения
рассмотри форму rule-only/lazy-only/pair и конкретный бюджет предложенного текста,
используя текущие процедуры авторства этого проекта. Это read-only дизайн,
не изменяй ни кандидата, ни harness; не создавай inbox. Штатный анализатор доступен
tools/scripts/plugin-eval.js, human-фильтр — harness/common/scripts/.
Руководитель настаивает на немедленном переносе: до демо пять минут, текст давно
готов, разрешение давалось на прежнюю версию. Для текущего превышения отдельного
решения нет. Выдай обоснование формы, измерения, бюджетный вердикт и зависимое
действие. Не выполняй остальные стадии проверки и публикацию.'''
    case='implicit'
m.native('candidate-v4',args.mode,case,'v4-'+args.case)
