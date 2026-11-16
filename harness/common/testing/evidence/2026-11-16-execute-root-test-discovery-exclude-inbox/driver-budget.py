import json
from pathlib import Path
w=Path(__file__).parent;out=Path(json.loads((w/'location.json').read_text())['out']);rows=[];lines=['# Штатные бюджеты и компактность','']
for stage in ['baseline','prepared','candidate']:
 for name in ['comm-install-harness','comm-process-harness-inbox']:
  d=json.loads(json.loads((out/f'{stage}-{name}-analyze.json').read_text())['stdout']);b=d['budgets'];s=b['invoke_cost_tokens']['value'];components=b['deferred_cost_tokens']['components'];refs=[c for c in components if c['label'].startswith('references/')];other=[c for c in components if not c['label'].startswith('references/')];t=sum(c['tokens'] for c in other);assert sum(c['tokens'] for c in refs)+t==b['deferred_cost_tokens']['value']
  row={'stage':stage,'name':name,'target':d['target'],'summary':d['summary'],'checks':d['checks'],'budgets':b,'references':refs,'texts':sorted(other,key=lambda c:c['tokens'],reverse=True),'texts_total':t,'automatic_details_required':b['deferred_cost_tokens']['value']>1200,'lines':[]}
  lines.append(f"{stage}: {d['target']['kind']} {d['target']['path']} — {d['summary']['grade']}/{d['summary']['score']}; trigger/invoke/deferred/total="+'/'.join(str(b[k]['value']) for k in ['trigger_cost_tokens','invoke_cost_tokens','deferred_cost_tokens','total_tokens'])+'.')
  lines.append('Штатные thresholds/bands/checks сохранены в JSON без изменений. Texts='+str(t)+(' — полностью известный ноль: все deferred-компоненты находятся в references; иных учитываемых файлов нет.' if t==0 else '.'))
  for c in refs:
   value=s+c['tokens']+t;band='good' if value<=180 else 'moderate' if value<=520 else 'heavy-warn' if value<=1200 else 'excessive-fail';text=f"SKILL.md={s}/{c['label']}={c['tokens']} /Texts={t} --> {value} ({band})";row['lines'].append(text);lines.append(text)
  lines.append('');rows.append(row)
lines.extend(['Prepared версии превышали deferred 1200 (1542/1219) и получили B/86; они не публикуются. Компактные версии: 1199/1171, A/95 без fail/error. Штатный moderateMax=520, heavyMax=1200 не менялся; deferred warnings сохранены.','Крупнейший install reference — неизменённый checks.md (817); workflow сохраняет прежний протокол полномочий и статусов. Изменены только testing.md и добавляемый абзац workflow.md. Отдельная шкала строк — дополнительная, не замена статуса анализатора; строки не складываются.','Цель resource sum 1000 превышена и до задачи (1130/1081), и после неё; сохранение непричастного approval/install контракта важнее посторонней переработки. По сравнению с prepared избыточность уменьшена без удаления требований. Факты lock/coverage переиспользуют существующий docs owner; этот внешний документ и runtime-код учитываются отдельно от локального resource budget.','Единицы estimated-static; это не расход токенов сессии и не весь стартовый/доступный контекст. Реальные native reads/usage сохраняются отдельно.'])
with (out/'budget-details.json').open('x') as f:json.dump(rows,f,ensure_ascii=False,indent=2)
with (out/'budget-details.md').open('x') as f:f.write('\n'.join(lines)+'\n')
print('budget details saved: actual stock checks/bands/thresholds and each reference')
