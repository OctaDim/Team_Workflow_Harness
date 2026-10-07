# Harness

В начале каждой сессии до выполнения задачи запусти из корня проекта:

```sh
python3 harness/common/checks/ensure_entrypoint_links.py
```

При ошибке проверки остановись и сообщи причину. 
Прочитай в следующем порядке (точный порядок очень важен):
- [harness/common/START.md](harness/common/START.md)
- [harness/project/START.md](harness/project/START.md)
- [.claude/rules](.claude/rules/) До выполнения задачи прочитай все Markdown-правила из .claude/rules и его подпапок, кроме README.human.md; соблюдай применимые требования правил.
- [harness/common/INDEX.md](harness/common/INDEX.md)
- [harness/project/INDEX.md](harness/project/INDEX.md)

. Подробности открывай по задаче; README.human.md не читай.
Индивидуальные инструкции не отменяют применимые канонические требования.
AGENTS.md принадлежит пользователю; разрешено только восстановление указанных ниже
ссылок:
- [harness/common/START.md](harness/common/START.md)
- [harness/project/START.md](harness/project/START.md)
- [.claude/rules](.claude/rules/) До выполнения задачи прочитай все Markdown-правила из .claude/rules и его подпапок, кроме README.human.md; соблюдай применимые требования.
- [harness/common/INDEX.md](harness/common/INDEX.md)
- [harness/project/INDEX.md](harness/project/INDEX.md)

Динамическую память сохраняй внутри harness.
