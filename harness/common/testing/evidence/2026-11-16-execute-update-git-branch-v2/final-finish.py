import json,hashlib,os,subprocess
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
w=Path(__file__).parent;loc=json.loads((w/'location-v2.json').read_text());out=Path(loc['out']);source=Path(loc['source']);repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');request=source.parent.parent;r=json.loads((out/'native-review-v1.json').read_text());assert r['Codex']=='passed' and len(r['case_results'])==20;assert json.loads((out/'readonly-command-audit.json').read_text())['passed'];assert json.loads((out/'publication.json').read_text())['full_copies_equal']
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1');p=subprocess.run(['/tmp/harness-inbox-20261113-venv/bin/python','-m','pytest','-q'],cwd=repo,env=env,capture_output=True,text=True,timeout=300)
with (out/'postpublication-pytest.json').open('x') as f:json.dump({'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr},f,ensure_ascii=False,indent=2)
assert p.returncode==0,p.stdout+p.stderr
now=datetime.now(ZoneInfo('Europe/Minsk'));date=now.date().isoformat();sha=hashlib.sha256((source/'SKILL.md').read_bytes()).hexdigest();table='\n'.join('| '+row['kind']+' | '+row['mode']+'/'+row['case']+' | passed |' for row in r['case_results'])
report=f'''# Исполнение заявки 5/8: актуализация ветки

Создано: {now.isoformat()}. Candidate-v2, SHA256 SKILL.md `{sha}`. Полный новый владелец опубликован canonical/.agents/.claude, 15 обычных файлов; наборы/байты равны. Root entrypoints, правила и project сохранены. Git-коммиты реального рабочего репозитория не создавались.

Процедура связывает сохранность работы, свежую интеграционную основу, выбор A/B и смысловую резолюцию. Повторно использует опубликованные владельцы 2/3/4 и действующих владельцев тестирования/доменных полномочий. Не предписывает универсальный merge/rebase, не разрешает менять локальную ветку во время PR-операции и не заменяет approval для SQL или protected harness.

## RED → текущая версия

Baseline без нового владельца уже сохранил API v2 + отказ от пустых строк, обновил metadata/generated и получил 8/8 GREEN в обоих режимах. Улучшение функционального поведения по этим двум baseline не заявляется. Обнаружен пробел нового output-контракта: в итоговом ответе отсутствовал old SHA. V1 добавил явную процедуру, но один implicit-ответ всё ещё пропустил old SHA при правильном результате. V1 не публиковался. V2 задаёт labeled full-SHA поля old/target/result и честные unknown/not created. Все 20 current-проверок пройдены; у шести выполненных A/B полные SHA сверены с независимым Git-состоянием.

A проверяется на свежем C: 5 behavioral failures из 8; B — на исходном B: 7 failures из 8. Это валидные RED разных рабочих основ, не import/environment failures. Новый worktree сравнивается с tracked immutable inputs; ignored pytest cache исходного дерева не требуется переносить. Само исходное дерево, staged/unstaged/untracked и файлы сохраняются полностью; чужое содержимое не копируется в результат.

## Native Codex и реальные эффекты

Codex CLI 0.166.0, default model/effort без override; модель в событиях не раскрыта. В каждом режиме отдельные ephemeral sessions: common-only с нейтральным project и common+project с сохранённым project. Полный START/rules/INDEX протокол и human-body exclusion проверены отдельно. Внешний workspace read-only через bwrap, Git и тестовые commits только во временных проектах.

B даёт ровно merge-коммит с родителями old/target, без переписывания истории и изменения других refs. A создаёт свежую ветку/worktree через владельца 4, переносит committed feature без чужих данных, даёт commit с parent=target и сохраняет исходный branch/index. У обоих совмещены переименованный API, callers, empty-input guard, version/cache/build metadata; lock пересоздан проектным generator, legacy не восстановлен. Восемь фиксированных unit/integration checks проходят на итоговом commit; tests/generator/инструкции не изменяются для green.

Commit-owner, точный установленный CE 3.38.0 и publication-data guard фактически прочитаны до commit. Completed-event audit проверяет полный green до commit; actual SHA/parents/tree/status и независимый повтор восьми тестов подтверждают эффект. CE namespace в изолированной среде связан с точным установленным body, не эмулируется plugin registry. Весь внешний body/metadata/hash и реальные чтения учтены отдельно.

Негативные cases оставляют refs/index/files/worktrees/config неизменными: unresolved A/B с dependency D и опубликованной веткой, PR read-only, foreign staging, противоречивый intent, SQL approval OPEN и неразрешённый canonical-harness diff. Completed-команды проверены на изменяющие Git-операции и явные файловые записи; итоговые snapshots неизменны. SQL inspection вправе остановиться до SQL design; keyword не принуждает к проектированию. Old one-test green не повышается до совместимости новой версии. В negative cases обновление намеренно не выполняется; старый B не объявляется GREEN.

| Сценарий | Режим/вызов | Результат |
|---|---|---|
{table}

Пределы: локальный file-protocol remote и синтетические контракты, не live hosting/deployment/реальные SQL-серверы. Инструкции не являются ОС enforcement. Полные raw, preflight, исходные verdict, current reviews, commands/usage и хэши сохранены; исторические результаты не переписаны.

## Формальные проверки и контекст

Skill-creator + plugin-eval start/analyze/explain-budget: passed, A/100 без fail/error. SKILL 190 слов; trigger/invoke/deferred/total=37/431/481/949. Baseline нового владельца отсутствовал: 0 собственного static контекста. Ресурсы 481 ниже цели 1000, штатные thresholds не менялись. Startup guards, metadata и вся доступная common lazy-библиотека — context-accounting.json; CE body отдельно — external-context.json. Actual-external-reads и native-review хранят полные фактические чтения/output sizes и исходную session usage. Char/4 и static — оценки, не точная стоимость скилла.

До публикации по 168 тестов в каждом режиме, project-only отказ до записи, стабильная синхронизация. Checked publisher сверил exact source, 20 current native verdict, read-only audit, suites, зависимости и protected snapshots до копирования. После публикации: {p.stdout.strip().splitlines()[-1]}.

Codex/common-only: проверенный в указанном scope.
Codex/common+project: проверенный в указанном scope.
Claude/common-only и common+project: непроверенный — не запускался.
Итоговый статус: непроверенный.
'''
with (out/f'{date}-report.md').open('x') as f:f.write(report)
with (request/'request.md').open('a') as f:f.write(f'''\n## Execution — завершение\n\nStatus: completed\nResult: candidate-v2 опубликован canonical/.agents/.claude; native Codex 20/20, formal/install/full-suite проверки пройдены.\nUpdated: {now.isoformat()}\nCodex/common-only: проверенный в scope отчёта.\nCodex/common+project: проверенный в scope отчёта.\nClaude/common-only: непроверенный — не запускался.\nClaude/common+project: непроверенный — не запускался.\nИтоговый статус: непроверенный.\nОтчёт: [permanent report](../../testing/evidence/{out.name}/{date}-report.md).\n''')
print(json.dumps({'status':'completed','report':str(out/f'{date}-report.md'),'tests':p.stdout.strip().splitlines()[-1],'sha256':sha},ensure_ascii=False))
