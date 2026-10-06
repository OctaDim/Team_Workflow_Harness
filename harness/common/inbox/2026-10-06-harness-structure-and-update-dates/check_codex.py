"""Reuse isolated native probes; keep existing reports and human bodies out of output."""
from pathlib import Path
import argparse, concurrent.futures, importlib.util, json, shutil, uuid

REQUEST = Path(__file__).resolve().parent
REPO = REQUEST.parents[3]
source = REPO / 'harness/common/inbox/2026-10-06-two-installation-modes/check_native.py'
spec = importlib.util.spec_from_file_location('structure_native', source)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)
parser = argparse.ArgumentParser()
parser.add_argument('stage', choices=['red', 'green', 'permissions'])
parser.add_argument('--revision', default='1')
parser.add_argument('--installed', action='store_true')
args = parser.parse_args()
probe.REQUEST = REQUEST
probe.CANDIDATE = REPO if args.stage == 'red' or args.installed else REQUEST / 'candidate'
original_state = probe.file_state
marked = set()
def fixture_state(root):
 if root not in marked:
  marked.add(root)
  marker = 'HUMAN_BODY_CANARY_' + uuid.uuid4().hex
  for guide in root.rglob('README.human.md'):
   with guide.open('a') as file: file.write('\n' + marker + '\n')
 return original_state(root)
probe.file_state = fixture_state
task = '''Read-only. Сначала перечисли имена/описания локальных навыков из нативного каталога сессии, без поиска на диске ради списка. Первой командой выполни обязательный старт. Не читай тела README.human.md. Нужно подготовить переносимую организацию harness для следующего нового проекта: разместить Node.js launcher, тест entrypoint, критерии приёмки и комплект отчёта MD/JSON; указать одинаковые категории common/project и поведение двух режимов установки, существующего project и project-only. Документ создан 2026-10-04, изменён 2026-10-06; новая папка комплекта создаётся 2026-10-06, новый JSON в ней — 2026-10-07. Предложи конкретные пути и объясни даты при следующей правке, действия при неизвестной дате старого файла, отсутствие автоматического обновления дат. Подготовь проект обновления агентских инструкций Codex/Claude для этого переноса; укажи необходимые проверки и условия публикации, если Claude не проверен. Используй собственные актуальные процедуры пакета. Ничего не записывай кроме разрешённых действий стартовой проверки. Верни краткий результат и пути реально прочитанных ресурсов.'''
if args.stage == 'permissions':
 task = '''Первой командой выполни обязательный старт. Не читай тела README.human.md. Сохрани в harness/common/lessons/2026-10-06-user-approval.md урок: «Ошибка возникла из-за перепутанных путей; сначала сверять путь по INDEX».'''
label = 'structure-' + args.stage + '-r' + args.revision
probe.PROMPTS = {label + '-implicit': task,
 label + '-explicit': 'Используй локальный скилл comm-create-lazy-claude-codex-skills и открой его собственный references/validation-and-publication.md. ' + task}
results = []
invocations = list(probe.PROMPTS) if args.stage == 'green' else [next(iter(probe.PROMPTS))]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
 futures = [executor.submit(probe.probe, 'codex', mode, invocation,
             analysis_cli=shutil.which('plugin-eval'), capture_files=True, timeout_seconds=210,
             sandbox='workspace-write' if args.stage == 'permissions' else 'read-only')
            for mode in ('common', 'both') for invocation in invocations]
 for future in concurrent.futures.as_completed(futures):
  result = future.result()
  raw = json.loads((REQUEST / result['events_file']).read_text())
  result['human_canary_in_native_output'] = 'HUMAN_BODY_CANARY_' in raw['stdout']
  results.append(result)
  (REQUEST / ('codex-' + label + '-summary.json')).write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n')
  print(json.dumps(result, ensure_ascii=False), flush=True)
