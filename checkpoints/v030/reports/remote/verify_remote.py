import os,sys,json,hashlib,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent;A=R/'repo';T=A/'scripts/current_inspection';Q=T/'qa/v030_current';M=R/'models';B=Path('/workspace/scratch/8bdb2666bb6b/tools/blender-5.2.3-linux-x64/blender');S=M/'castle_v029.blend';C=M/'castle_v030.blend';BASE=R.parent/'v028_remote_historical_v018/castle_v018.blend'
def need(v,m):
 if not v:raise RuntimeError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inv(p):return {str(x.relative_to(p)):sha(x)for x in sorted(p.rglob('*'))if x.is_file()}
need(not sys.flags.optimize,'No -O');need(sha(S)=='4f838529d32cbf6a0314cc0a23b3dd1703b73d80c5db146fb4d323697b882df5'and sha(C)=='9f020b7ec6eda309d674653598b169f65ba5dc1d1f194ffa31323f6393feda35'and sha(BASE)=='c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd','Exact restored inputs');before=inv(A);pins={str(x):sha(x)for x in [S,C,BASE]};(R/'QA_INPUTS.json').write_text(json.dumps({'archive':before,'models':pins},indent=2)+'\n');env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',XDG_CACHE_HOME=str(R/'cache'),INSPECTION_QA_TOOL=str(T));env.pop('PYTHONOPTIMIZE',None);commands=[]
def run(name,cmd,cwd=R):
 commands.append({'name':name,'command':[str(x)for x in cmd],'cwd':str(cwd)})
 with (R/(name+'.log')).open('xb')as log:p=subprocess.run(commands[-1]['command'],cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT)
 need(p.returncode==0,'Failed '+name+' exit '+str(p.returncode));print(name+' PASS',flush=True)
re=R/'rebuilt';re.mkdir();run('qa_rebuild',[B,'--background','--factory-startup','--disable-autoexec','--threads','4','--python-exit-code','1','--python-expr','import sys; sys.dont_write_bytecode=True','--python',A/'checkpoints/v030/reproduce/build_fittings.py','--','--source',S,'--output',re/'rebuilt.blend','--report',re/'build.json']);rebuilt_sha=sha(re/'rebuilt.blend')
run('qa_model',[sys.executable,'-B',A/'checkpoints/v030/qa/run_qa.py','--blender',B,'--source',S,'--candidate',re/'rebuilt.blend','--candidate-sha',rebuilt_sha,'--accepted',C,'--output-dir',R/'model_qa'])
run('qa_exports',[sys.executable,'-B',Q/'export_four.py','--repository-root',A,'--tool',T,'--source',C,'--blender',B,'--output-dir',R/'viewers'])
cmd=[sys.executable,'-B',Q/'run_qa.py','--blender',B,'--tool',T,'--source',C,'--baseline',BASE,'--output-dir',R/'inspection_qa']
for mode in ['default','off','high','low']:cmd+=['--'+mode,R/'viewers'/(mode+'.blend'),'--'+mode+'-receipt',R/'viewers'/(mode+'.json')]
run('qa_inspection',cmd)
run('qa_runtime_pure',[sys.executable,'-B','-m','unittest','test_preflight','test_tree_pure','test_edit_index','test_index_panel','test_v030_catalog','-v'],T)
run('qa_independent_pure',[sys.executable,'-B',T/'tests/test_preflight_independent.py','--tool',T,'--source',C,'-v'])
for name in ['model_qa','inspection_qa']:need(json.loads((R/name/'SUMMARY.json').read_text())['pass']is True,name+' JSON')
need(inv(A)==before,'Archive changed');need(all(sha(x)==h for x,h in pins.items()),'Input model changed');need('Ran 47 tests'in(R/'qa_runtime_pure.log').read_text(),'Expected47 current tests');need('Ran 24 tests'in(R/'qa_independent_pure.log').read_text(),'Expected24 independent tests')
summary={'pass':True,'remote_commit':'facb336b3bec7c36608f06ab9788ca06eda3257b','archive_inventory_unchanged':True,'models_unchanged':True,'rebuilt_sha256':rebuilt_sha,'model_sha256':pins,'model_summary_sha256':sha(R/'model_qa/SUMMARY.json'),'inspection_summary_sha256':sha(R/'inspection_qa/SUMMARY.json'),'model_bundle_sha256':sha(A/'checkpoints/v030/qa/FILES.json'),'inspection_bundle_sha256':sha(Q/'FILES.json'),'native_calls':10,'pure_tests':{'current':47,'independent':24,'wrapper':13},'commands':commands,'rendered':False};(R/'REMOTE_QA_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print('REMOTE FULL QA PASS',flush=True)
