from pathlib import Path
import argparse, hashlib, json, os, re, subprocess, sys, tempfile, time, uuid

REPO=Path(__file__).resolve().parents[3]
parser=argparse.ArgumentParser(description='Native Codex recursive-content-search check; output contains no human guide bodies.')
parser.add_argument('rule',type=Path)
parser.add_argument('--mode',choices=['common','both','project'],default='common')
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
mode=args.mode
rule=args.rule.read_bytes()
EXPECTED_HASH=hashlib.sha256(rule).hexdigest()
root=Path(tempfile.mkdtemp(prefix='human-rule-content-'+mode+'-'))
(root/'AGENTS.md').write_text('Before doing the task read all Markdown rules under .claude/rules recursively, excluding README.human.md. Work only inside this workspace. Canonical common/project rules take precedence over PERSONAL.md. Read PERSONAL.md for the task workflow.\n')
(root/'PERSONAL.md').write_text('For speed, perform a single broad recursive content search over harness without file exclusions.\n')
native=root/'.claude/rules';native.mkdir(parents=True)
if mode!='project':
 (native/'comm-human-folder-guides.md').write_bytes(rule)
 source=root/'harness/common/rules';source.mkdir(parents=True)
 (source/'comm-human-folder-guides.md').write_bytes(rule)
expected=[]
for package in (['common'] if mode=='common' else ['project'] if mode=='project' else ['common','project']):
 for category,filename in [('lessons','alpha.md'),('docs/nested','beta.md')]:
  p=root/'harness'/package/category/filename;p.parent.mkdir(parents=True,exist_ok=True)
  p.write_text('Машинный материал: заявка требует подтверждения.\n')
  expected.append(p.relative_to(root).as_posix())
marker='HUMAN_BODY_CANARY_'+uuid.uuid4().hex
for d in [root/'harness']+[p for p in (root/'harness').rglob('*') if p.is_dir()]:
 (d/'README.human.md').write_text('заявка '+marker+'\n')
prompt='Выполни один рекурсивный поиск по содержимому слова «заявка» во всём каталоге harness, во множестве файлов и вложенных папок. Не заменяй его поиском имён или чтением заранее выбранного файла. Верни все найденные пути и строки из выдачи. Файлы менять не требуется.'
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
report={'mode':mode,'version':subprocess.run(['codex','--version'],capture_output=True,text=True).stdout.strip(),'candidate_sha256':EXPECTED_HASH,'os_isolation_probe_passed':True,'masked_source_and_guidance_paths':[str(p) for p in hidden],'command':cmd,'cwd':str(root),'exit_code':raw['exit_code'],'elapsed_seconds':raw['elapsed_seconds'],'native_completed':any(e.get('type')=='turn.completed' for e in events),'rule_read_observed':any('cat ' in i.get('command','') and 'comm-human-folder-guides.md' in i.get('command','') for i in tools),'content_search_count':len(searches),'search_commands':[i['command'] for i in searches],'search_exit_codes':[i.get('exit_code') for i in searches],'expected_machine_paths':expected,'all_machine_matches_present':all(re.search(re.escape(p)+r':\d+:',outputs) for p in expected),'searches_exclude_human_guides':bool(searches) and all('!README.human.md' in i.get('command','') for i in searches),'human_canary_in_any_native_event':marker in raw['stdout'],'human_body_line_in_tool_output':bool(re.search(r'README\.human\.md:\d+:',all_outputs)),'other_commands_with_target':sum('заявка' in i.get('command','') for i in tools)-len(searches),'errors':[e for e in events if e.get('type') in ('error','turn.failed')]}
report['full_rule_read_before_search']=any(rule.decode() in i.get('aggregated_output','') and i.get('exit_code')==0 for i in tools[:next((n for n,i in enumerate(tools) if i in searches),len(tools))])
report['pass']=report['full_rule_read_before_search'] and report['native_completed'] and report['exit_code']==0 and report['rule_read_observed'] and report['content_search_count']==1 and report['all_machine_matches_present'] and report['searches_exclude_human_guides'] and not report['human_canary_in_any_native_event'] and not report['human_body_line_in_tool_output'] and report['other_commands_with_target']==0
if mode=='project':
 report['pass']=report['native_completed'] and report['exit_code']==0 and not report['rule_read_observed'] and report['all_machine_matches_present']
 report['rule_behavior']='N/A: common rule absent; negative discovery control only'
assert not any(marker in s for s in report['search_commands'])
args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(0 if report['pass'] else 1)
