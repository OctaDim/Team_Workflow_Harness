import importlib.util,json,os,shutil
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
w=Path(__file__).parent;loc=json.loads((w/'location-v2.json').read_text());repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=Path(loc['out']);source=Path(loc['source']);oldout=Path(loc['previous_out']);sp=importlib.util.spec_from_file_location('g',repo/'harness/common/testing/evidence/2026-11-13-execute-check-current-harness-duplicates/validate_execution.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
assert json.loads((out/'publication.json').read_text())['full_copies_equal'];r=g.h.run([g.PYTHON,'-m','pytest','-q'],cwd=repo,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'),timeout=300);g.save(out/'installed-root-suite.json',r);assert r['exit_code']==0,r['stdout'][-1500:];before=json.loads((out/'before.json').read_text());assert g.protect()==before['protected'];actual=g.h.snapshot(source)
for parent in ['harness/common/skills','.agents/skills','.claude/skills']:assert g.h.snapshot(repo/parent/source.name)==actual
now=datetime.now(ZoneInfo('Europe/Minsk')).isoformat();report=out/'2026-11-16-report.md'
text='''# Миграция репозитория с проверкой связанных свойств

Опубликован comm-migrate-git-repository candidate-v2: полные равные ordinary
canonical/.agents/.claude папки, 15 файлов. Новый lazy-владелец связывает
идентичность, механизм, инвентарь и проверки интеграций; общие выбор подхода,
сохранность Git, факты/тесты и разрешения остаются действующим владельцам.
Правило не добавлено. Entry points, project, правила и существующие чужие
изменения сохранены. Точная версия/hashes — before.json, native-review-final.json,
publication-gate.json и publication.json.

Маршрут writing-skills: baseline → подготовленный кандидат → исправление when-read
→ GREEN → текущие проверки → публикация. Baseline links-only функционально
прошёл 6/6; подготовленная версия также выполнила native transfer и 6/6.
Однако оба пропустили чтение общего work-safety перед изменением remote.
Ссылочная интеграция требовалась договорённостью о единственных владельцах;
упоминание ограничений в step3 их не загружало. В candidate-v2 заменено только
это упоминание явным pre-mutation чтением полного корневого пути; алгоритм
не скопирован. Исходный кандидат/два native raw и RED-диагноз сохранены в
../2026-11-16-execute-migrate-git-repository/. Текущий положительный сценарий
повторён до запуска полной матрицы, ресурс прочитан до мутаций.

Codex: текущие 20/20 native сценариев, по 10 common-only/common+project,
явный/неявный выбор, оба собственных ресурса и общие when-read, полный startup
до тел, unrelated без тел/API/мутаций. Два положительных сценария на режим:
реальный временный bare Git с synthetic native transfer, затем отдельно
обновление текущих потребителей уже перенесённого repo. Все четыре проходят
6/6 поведенческих проверок и независимую parent проверку; изменения ограничены
тремя текущими файлами и URL upstream. Исходные branch/HEAD/refs/staging и
прочие файлы сохранены. Synthetic API переносит identity repo-17 и метаданные,
реальный Git сохраняет refs/history и отдельные LFS fixture bytes.

Проверены transfer против самостоятельной copy/cross-host цели, незаданные
identity/свойства/метод, несовместимый/занятый получатель, destination-only
protected trunk и ref при риске --mirror, reuse старого места и исчезнувший
redirect, access denied без credentials/другого канала/grant-admin.
Пять URL-форм (HTTPS/SSH/API/raw/PR) обновляются отдельно от правильных старых
service/email и неизменяемой исторической публикации. Ноль oldteam не является
критерием корректности. Пустой diff не заменяет проверку свойств переноса.
operation-audit.json сверяет фактические Git-команды; API action log проверяет
также попытки запрещённых операций, даже если они не изменили состояние.

Два первоначальных common destination fixtures ошиблись до Codex: новый объект
создали после clone, и destination update-ref его не имел. Они не считаются
native результатами. Исправлен seed refs/объектов, preflight пройден, оба случая
повторены успешно; исходные ошибки и неуспешный batch exit сохранены.
Тестовый oracle также был излишне буквальным к форме финальной сводки:
для links-only точные revisions уже записаны в native inspect/Git outputs;
для неоднозначной identity присутствовали вопросы с русскими «источник/цель».
Полные ответы и неизменённые состояния проверены вручную; отдельные addenda
исправляют интерпретацию, не исходные записи. Native-transfer сохраняет более
сильное требование показать прямо запрошенный SHA. Нет нового изменения
кандидата, заимствования старой проверки или повышения неудачных raw.

Skill-creator и штатный plugin-eval0.1.2 до/после публикации: A100, без fail/error.
Candidate-v2: invoke425, deferred346, trigger43, total814 (stock char/4 estimates).
Пороговые значения и coverage не менялись; человеческие guides исключены.
Полные изолированные наборы:195 passed в common-only и195 в common+project;
project-only отказ до записи, повторный startup неизменен, существующий project
сохранён. Рабочий набор после публикации: ROOT_RESULT.

Внешние машинные зависимости сверены с before всех20 запусков, hashes —
external-dependencies.json. Полная доступная lazy-библиотека, startup/metadata,
собственные ресурсы, реальные per-session reads/usage и внешние fixture code/data
разделены в context-accounting.json. Обращение к topic13 карты подготовки
нужно по прямой ссылке текущей заявки; это сверка её договора, не использование
закрытой истории как новых требований. Версии: CodexCLI0.166.0, Git2.43.0,
Python3.12.15, pytest8.4.2, Node22.14.0; model/effort — CLI default, без override.

Первичные источники: [Git push --mirror](https://git-scm.com/docs/git-push),
[GitHub transfer и redirects](https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository),
[отдельный перенос LFS при duplication](https://docs.github.com/en/repositories/creating-and-managing-repositories/duplicating-a-repository).
Наблюдения вымышленного FixtureForge и его полная датированная декларация —
тестовые источники, их свойства не объявляются универсальными свойствами GitHub.
Реальные provider transfers, Git LFS client protocol, доставка webhooks,
реальный CI job, credentials/deploy keys и production не проверялись.
Проверены metadata bindings, fixture bytes и безопасный фактический file Git
ls-remote. Эти границы не подменяются успешным количеством unit tests.

Codex/common-only: проверен в документированной текущей области.
Codex/common+project: проверен в документированной текущей области.
Claude/common-only и Claude/common+project: не запускались; непроверенные.
Итоговый статус: непроверенный.
'''.replace('ROOT_RESULT',r['stdout'].strip().splitlines()[-1]+'; exit0')+'\nЗавершено: '+now+'.\n'
with report.open('x') as f:f.write(text)
p=source.parent.parent/'request.md'
with p.open('a') as f:f.write('\n## Execution — результат текущего исполнения\n\nStatus: completed\nResult: candidate-v2 полного comm-migrate-git-repository опубликован в canonical/.agents/.claude;15 файлов равны. Codex20/20, A100, оба режима195/195, рабочий набор195 passed.\nReason: договор/текущие обязательные проверки выполнены; исходный when-read gap исправлен и повторно проверен, неудачные/невалидные исходные raw сохранены.\nReport: ../../testing/evidence/'+out.name+'/2026-11-16-report.md\nUpdated: '+now+'\nCodex/common-only: verified (documented current scope)\nCodex/common+project: verified (documented current scope)\nClaude/common-only: not run; unverified\nClaude/common+project: not run; unverified\nOverall: unverified\n')
for filename in ['publish.py','close.py']:shutil.copyfile(w/filename,out/('driver-'+filename))
g.save(out/'completion.json',{'source':actual,'protected_unchanged':True,'full_copies_equal':True,'completed':now,'root_suite':r['stdout'].strip().splitlines()[-1]});print('Migration request completed; '+r['stdout'].strip().splitlines()[-1])
