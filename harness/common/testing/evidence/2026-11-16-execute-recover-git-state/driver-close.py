import hashlib,importlib.util,json,os,shutil
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
w=Path(__file__).parent;loc=json.loads((w/'location.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);source=Path(loc['source']);sp=importlib.util.spec_from_file_location('g',repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
assert json.loads((out/'publication.json').read_text())['full_copies_equal'];r=g.h.run([g.PYTHON,'-m','pytest','-q'],cwd=repo,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'),timeout=300);g.save(out/'installed-root-suite.json',r);assert r['exit_code']==0,r['stdout'][-1500:];before=json.loads((out/'before.json').read_text());assert g.protect()==before['protected'];actual=g.h.snapshot(source)
for parent in ['harness/common/skills','.agents/skills','.claude/skills']:assert g.h.snapshot(repo/parent/source.name)==actual
now=datetime.now(ZoneInfo('Europe/Minsk')).isoformat();report=out/'2026-11-16-report.md'
text='''# Восстановление Git по фактам и точным разрешениям

Опубликован подготовленный comm-recover-git-state: полный SKILL, modes и human
папки, равные ordinary canonical/.agents/.claude копии. Новый lazy-владелец
объединяет восстановление; общие сохранность, naming, факты, commits/публикация
и проверка поведения остаются действующим владельцам. Новое правило не создано.
Точные hashes: before.json, native-review-final.json, publication-gate.json,
publication.json. Корневые entrypoints, project и правила не менялись.

Маршрут writing-skills: два реальных baseline без кандидата, затем проверка
подготовленного кандидата. Оба baseline прошли свои технические сценарии:
merge с primary вторым родителем плюс одно-родительский squash; abort-risk с
чужим staging и отсутствующим дооперационным снимком. Новых инструкций по этим
успешным controls не написано. RED и причинный выигрыш не выдумываются;
версия кандидата сохранилась без редакционных изменений. Полные baseline
ответы/пределы — baseline-assessment.json и исходные JSON.

Текущая native матрица Codex: 20/20, по 10 в common-only/common+project,
явные и неявные вызовы, собственный modes и общие when-read ресурсы,
полный startup/discovery до тел, нерелевантная арифметика без загрузки тел.
Проверены незавершённый merge и применимый abort; точный разрешённый reset;
отказ от мутаций при недостаточной authority/чужих правках; опубликованные
merge/squash, выбор mainline по реальным parents и будущие merges; потерянный
ref и истёкший/удалённый объект; восстановление одной recovery-ветки с naming
без изменения оригинала; расхождение содержимого; PR read only.
Положительные abort/reset реально выполняются и проходят поведенческую пробу
в своих временных репозиториях; исходный/целевой/фактический SHA и refs/index/
files сверяются. Published corrective/revert проверяется как решение: fixture
не разрешает его исполнение, commit/revert/push не заявляются выполненными.
В опубликованной пробе tree merge уже равен primary: mainline=2 сам по себе
не делает revert необходимым; отдельный одно-родительский squash оценивается
по его фактическому эффекту. Контракт/границы сценариев — contract-coverage.json; порядок чтений до мутаций
проверяется отдельно от итогового количества результатов.
Дополнительный operation-audit-final-v2.json проверяет попытки команд: чтение
без мутаций и только разрешённые операции положительных сценариев. Ошибки
парсера (merge-base, stash list, config getter и CAS update-ref с переменными)
разобраны по полным командам и AST; исходные аудиты и отдельные дополнения
сохранены, candidate/raw не менялись.

У самого драйвера обнаружен побочный __pycache__ родительской пробы: первоначально
после-agent снимок снимался после её выполнения. Исходные записи сохранены;
исправлены порядок снимка и bytecode-режим, положительные common сценарии
повторены с current-frozen. Нормальная смена HEAD в worktree-описании при
разрешённом reset учитывается как ожидаемый результат. Ошибка имени queue.py
до запуска CLI также не считается native результатом. Ни одна из этих ошибок
не исправлялась изменением кандидата или переписыванием raw.

Skill-creator и stock plugin-eval 0.1.2: A100 до и после публикации,
invoke 383, deferred 294, trigger 41, total 718; предупреждений бюджета и
fail/error нет, пороги/coverage не менялись. Два полных изолированных набора:
195 passed common-only и 195 passed common+project. Project-only отказал до
записи; repeat startup не меняет состояние; project сохранён.
Реальный рабочий набор после публикации: ROOT_RESULT.

Внешние машинные зависимости сверены с before каждого native запуска,
хеши — external-dependencies.json. Startup/metadata, собственные ресурсы,
полная доступная библиотека и фактические reads/session usage отдельно —
context-accounting.json. Изоляция исключает глобальные авторские инструкции;
перенос работает на обычных копиях. CLI 0.166.0 (default model/effort, без override),
Git 2.43.0, Python 3.12.15, pytest 8.4.2, Node 22.14.0.

Первичные технические источники: ограничения
[merge --abort](https://git-scm.com/docs/git-merge),
[mainline и последствия revert для будущих merges](https://git-scm.com/docs/git-revert),
[локальные истекающие reflogs](https://git-scm.com/docs/git-reflog),
[эффект reset на HEAD/index/files](https://git-scm.com/docs/git-reset).
Документация поддерживает технические границы; результаты запуска относятся
к указанной установленной версии. Универсальная восстановимость не обещается.

Codex/common-only: проверен в документированной текущей области.
Codex/common+project: проверен в документированной текущей области.
Claude/common-only и Claude/common+project: не запускались; непроверенные.
Итоговый статус: непроверенный.
'''.replace('ROOT_RESULT',r['stdout'].strip().splitlines()[-1]+'; exit 0')+'\nЗавершено: '+now+'.\n'
with report.open('x') as f:f.write(text)
p=source.parent.parent/'request.md'
with p.open('a') as f:f.write('\n## Execution — результат текущего исполнения\n\nStatus: completed\nResult: полный comm-recover-git-state опубликован в canonical/.agents/.claude; Codex 20/20, режимы 195/195, рабочий набор 195 passed.\nReason: требования и обязательные текущие проверки выполнены; исходный кандидат не изменялся, baseline также прошёл.\nReport: ../../testing/evidence/'+out.name+'/2026-11-16-report.md\nUpdated: '+now+'\nCodex/common-only: verified (documented current scope)\nCodex/common+project: verified (documented current scope)\nClaude/common-only: not run; unverified\nClaude/common+project: not run; unverified\nOverall: unverified\n')
for filename in ['publish.py','close.py']:shutil.copyfile(w/filename,out/('driver-'+filename))
g.save(out/'completion.json',{'source':actual,'protected_unchanged':True,'full_copies_equal':True,'completed':now,'root_suite':r['stdout'].strip().splitlines()[-1]});print('Recovery request completed; '+r['stdout'].strip().splitlines()[-1])
