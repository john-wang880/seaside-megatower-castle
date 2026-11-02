"""Fresh archive-only four-copy export + independent editing-index QA; no renders."""
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
S='f0d135e0c6e554b5ae7c520ef9ccefc61e2a7c4abc3129eef1d3d4118bca8096';B='c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd'
def need(v,m):
 if not v:raise RuntimeError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inv(p):return {str(f.relative_to(p)):sha(f) for f in sorted(p.rglob('*')) if f.is_file()}
def verify_manifest(p):
 d=json.loads(p.read_text());d=d.get('files',d)
 for n,h in d.items():
  need(not Path(n).is_absolute() and '..'not in Path(n).parts,'Unsafe manifest path');h=h.get('sha256')if isinstance(h,dict)else h;need(sha(p.parent/n)==h,'Manifest mismatch '+n)
p=argparse.ArgumentParser()
for k in ['archive','source','baseline','blender','output-dir','payload-sha','qa-sha','commit']:p.add_argument('--'+k,required=True)
a=p.parse_args();need(not sys.flags.optimize,'Optimized Python refused');paths={k:Path(getattr(a,k)).absolute()for k in ['archive','source','baseline','blender','output_dir']}
for k,v in paths.items():need('..'not in v.parts and v.resolve()==v and all(not q.is_symlink()for q in [v,*v.parents]),'Aliased '+k)
r,s,b,exe,out=[paths[k]for k in ['archive','source','baseline','blender','output_dir']];need(r.is_dir()and s.is_file()and b.is_file()and exe.is_file(),'Missing input');need(not out.exists()and out.parent.is_dir()and not out.is_relative_to(r),'New external output required');need(sha(s)==S and sha(b)==B,'Wrong model');tool=r/'scripts/current_inspection';qa=tool/'qa/edit_index';need(sha(tool/'PUBLIC_PAYLOAD.json')==a.payload_sha and sha(qa/'FILES.json')==a.qa_sha,'Wrong frozen bundle');verify_manifest(tool/'PUBLIC_PAYLOAD.json');verify_manifest(qa/'FILES.json');before=inv(r);pins={str(s):S,str(b):B,str(exe):sha(exe)};out.mkdir();(out/'cache').mkdir();env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',XDG_CACHE_HOME=str(out/'cache'));commands=[];result={'pass':False,'commit':a.commit,'source_sha256':S,'baseline_sha256':B,'payload_sha256':a.payload_sha,'qa_manifest_sha256':a.qa_sha,'commands':commands,'rendered':False,'canonical_saved':False}
def run(name,args):
 with (out/(name+'.log')).open('x')as f:z=subprocess.run(args,cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT)
 commands.append({'name':name,'argv':args,'returncode':z.returncode});need(z.returncode==0,'Failed '+name);need(inv(r)==before and all(sha(k)==v for k,v in pins.items()),'Input drift')
try:
 for mode in ['default','off','high','low']:
  cmd=[str(exe),'-b','--factory-startup','-t','8','--disable-autoexec','--python-exit-code','1','--python-expr','import sys;sys.dont_write_bytecode=True','--python',str(tool/'export_inspection.py'),'--','--repository-root',str(r),'--source',str(s),'--output',str(out/(mode+'.blend')),'--report',str(out/(mode+'.json'))]
  if mode!='default':cmd+=['--editing-index']
  if mode in ['high','low']:cmd+=['--tree-mode',mode.upper()]
  run('export_'+mode,cmd);q=json.loads((out/(mode+'.json')).read_text());need(q['source_unchanged']and q['bookmark_count']==18 and q['editing_index']==(mode!='default')and q['output_sha256']==sha(out/(mode+'.blend')),'Export receipt mismatch')
 cmd=[sys.executable,'-B',str(qa/'run_qa.py'),'--source',str(s),'--baseline',str(b),'--tool',str(tool),'--blender',str(exe),'--output-dir',str(out/'qa')]
 for mode in ['default','off','high','low']:cmd+=['--'+mode,str(out/(mode+'.blend')),'--'+mode+'-receipt',str(out/(mode+'.json'))]
 run('independent_qa',cmd);q=json.loads((out/'qa/SUMMARY.json').read_text());need(q['pass']and q['all_inputs_unchanged']and q['native_calls']==3,'QA summary failed');result.update(pass_=True,qa_summary_sha256=sha(out/'qa/SUMMARY.json'),archive_file_count=len(before),viewer_sha256={k:sha(out/(k+'.blend'))for k in ['default','off','high','low']});result['pass']=result.pop('pass_')
finally:
 result['archive_unchanged']=inv(r)==before;result['input_models_executable_unchanged']=all(sha(k)==v for k,v in pins.items());result['pass']=result['pass']and result['archive_unchanged']and result['input_models_executable_unchanged'];(out/'REMOTE_SUMMARY.json').write_text(json.dumps(result,indent=2)+'\n')
print('REMOTE EDITING INDEX PASS')
