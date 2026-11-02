"""Explicit fresh-archive v028 OFF/HIGH/LOW export plus existing public QA."""
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
SOURCE='f0d135e0c6e554b5ae7c520ef9ccefc61e2a7c4abc3129eef1d3d4118bca8096'
BASE='c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd'
PAYLOAD='22536aeb9e39ea74c2e1d3a3afbd075ceca1450ccc510016904cf9fbbdadc0f8'
def need(v,m):
 if not v:raise RuntimeError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def path(v):
 p=Path(v).expanduser().absolute();need('..'not in p.parts and p.resolve()==p and all(not q.is_symlink()for q in[p,*p.parents]),'Aliased path');return p
def inventory(root):
 result={}
 for p in sorted(root.rglob('*')):
  need(not p.is_symlink(),'Archive symlink');need('__pycache__'not in p.parts and p.suffix!='.pyc','Archive cache')
  if p.is_file():result[str(p.relative_to(root))]=sha(p)
 return result
def manifest(p):
 d=json.loads(p.read_text());need(all(not Path(n).is_absolute()and'..'not in Path(n).parts and sha(p.parent/n)==h for n,h in d.items()),'Manifest mismatch '+str(p))
def main():
 need(not sys.flags.optimize,'Optimized Python refused')
 ap=argparse.ArgumentParser()
 for k in ['archive','source','baseline','blender','output-dir']:ap.add_argument('--'+k,required=True)
 a=ap.parse_args();archive,source,baseline,blender,out=[path(getattr(a,k))for k in ['archive','source','baseline','blender','output_dir']]
 need(archive.is_dir()and source.is_file()and baseline.is_file()and blender.is_file(),'Missing input');need(not os.path.lexists(out)and out.parent.is_dir()and not out.is_relative_to(archive),'New external output required')
 need(sha(source)==SOURCE and sha(baseline)==BASE,'Model hash mismatch');tool=archive/'scripts/current_inspection';need(sha(tool/'PUBLIC_PAYLOAD.json')==PAYLOAD,'Unreviewed public payload');manifest(tool/'PUBLIC_PAYLOAD.json');manifest(tool/'qa/FILES.json')
 before=inventory(archive);pins={str(source):SOURCE,str(baseline):BASE,str(blender):sha(blender),str(Path(__file__).resolve()):sha(Path(__file__))};out.mkdir();env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');commands=[]
 def run(name,cmd):
  with(out/(name+'.log')).open('x')as f:r=subprocess.run(cmd,cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT,check=False)
  commands.append({'name':name,'argv':cmd,'returncode':r.returncode});need(r.returncode==0,'Failed '+name)
 result={'pass':False,'archive_inventory':before,'input_sha256':pins,'commands':commands,'rendered':False,'source_saved':False}
 try:
  for mode in ['OFF','HIGH','LOW']:
   cmd=[str(blender),'-b','--factory-startup','-t','8','--disable-autoexec','--python-exit-code','1','--python-expr','import sys;sys.dont_write_bytecode=True','--python',str(tool/'export_inspection.py'),'--','--repository-root',str(archive),'--source',str(source),'--output',str(out/(mode+'.blend')),'--report',str(out/(mode+'.json'))]
   if mode!='OFF':cmd+=['--tree-mode',mode]
   run('export_'+mode,cmd);r=json.loads((out/(mode+'.json')).read_text());need(r['source_sha256']==SOURCE and r['source_unchanged']and r['bookmark_count']==18 and r['added_cameras']==17 and r['output_sha256']==sha(out/(mode+'.blend')),'Export receipt mismatch')
  cmd=[sys.executable,'-B',str(tool/'qa/run_qa.py'),'--source',str(source),'--baseline',str(baseline),'--tool',str(tool),'--blender',str(blender),'--output-dir',str(out/'qa')]
  for mode in ['off','high','low']:cmd+=['--'+mode,str(out/(mode.upper()+'.blend')),'--'+mode+'-receipt',str(out/(mode.upper()+'.json'))]
  run('public_qa',cmd);s=json.loads((out/'qa/SUMMARY.json').read_text());m=json.loads((out/'qa/modes.json').read_text());need(s['pass']and s['all_inputs_unchanged']and m['pass']and len(m['negatives'])==27,'QA JSON gate')
  need(all(v['category_count']==13 and v['reopen_and_18_bookmark_interleaving']for v in m['modes'].values()),'Mode/bookmark gate')
  result.update(pass_=True,viewer_sha256={k:sha(out/(k+'.blend'))for k in ['OFF','HIGH','LOW']},qa_summary_sha256=sha(out/'qa/SUMMARY.json'),qa_modes_sha256=sha(out/'qa/modes.json'));result['pass']=result.pop('pass_')
 finally:
  result['all_archive_files_unchanged']=before==inventory(archive);result['all_inputs_unchanged']=all(sha(p)==h for p,h in pins.items())
  if not(result['all_archive_files_unchanged']and result['all_inputs_unchanged']):result['pass']=False
  with(out/'REMOTE_INSPECTION.json').open('x')as f:json.dump(result,f,indent=2)
  need(result['all_archive_files_unchanged']and result['all_inputs_unchanged'],'Input mutation')
 print('REMOTE V028 INSPECTION PASS')
if __name__=='__main__':main()
