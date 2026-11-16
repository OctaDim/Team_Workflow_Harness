import json,hashlib,subprocess,os
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
repo=Path('/home/octadim/MyProjects/Team_Workflow_Harness');out=repo/'harness/common/testing/evidence/2026-11-15-execute-create-git-branch';request=repo/'harness/common/inbox/2026-11-14-04-create-git-branch';source=request/'candidate/comm-create-git-branch';review=json.loads((out/'native-review-v1.json').read_text());assert review['Codex']=='passed' and len(review['case_results'])==18;assert json.loads((out/'publication.json').read_text())['full_copies_equal']
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1');r=subprocess.run(['/tmp/harness-inbox-20261113-venv/bin/python','-m','pytest','-q'],cwd=repo,env=env,capture_output=True,text=True,timeout=300)
with (out/'postpublication-pytest.json').open('x') as f:json.dump({'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr},f,ensure_ascii=False,indent=2)
assert r.returncode==0,r.stdout+r.stderr
now=datetime.now(ZoneInfo('Europe/Minsk'));date=now.date().isoformat();sha=hashlib.sha256((source/'SKILL.md').read_bytes()).hexdigest();table='\n'.join('| '+row['kind']+' | '+row['mode']+'/'+row['case']+' | passed |' for row in review['case_results'])
report=f'''# Исполнение заявки 4/8: создание Git-ветки

Создано: {now.isoformat()}. Candidate без изменений, SHA256 SKILL.md `{sha}`.
Постоянный результат: полный comm-create-git-branch в canonical/.agents/.claude, 12 обычных файлов с равными наборами/байтами. Новые always-loaded правила, root entrypoints и Git-коммиты рабочего репозитория не создавались.

Процедура создаёт новую независимую ветку от свежего именованного remote integration SHA, а не unfinished HEAD; имя берётся из effective Git email local part и смысла результата. Общие work-safety/base-state правила остаются владельцам заявок 2/3, которые опубликованы и проверены до этой заявки. Отсутствие тикета/Linear не блокирует создание. Коллизии, неизвестный/недопустимый префикс, гонка и host failure требуют остановки; commit/push/PR не включаются автоматически.

## RED и финальная приёмка

Без нового владельца обе baseline-сессии сохранили данные и использовали свежую основу, но создали agent-summary-tool и feat/agent-summary-tool, без требуемого email-префикса. Candidate дал branch.actor/add-agent-summary-tool при явном/неявном выборе в обоих режимах. Это сравнение нового naming-контракта, не утверждение, что прежняя политика уже запрещала baseline-имена.

Финальный Codex: 18/18. CLI 0.166.0, default model/effort без override; модель в turn events не раскрыта. Bwrap держит реальный workspace read-only; эффекты только в одноразовых Git-репозиториях. Каждый сценарий проходит START/rules/INDEX и human-exclusion отдельно. Общие и собственный ресурсы реально читаются; unrelated не загружает тело/ресурс нового владельца.

Положительные сценарии создают отдельный worktree. Проверены реальный свежий local-file remote central/integration/current, отставшие local/tracking refs, полный source SHA, branch prefix и literal check-ref-format, HEAD нового worktree на source SHA, сохранность исходных файлов/ветки/индекса/конфигурации/remote refs. Нет реализации, новых коммитов, push/PR или обновления local integration.

Негативные сценарии: local+remote collision и remote-only collision ждут выбора вместо автосуффикса; invalid/missing prefix спрашивают пользователя. Реальная гонка вставляет чужой ref непосредственно перед Git creation: чужой SHA сохранён, одна попытка, force/retry нет. Host proxy отклоняет создание до эффекта: новая ветка не заявляется как созданная, одна попытка без обхода.

| Сценарий | Режим/вызов | Результат |
|---|---|---|
{table}

## Фикстуры и пределы

Первые baseline-v1 невалидны как naming-проверка: bind-mounted proxy вычислял __file__=/usr/bin/git и искал неверный audit path. Raw сохранены; модели остановились безопасно. Исправленный proxy содержит конкретный isolated path; отдельный preflight проверяет реальный Git read/create, race и host failure до повторных моделей.

Удаление user.email само по себе не доказывало отсутствия effective identity: git var GIT_AUTHOR_IDENT вычислял prefix=octadim. Оба исходных missing-prefix raw сохранены, первоначальная неверная test assumption не повышена до pass. Финальная fixture-v3 включает user.useConfigOnly, нейтральный HOME и отсутствие identity env; отдельный probe подтвердил exit 128, затем оба native режима корректно запросили префикс. Кандидат не менялся. Это исправление входа теста, не ослабление проверок.

Сценарии локальные, не проверяют live hosting/API. Host proxy и запрет чтения его реализации — часть теста; инструкции не объявлены ОС-механизмом безопасности. Source, конфиги, proxy preflights, raw, baseline/final reviews и скрипты сохраняются отдельно.

## Проверки и контекст

Skill-creator + plugin-eval start/analyze/explain-budget: passed, A/100, без fail/error. Static trigger/invoke/deferred/total=41/365/222/628; baseline нового владельца отсутствовал (0). SKILL 181 слов, 1459 Unicode символов. Сумма собственных ресурсов 222 static tokens, штатные thresholds не менялись. Общие зависимости/доступная lazy-библиотека и startup guards учтены отдельно в context-accounting.json; actual-external-reads и native-review сохраняют фактические полные чтения, размеры output и исходную session usage. Static char/4 — оценка, не измерение цены скилла.

Оба prepublication режима: по 168 тестов; project-only отказал до записи; синхронизация стабильна. Checked publisher сверил exact source, 18 current native verdict, suites, dependency hashes и защищённые snapshots до копирования. После публикации: {r.stdout.strip().splitlines()[-1]}.

Codex/common-only: проверенный в указанном scope.
Codex/common+project: проверенный в указанном scope.
Claude/common-only и common+project: непроверенный — не запускался.
Итоговый статус: непроверенный.
'''
with (out/f'{date}-report.md').open('x') as f:f.write(report)
with (request/'request.md').open('a') as f:f.write(f'''\n## Execution — завершение\n\nStatus: completed\nResult: candidate опубликован canonical/.agents/.claude; native Codex 18/18, formal/install/full-suite проверки пройдены.\nUpdated: {now.isoformat()}\nCodex/common-only: проверенный в scope отчёта.\nCodex/common+project: проверенный в scope отчёта.\nClaude/common-only: непроверенный — не запускался.\nClaude/common+project: непроверенный — не запускался.\nИтоговый статус: непроверенный.\nОтчёт: [permanent report](../../testing/evidence/{out.name}/{date}-report.md).\n''')
print(json.dumps({'status':'completed','report':str(out/f'{date}-report.md'),'tests':r.stdout.strip().splitlines()[-1],'sha256':sha},ensure_ascii=False))
