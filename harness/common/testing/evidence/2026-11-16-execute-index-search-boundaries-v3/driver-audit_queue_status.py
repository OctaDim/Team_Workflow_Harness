from pathlib import Path
import re,json
repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');rows=[];unknown=[]
for pkg in ['common','project']:
 for p in sorted((repo/f'harness/{pkg}/inbox').glob('*/request.md')):
  found=[]
  for i,s in enumerate(re.split(r'(?m)^(?=#{1,4} )',p.read_text().replace('**',''))):
   if not s.strip() or 'истори' in s.splitlines()[0].lower():continue
   ms=list(re.finditer(r'(?im)^\s*(?:-\s*)?(?:Status|Статус)\s*:\s*(new|in progress|completed|blocked|rejected|выполнена|отклонена|новая|в работе|заблокирована)\b',s))
   if ms:
    dates=re.findall(r'(?im)^\s*(?:-\s*)?(?:Updated|Обновлено|Дата обновления)\s*:\s*(\d{4}-\d\d-\d\d[^\n]*)',s);found.append((dates[-1] if dates else '',i,ms[-1].group(1)))
  status=max(found)[2] if found else 'unknown'
  if status not in ['completed','rejected','выполнена','отклонена']:rows.append({'request':p.parent.name,'package':pkg,'status':status,'updated':max(found)[0] if found else None})
print(json.dumps(rows,ensure_ascii=False,indent=2))
out=Path(json.loads((Path(__file__).parent/'location.json').read_text())['out']);
with (out/'queue-status-v3.json').open('x') as f:json.dump({'note':'Supports Russian legacy and bold execution fields; current latest dated nonhistorical section takes precedence. Original narrower parser retained as diagnostic.','open':rows},f,ensure_ascii=False,indent=2)
