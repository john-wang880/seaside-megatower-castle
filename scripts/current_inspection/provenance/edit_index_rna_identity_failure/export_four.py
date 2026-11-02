import pathlib,hashlib,json,subprocess,os
P=pathlib.Path(__file__).resolve().parent;R=P.parents[1];tool=P/'staged_tool';source=R/'work/v028/castle_v028.blend';blender=R.parent/'tools/blender-5.2.3-linux-x64/blender';out=P/'viewers 中文';out.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inventory():return {str(p.relative_to(tool)):sha(p) for p in sorted(tool.rglob('*')) if p.is_file()}
before=inventory();sourcehash=sha(source);exe=sha(blender);rows=[]
(P/'EXPORT_INPUTS.json').write_text(json.dumps({'tool':before,'source':sourcehash,'blender':exe},indent=2))
for label,args in [('defaultOFF',[]),('indexOFF',['--editing-index']),('indexHIGH',['--editing-index','--tree-mode','HIGH']),('indexLOW',['--editing-index','--tree-mode','LOW'])]:
 cmd=[str(blender),'-b','--factory-startup','-t','8','--disable-autoexec','--python-exit-code','1','--python-expr','import sys;sys.dont_write_bytecode=True','--python',str(tool/'export_inspection.py'),'--','--repository-root',str(R),'--source',str(source),'--output',str(out/(label+'.blend')),'--report',str(out/(label+'.json')),*args]
 with open(out/(label+'.log'),'w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
 if r.returncode:raise RuntimeError('export failed '+label)
 receipt=json.load(open(out/(label+'.json')));assert receipt['source_unchanged'] and receipt['bookmark_count']==18
 rows.append({'case':label,'model':str(out/(label+'.blend')),'receipt':str(out/(label+'.json')),'sha256':sha(out/(label+'.blend'))});print(label,'PASS',flush=True)
assert before==inventory() and sha(source)==sourcehash and sha(blender)==exe
(P/'EXPORTS.json').write_text(json.dumps({'status':'PASS','exports':rows,'source_unchanged':True,'tool_unchanged':True,'blender_unchanged':True,'independent_qa':'pending'},indent=2))
