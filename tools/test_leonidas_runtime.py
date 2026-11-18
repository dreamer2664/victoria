"""Run the exact runtime source in Luau 0.747 under a documented fake API.

This is a deterministic logic / transform unit test. It is NOT a Roblox
engine test: no Studio import, physics, Humanoid, weld replication, streaming,
network authority, frame-time or real ProximityPrompt/line-of-sight behavior.
LUAU_BIN=/path/to/luau python3 tools/test_leonidas_runtime.py
"""
from pathlib import Path
import os,sys,subprocess,json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs'/'leonidas_ii';WORK=OUT/'build';WORK.mkdir(parents=True,exist_ok=True)
runtime=ROOT/'roblox'/'leonidas_ii'/'Aurelian_Runtime.luau';data=ROOT/'roblox'/'leonidas_ii'/'Aurelian_Data.luau'
exe=os.getenv('LUAU_BIN') or shutil.which('luau') or str(Path.home()/'.cache'/'luau'/'luau')
compiler=os.getenv('LUAU_COMPILE_BIN') or shutil.which('luau-compile') or str(Path(exe).with_name('luau-compile'))
compile_rows=[]
for name in ('Aurelian_Install.luau','Aurelian_Runtime.luau','Aurelian_Data.luau','Aurelian_StudioAcceptance.luau','Aurelian_Server.server.luau','Aurelian_Client.client.luau'):
 path=ROOT/'roblox/leonidas_ii'/name;run=subprocess.run([compiler,'--null',str(path)],cwd=ROOT,text=True,capture_output=True)
 compile_rows.append(dict(file=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),exit_code=run.returncode,status='PASS' if run.returncode==0 else 'FAIL',diagnostics=run.stderr))
 print(compile_rows[-1]['status'],'COMPILE',name,flush=True)
compile_report=dict(scope='Luau compile/bytecode only; NOT Roblox API/type/engine certification.',compiler_sha256=hashlib.sha256(Path(compiler).read_bytes()).hexdigest(),runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),files=compile_rows,summary={s:sum(r['status']==s for r in compile_rows) for s in ('PASS','FAIL')})
(OUT/'LUAU_COMPILE.json').write_text(json.dumps(compile_report,indent=2)+'\n')
if compile_report['summary']['FAIL']:sys.exit(1)
source=runtime.read_text();assert ']====]' not in source
text=(ROOT/'tools'/'leonidas_runtime_harness.luau').read_text().replace('__RUNTIME_TEXT__','[====['+source+']====]')
script=WORK/'runtime_stub.luau';script.write_text(text)
result=subprocess.run([exe,str(script)],cwd=ROOT,text=True,capture_output=True)
lines=result.stdout.splitlines();rows=[]
for line in lines:
 if line.startswith('PASS '):
  name,_,detail=line[5:].partition(' · ');rows.append(dict(test=name,status='PASS',detail=detail))
report=dict(scope='Exact Luau runtime under fake Roblox API. LOGIC/TRANSFORMS ONLY; no Studio, physics, contacts, multiplayer, streaming or performance acceptance.',runtime_sha256=hashlib.sha256(runtime.read_bytes()).hexdigest(),data_sha256=hashlib.sha256(data.read_bytes()).hexdigest(),runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),harness_sha256=hashlib.sha256((ROOT/'tools/leonidas_runtime_harness.luau').read_bytes()).hexdigest(),exit_code=result.returncode,tests=rows,stdout=result.stdout,stderr=result.stderr)
(OUT/'RUNTIME_LOGIC_TESTS.json').write_text(json.dumps(report,indent=2));print(result.stdout,end='');print(result.stderr,end='',file=sys.stderr)
if result.returncode or len(rows)<30:sys.exit(result.returncode or 1)
print('Logic test report saved; live acceptance remains UNVERIFIED.')
