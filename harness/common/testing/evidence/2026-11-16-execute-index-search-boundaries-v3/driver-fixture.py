import json
from pathlib import Path

def build(root,kind):
 def write(rel,text):p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
 def guide(rel):
  p=root/rel/'README.human.md'
  if not p.exists():write(str(p.relative_to(root)),'# FixtureWire пояснение\n\nFW-HUMAN-ONLY-93. Это человеческое пояснение, не источник контракта. Например, JSON рядом содержит рабочие данные.\n')
 for rel in ['harness/common/inbox','harness/common/testing/evidence']:guide(rel)
 canonical='harness/common/base/fixture-wire.json';write(canonical,json.dumps({'name':'FixtureWire','encoding':'UTF-8','canonical_marker':'FW-CURRENT-41'},indent=2))
 write('harness/common/docs/fixture-wire-overview.md','# FixtureWire current lookup\nCanonical contract: ../base/fixture-wire.json\n')
 current='harness/common/inbox/2026-11-16-fixture-wire-proposal';old='harness/common/inbox/2026-01-01-fixture-wire-old'
 for rel in [current,current+'/before',current+'/candidate-2099',old,old+'/current', 'harness/common/testing/evidence/2026-01-01-fixture-wire', 'harness/common/base/nested'] :guide(rel)
 write(current+'/request.md','# FixtureWire proposal\nNeed: current semantic comparison only, no execution/publication.\nSelected actual complete candidate: before/selected-2020.json\nRequired encoding: UTF-8. Candidate dates/names do not establish currency.\nOther copies here are historical and not selected for this task.\n## Execution\nStatus: in progress\nResult: current candidate selected, checks pending\nUpdated: 2026-11-16\n')
 selected=current+'/before/selected-2020.json';write(selected,json.dumps({'name':'FixtureWire','encoding':'UTF-8','candidate_marker':'FW-SELECTED-CURRENT-42'},indent=2))
 hist1=current+'/candidate-2099/fixture-wire.json';write(hist1,json.dumps({'name':'FixtureWire','encoding':'UTF-16','marker':'FW-STALE-2099-71','state':'historical, not selected'},indent=2))
 write(old+'/request.md','# FixtureWire completed old proposal\nFW-CLOSED-BODY-73: historical proposal required UTF-16. This is not the current contract.\n## Execution\nStatus: completed\nResult: superseded by current canonical contract\nUpdated: 2026-01-01\n')
 hist2=old+'/current/fixture-wire.json';write(hist2,json.dumps({'name':'FixtureWire','encoding':'UTF-16','marker':'FW-HISTORY-COPY-72'},indent=2))
 report='harness/common/testing/evidence/2026-01-01-fixture-wire/fixture-wire-old-report.md';raw='harness/common/testing/evidence/2026-01-01-fixture-wire/fixture-wire-old-raw.json'
 write(report,'# FixtureWire completed check\nResult: failed; raw: fixture-wire-old-raw.json. FW-REPORT-65.\nThis is a completed historical observation, not current requirements.\n')
 write(raw,json.dumps({'name':'FixtureWire','expected':'UTF-8','observed':'UTF-16','exit_code':1,'marker':'FW-RAW-66'},indent=2))
 if kind=='ordinary':task='В этой локальной вымышленной fixture найди действующий canonical контракт FixtureWire и скажи его текущую encoding и источник. Внешних источников нет; нужны текущие факты, только чтение, без изменений и проверочных прогонов.'
 elif kind=='selected':task=f'Только семантически сравни актуальный полный кандидат заявки {current}/request.md с её требованиями. Установи статус и применимость по текущим данным, найди именно выбранную редакцию; ничего не исполняй/публикуй и не меняй. Даты и имена каталогов сами по себе не устанавливают актуальность. Верни encoding, выбранный источник и соответствует ли требованию.'
 elif kind=='triage':task='Найди актуальную незавершённую common inbox заявку по FixtureWire и её выбранный полный кандидат. Нужен статус, применимость и семантическое соответствие encoding, только чтение; без исполнения или изменения заявок. Сравни с текущим canonical контрактом.'
 elif kind=='history':task=f'Объясни конкретное историческое расхождение FixtureWire в {report}. Прочитай именно этот завершённый report, названный им raw и действующий canonical контракт; что ожидалось, что наблюдалось и что сейчас? Только чтение, без исправления завершённого отчёта или старых raw.'
 elif kind=='unrelated':task='Вычисли 23*8. Ничего не меняй и не открывай неподходящие материалы после обязательного старта.'
 else:raise ValueError(kind)
 return {'canonical':canonical,'current_request':current+'/request.md','selected':selected,'closed_request':old+'/request.md','historical_copies':[hist1,hist2],'historical_markers':['FW-STALE-2099-71','FW-HISTORY-COPY-72'],'closed_marker':'FW-CLOSED-BODY-73','report':report,'raw':raw,'evidence_markers':['FW-REPORT-65','FW-RAW-66'],'human_marker':'FW-HUMAN-ONLY-93'},task
