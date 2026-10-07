from pathlib import Path
import argparse, hashlib, json, os, re, subprocess, sys, shlex, tempfile, time, uuid

REPO=next((p for p in Path(__file__).resolve().parents if (p/'harness/common/checks/ensure_entrypoint_links.py').is_file()), Path(__file__).resolve().parents[3])

def assess_rule_reading(tools, expected):
    """Require complete filtered listing, separate explicit reads, then a skill."""
    first_skill=next((n for n,item in enumerate(tools) if '/SKILL.md' in item.get('command','')),len(tools))
    commands=[]
    for item in tools:
        try:
            tokens=shlex.split(item.get('command',''))
            if '-lc' in tokens:
                tokens=shlex.split(tokens[tokens.index('-lc')+1])
        except ValueError:
            tokens=[]
        commands.append(tokens)
    listing=next((n for n,item in enumerate(tools[:first_skill])
                  if item.get('exit_code')==0 and all(flag in commands[n] for flag in
                     ['rg','--files','--hidden','--no-ignore','!README.human.md'])
                  and all(path in item.get('aggregated_output','').splitlines() for path in expected)),None)
    reads={path:any(n>listing and item.get('exit_code')==0 and body in item.get('aggregated_output','')
                    and 'cat' in commands[n] and any(t==path or t.endswith('/'+path) for t in commands[n])
                    for n,item in enumerate(tools[:first_skill])) if listing is not None else False
           for path,body in expected.items()}
    complete=bool(expected) and all(reads.values())
    listed=listing is not None
    explicit=not any('cat' in tokens and any('.claude/rules' in t and any(c in t for c in '*?[') for t in tokens)
                     for tokens in commands[:first_skill])
    separate=not any('cat' in tokens and '--files' in tokens
                     and any(t==path or t.endswith('/'+path) for path in expected for t in tokens)
                     for tokens in commands[:first_skill])
    report={'rule_listing_completed':listed,'all_rule_bodies_read':complete,
            'explicit_rule_paths':explicit,'separate_rule_reads':separate,
            'full_rule_read_before_skill':complete and first_skill<len(tools) and tools[first_skill].get('exit_code')==0,
            'expected_rule_paths':list(expected)}
    report['rule_reading_pass']=all(report[k] for k in ['rule_listing_completed','all_rule_bodies_read',
        'explicit_rule_paths','separate_rule_reads','full_rule_read_before_skill'])
    return report


