"""Explicitly invoked four-copy export orchestrator. Requires sole authorized native slot."""
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
if sys.flags.optimize:raise RuntimeError('Optimized Python refused')
sys.path.insert(0,str(Path(__file__).parent/'adapter'))
from compare_support import require,SOURCE_SHA
from expected_scope import validate_scope
from run_qa import clean_path,inventory
p=argparse.ArgumentParser()
for name in ('repository-root','tool','source','blender','output-dir'):p.add_argument('--'+name,required=True)
a=p.parse_args();paths={k:clean_path(v)for k,v in vars(a).items()};sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for k,v in paths.items():
 require(not any(x.is_symlink()for x in [v,*v.parents]),'Symlink refused '+k)
 if k!='output_dir':require(v.exists(),'Missing '+k)
t=paths['tool'];s=paths['source'];out=paths['output_dir'];require(not out.exists()and out.parent.is_dir(),'New output required');require(not out.is_relative_to(t)and not out.is_relative_to(s.parent),'Output must be outside immutable inputs');require(sha(s)==SOURCE_SHA,'Canonical source hash');validate_scope(json.loads((t/'catalog.json').read_text()),json.loads((t/'edit_index.json').read_text()),t);before=inventory(t);out.mkdir();rows=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',XDG_CACHE_HOME=str(out/'cache'));env.pop('PYTHONOPTIMIZE',None)
for mode in ('default','off','high','low'):
 cmd=[str(paths['blender']),'--background','--factory-startup','--disable-autoexec','--threads','4','--python-exit-code','1','--python-expr','import sys; sys.dont_write_bytecode=True','--python',str(t/'export_inspection.py'),'--','--repository-root',str(paths['repository_root']),'--source',str(s),'--output',str(out/(mode+'.blend')),'--report',str(out/(mode+'.json'))]
 if mode!='default':cmd+=['--editing-index']
 if mode in ('high','low'):cmd+=['--tree-mode',mode.upper()]
 with (out/(mode+'.log')).open('xb')as log:r=subprocess.run(cmd,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT)
 require(r.returncode==0,'Export failed '+mode);require(sha(s)==SOURCE_SHA and inventory(t)==before,'Source/tool changed');rows.append({'mode':mode,'command':cmd,'viewer_sha256':sha(out/(mode+'.blend')),'receipt_sha256':sha(out/(mode+'.json'))});print('EXPORT PASS',mode,flush=True)
(out/'EXPORTS.json').write_text(json.dumps({'pass':True,'source_sha256':SOURCE_SHA,'tool_inventory':before,'exports':rows,'tool_source_unchanged':True},indent=2)+'\n')
