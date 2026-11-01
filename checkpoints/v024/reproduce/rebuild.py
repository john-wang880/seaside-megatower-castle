"""Guarded wrapper around the byte-exact executed builder; no runtime rewriting."""
import argparse,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE_SHA='c4b1dda3b8f70e4c8cb0171834b2150b6d7610f6296847362fd204b2dfa7ad51'
SOURCE_BYTES=47628324
PINNED={'SCOPE.json':'8d4e87215c252932bb167995bd67df34751e1d4a074c80f2b5690256d6876b16','plan.json':'b858a3cf10451e0b67daa4214b6d830c2ab5dc51ffc787a5516a295855fc5e75','scripts/build.py':'45fbe7db124f1395c8da0abed6643434c17fd7a63faba2efe703aa8315f73066','scripts/snapshot_support.py':'ef8b575c70fbb394bfd76cba93b97bc07a6c03abdfe7f4eb2752cfd236be6249'}
class GuardError(ValueError):pass
def need(ok,msg):
 if not ok:raise GuardError(msg)
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def safe(value,exists=False):
 p=Path(value).expanduser().absolute();need('..'not in p.parts and all(not x.is_symlink()for x in[p,*p.parents])and p.resolve()==p,'Aliased or symlink path')
 if exists:need(p.is_file(),'Missing input file')
 else:need(p.parent.is_dir()and not os.path.lexists(p),'Output/report exists or parent missing')
 return p
def validate_scope(plan,scope):
 need(plan['schema']=='v024-evaluated-union-v1'and plan['source_sha256']==SOURCE_SHA and plan['source_bytes']==SOURCE_BYTES,'Wrong plan source/schema')
 need(plan['object']=='V008 | gallery with genuine eastern approach portal'and plan['material']=='Citadel • aged gallery grey','Wrong object/material')
 need([x['evaluated']['seed']for x in plan['mapping']]==[56,80,104,128,152,176]and[x['raw']['seed']for x in plan['mapping']]==[16,24,32,40,48,56],'Wrong six-component mapping')
 need([i for x in plan['mapping']for i in x['raw']['indices']]==list(range(16,64)),'Wrong48rawvertex scope')
 need([i for x in plan['mapping']for i in x['evaluated']['indices']]==list(range(56,200)),'Wrong144evaluatedvertex scope')
 need(all(x['evaluated']['vertices']==24 and x['evaluated']['faces']==26 and x['evaluated']['materials']==[0]and x['raw']['materials']==[0]for x in plan['mapping']),'Wrong chamfer topology/material IDs')
 need(scope['source_sha256']==SOURCE_SHA and scope['selected_evaluated_seeds']==[56,80,104,128,152,176]and scope['selected_raw_seeds']==[16,24,32,40,48,56]and scope['raw_vertex_indices']==list(range(16,64)),'Independent scope mismatch')
 need(plan['deferred_components']==20 and plan['tolerances']=={'strict_crossing':1e-7,'positive_volume':1e-9},'Scope/tolerance changed')
def preflight(source,output,report,root=ROOT):
 need(not sys.flags.optimize,'Optimized Python is refused')
 for name,h in PINNED.items():need(sha(safe(root/name,True))==h,'Runtime/plan/scope hash mismatch: '+name)
 plan=json.loads((root/'plan.json').read_text());scope=json.loads((root/'SCOPE.json').read_text());validate_scope(plan,scope)
 src=safe(source,True);out=safe(output);rep=safe(report);need(len({src,out,rep})==3 and out.suffix.lower()=='.blend'and rep.suffix.lower()=='.json','Wrong output roles/aliases')
 need(src.stat().st_size==SOURCE_BYTES,'Wrong source bytes');need(sha(src)==SOURCE_SHA,'Wrong source hash')
 return src,out,rep

def publish(pairs):
 made=[]
 try:
  for tmp,dest in pairs:
   safe(dest);owned=os.stat(tmp);os.link(tmp,dest);made.append((dest,owned))
 except BaseException:
  for dest,owned in reversed(made):
   try:
    actual=os.lstat(dest)
    if(actual.st_dev,actual.st_ino)==(owned.st_dev,owned.st_ino):os.unlink(dest)
   except FileNotFoundError:pass
  raise

def run(source,output,report,blender):
 src,out,rep=preflight(source,output,report);exe=safe(blender,True);wrapper_sha=sha(__file__)
 # Builder can publish only inside this private fresh directory, never user outputs.
 with tempfile.TemporaryDirectory(prefix='.v024-rebuild-',dir=out.parent)as stage:
  stage=Path(stage);model=stage/'candidate.blend';internal=stage/'build.json'
  cmd=[str(exe),'--background','--factory-startup','--disable-autoexec','--python-exit-code','1','--python',str(ROOT/'scripts/build.py'),'--','--source',str(src),'--plan',str(ROOT/'plan.json'),'--output',str(model),'--report',str(internal)]
  result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  need(result.returncode==0,'Builder failed before final publication:\n'+result.stdout[-12000:])
  preflight(source,output,report);need(sha(__file__)==wrapper_sha,'Wrapper changed during build')
  build=json.loads(internal.read_text());need(build['candidate_sha256']==sha(model)and build['hashes']['source']==SOURCE_SHA and build['hashes']['builder']==PINNED['scripts/build.py']and build['hashes']['helper']==PINNED['scripts/snapshot_support.py']and build['hashes']['plan']==PINNED['plan.json'],'Internal receipt mismatch')
  receipt={'status':'Fresh guarded rebuild; independent semantic equivalence to accepted candidate still required','source_sha256':SOURCE_SHA,'source_unchanged':True,'wrapper_sha256':wrapper_sha,'pinned_runtime':PINNED,'output_sha256':sha(model),'output_bytes':model.stat().st_size,'output':str(out),'command':cmd,'builder_report':build,'rendered':False,'source_saved':False,'publication':'Exclusive hardlinks, temp inode captured before link; no fallback overwrite'}
  fd,t=tempfile.mkstemp(prefix='.v024-report-',suffix='.json',dir=rep.parent);os.close(fd);tmp_report=Path(t)
  try:
   tmp_report.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
   preflight(source,output,report);need(sha(__file__)==wrapper_sha,'Wrapper changed before publication')
   for p in[model,tmp_report]:
    with open(p,'rb')as f:os.fsync(f.fileno())
   publish([(model,out),(tmp_report,rep)])
  finally:tmp_report.unlink(missing_ok=True)
 return receipt

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ['source','output','report']:p.add_argument('--'+key,required=True)
 p.add_argument('--blender');p.add_argument('--preflight-only',action='store_true');a=p.parse_args()
 if a.preflight_only:preflight(a.source,a.output,a.report);print('Preflight PASS; no Blender launched')
 else:
  need(a.blender is not None,'Explicit existing Blender executable required');r=run(a.source,a.output,a.report,a.blender);print(json.dumps({k:r[k]for k in ['output','output_sha256','source_unchanged']}))
if __name__=='__main__':main()