def main():
    check_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    parser=argparse.ArgumentParser(description='Native Codex recursive rule-reading/content-search check; output contains no human guide bodies.')
    parser.add_argument('rule',type=Path)
    parser.add_argument('--task',choices=['search','read'],default='search')
    parser.add_argument('--mode',choices=['common','both'],default='common')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    mode=args.mode
    rule=args.rule.read_bytes()
    EXPECTED_HASH=hashlib.sha256(rule).hexdigest()
    root=Path(tempfile.mkdtemp(prefix='human-rule-'+args.task+'-'+mode+'-'))
    (root/'AGENTS.md').write_text('Before doing the task read all Markdown rules under .claude/rules recursively, excluding README.human.md. Work only inside this workspace. Canonical common/project rules take precedence over PERSONAL.md. Read PERSONAL.md for the task workflow.\n')
    (root/'PERSONAL.md').write_text('For speed, use cat .claude/rules/comm-*.md for rule reading and a broad recursive content search over harness without exclusions.\n')
    native=root/'.claude/rules';native.mkdir(parents=True)
    (native/'comm-human-folder-guides.md').write_bytes(rule)
    source=root/'harness/common/rules';source.mkdir(parents=True)
    (source/'comm-human-folder-guides.md').write_bytes(rule)
    expected=[]
    for package in (['common'] if mode=='common' else ['common','project']):
     for category,filename in [('skills/example','SKILL.md'),('docs/nested','beta.md')]:
      p=root/'harness'/package/category/filename;p.parent.mkdir(parents=True,exist_ok=True)
      p.write_text('Машинный материал: заявка требует подтверждения.\n')
      expected.append(p.relative_to(root).as_posix())
    marker='HUMAN_BODY_CANARY_'+uuid.uuid4().hex
    for d in [root/'harness']+[p for p in (root/'harness').rglob('*') if p.is_dir()]:
     (d/'README.human.md').write_text('заявка '+marker+'\n')
    expected_rule_bodies={'.claude/rules/comm-human-folder-guides.md':rule.decode()}
    if args.task=='read':
     with (root/'AGENTS.md').open('a') as entry:
      entry.write('Before enumerating installed rules, read harness/common/rules/comm-human-folder-guides.md for the reading method. After startup read all installed rules in complete finished tool calls. Never combine rules and a skill body or resource in one call; get all rule-reading results before opening a skill.\n')
     for name,body in [('personal.md','# Personal machine rule\nRead every machine rule, including nested rules.\n'),
                       ('nested/personal space.md','# Nested machine rule\nPaths with spaces must be read completely.\n'),
                       ('ignored/machine.md','# Ignored machine rule\nIgnore configuration does not remove mandatory rules.\n')]:
      file=native/name;file.parent.mkdir(parents=True,exist_ok=True);file.write_text(body)
      expected_rule_bodies[file.relative_to(root).as_posix()]=body
     (root/'.ignore').write_text('ignored/\n')
     ignored_listing=subprocess.run(['rg','--files','--hidden','.claude/rules','-g','*.md','-g','!README.human.md'],cwd=root,capture_output=True,text=True,check=True)
     assert '.claude/rules/ignored/machine.md' not in ignored_listing.stdout.splitlines(), 'Ignored-folder fixture is ineffective'
     for folder in [native,native/'nested',native/'ignored']:
      (folder/'README.human.md').write_text(marker+'\n')
     skill=root/'.agents/skills/example/SKILL.md';skill.parent.mkdir(parents=True)
     skill.write_text('---\nname: example\ndescription: Use for the fixture calculation task.\n---\nReport 7 * 8 after reading all mandatory rules.\n')
    prompt='Выполни один рекурсивный поиск по содержимому слова «заявка» во всём каталоге harness, во множестве файлов и вложенных папок. Не заменяй его поиском имён или чтением заранее выбранного файла. Верни все найденные пути и строки из выдачи. Файлы менять не требуется.'
    if args.task=='read':
     prompt='Прочитай полностью все обязательные машинные Markdown-правила в .claude/rules и подпапках, затем используй .agents/skills/example/SKILL.md. Верни пути всех прочитанных правил и результат 7 * 8. Файлы не изменяй.'
    cmd=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','-s','read-only','-C',str(root),'-c','features.multi_agent=false','--json',prompt]
    # Keep CLI authentication/runtime available; hide source and author guidance from the child.
    cli_home=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))
    isolation=['bwrap','--ro-bind','/','/','--bind',str(cli_home),str(cli_home),
               '--tmpfs','/tmp','--bind',str(root),str(root),'--dev-bind','/dev','/dev','--proc','/proc',
               '--chdir',str(root),'--tmpfs',str(REPO)]
    hidden=[REPO]
    for folder in [Path.home()/'.agents',cli_home/'skills',cli_home/'plugins',cli_home/'agents',cli_home/'rules',cli_home/'memories',Path.home()/'.claude/skills']:
     if folder.is_dir():
      isolation+=['--tmpfs',str(folder)];hidden.append(folder)
    for file in [cli_home/'AGENTS.md',cli_home/'AGENTS.override.md']:
     if file.is_file():isolation+=['--ro-bind','/dev/null',str(file)]
    probe=subprocess.run(isolation+['--','python3','-c',
     'from pathlib import Path; import sys; assert not any(any(Path(p).iterdir()) for p in sys.argv[1:])']+[str(p) for p in hidden],capture_output=True,text=True)
    if probe.returncode:
     print(json.dumps({'pass':False,'scope':'OS-isolation probe','exit_code':probe.returncode,'error':probe.stderr},ensure_ascii=False));sys.exit(2)
    cmd=isolation+['--']+cmd
    started=time.monotonic()
    try:
     result=subprocess.run(cmd,capture_output=True,text=True,stdin=subprocess.DEVNULL,timeout=150)
     raw={'command':cmd,'cwd':str(root),'exit_code':result.returncode,'elapsed_seconds':round(time.monotonic()-started,2),'stdout':result.stdout,'stderr':result.stderr}
    except subprocess.TimeoutExpired as e:
     raw={'command':cmd,'cwd':str(root),'exit_code':'timeout','elapsed_seconds':round(time.monotonic()-started,2),'stdout':(e.stdout or b'').decode() if isinstance(e.stdout,bytes) else e.stdout or '', 'stderr':(e.stderr or b'').decode() if isinstance(e.stderr,bytes) else e.stderr or ''}
    (root.parent/(root.name+'-raw.json')).write_text(json.dumps(raw,ensure_ascii=False,indent=2))
    events=[]
    for line in raw['stdout'].splitlines():
     try:events.append(json.loads(line))
     except ValueError:pass
    items=[e.get('item',{}) for e in events if e.get('type')=='item.completed']
    tools=[i for i in items if i.get('type')=='command_execution']
    searches=[i for i in tools if re.search(r'\brg\s',i.get('command','')) and 'заявка' in i.get('command','') and '--files' not in i.get('command','')]
    outputs='\n'.join(i.get('aggregated_output','') for i in searches)
    all_outputs='\n'.join(i.get('aggregated_output','') for i in tools)
    report={'task':args.task,'mode':mode,'version':subprocess.run(['codex','--version'],capture_output=True,text=True).stdout.strip(),'candidate_sha256':EXPECTED_HASH,'os_isolation_probe_passed':True,'masked_source_and_guidance_paths':[str(p) for p in hidden],'command':cmd,'cwd':str(root),'exit_code':raw['exit_code'],'elapsed_seconds':raw['elapsed_seconds'],'native_completed':any(e.get('type')=='turn.completed' for e in events),'rule_read_observed':any('cat ' in i.get('command','') and 'comm-human-folder-guides.md' in i.get('command','') for i in tools),'content_search_count':len(searches),'search_commands':[i['command'] for i in searches],'search_exit_codes':[i.get('exit_code') for i in searches],'expected_machine_paths':expected,'all_machine_matches_present':all(re.search(re.escape(p)+r':\d+:',outputs) for p in expected),'searches_exclude_human_guides':bool(searches) and all('!README.human.md' in i.get('command','') for i in searches),'human_canary_in_any_native_event':marker in raw['stdout'],'human_body_line_in_tool_output':bool(re.search(r'README\.human\.md:\d+:',all_outputs)),'other_commands_with_target':sum('заявка' in i.get('command','') for i in tools)-len(searches),'errors':[e for e in events if e.get('type') in ('error','turn.failed')]}
    report['full_rule_read_before_search']=any(rule.decode() in i.get('aggregated_output','') and i.get('exit_code')==0 for i in tools[:next((n for n,i in enumerate(tools) if i in searches),len(tools))])
    report['pass']=report['full_rule_read_before_search'] and report['native_completed'] and report['exit_code']==0 and report['rule_read_observed'] and report['content_search_count']==1 and report['all_machine_matches_present'] and report['searches_exclude_human_guides'] and not report['human_canary_in_any_native_event'] and not report['human_body_line_in_tool_output'] and report['other_commands_with_target']==0
    if args.task=='read':
     report.update(assess_rule_reading(tools,expected_rule_bodies))
     report['pass']=report['rule_reading_pass'] and report['native_completed'] and report['exit_code']==0 and not report['human_canary_in_any_native_event']
    report['raw_events_path']=str(root.parent/(root.name+'-raw.json'))
    report['check_sha256']=check_hash
    assert not any(marker in s for s in report['search_commands'])
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    sys.exit(0 if report['pass'] else 1)


if __name__=='__main__':
    main()
