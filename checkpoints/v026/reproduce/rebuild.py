"""Guarded wrapper around the byte-exact executed builder; no runtime rewriting."""
import argparse,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE_SHA='8a3590082c99a69d50d444f77165fae57fb611cf069cecda03fdf0c6c17cadd2'
SOURCE_BYTES=47663562
PINNED={'plan.json': 'de67090e807c3a496b890423772cfdaaad1f8e15a0597d793d2c8a000cb5087d', 'SCOPE.json': 'bbbca9d427f62bfc5fcf40b69d4e51da78b71e6d87aa28f5f7e3c13c9d65a1da', 'scripts/SCOPE.json': 'bbbca9d427f62bfc5fcf40b69d4e51da78b71e6d87aa28f5f7e3c13c9d65a1da', 'scripts/build.py': '38a38d07f08b2b1f3e20d2be488e815f79cb039b36871aafbc8160272258acfb', 'scripts/snapshot_support.py': 'ef8b575c70fbb394bfd76cba93b97bc07a6c03abdfe7f4eb2752cfd236be6249'}
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
 need(all(len(plan[k].encode('utf-8'))<=63 for k in ['collection','replacement','derivative_mesh','group','modifier']),'Owned name exceeds native byte limit')
 need(plan['schema']=='v026-shared-shaft-two-solid-union-v1'and plan['source_sha256']==SOURCE_SHA and plan['source_bytes']==SOURCE_BYTES and scope['source_sha256']==SOURCE_SHA,'Wrong source/schema')
 names={'object':'visible_object','hidden':'hidden_original_object','original_mesh':'original_shared_mesh','derivative_mesh':'owned_derivative_mesh','material':'effective_material','raw_material':'original_data_slot_material','collection':'collection','replacement':'union_object','group':'group','modifier':'modifier'}
 need(all(plan[k]==scope[v]for k,v in names.items()),'Scope names/material mismatch')
 need(plan['material']=='V005 | main large ashlar calibrated world units'and plan['raw_material']=='Citadel • deep slate ashlar'and scope['original_material_link']=='OBJECT','Effective OBJECT material mismatch')
 need([x['raw']['seed']for x in plan['mapping']]==[0,16]and len(plan['mapping'])==2,'Two-component scope changed')
 for x,c in zip(plan['mapping'],scope['components']):
  need(x['raw']=={'seed':c['seed'],'indices':c['vertex_ids']}and x['evaluated']=={'seed':c['seed'],'indices':c['vertex_ids'],'bounds':c['bounds'],'faces':c['face_ids']},'Actual component mapping changed')
 need([i for x in plan['mapping']for i in x['raw']['indices']]==list(range(8))+list(range(16,24)),'Wrong16vertex mask scope')
 need(scope['dependency_delta']['original_shared_mesh_users']==[2,1]and scope['dependency_delta']['owned_derivative_users']==1,'Shared dependency scope changed')
 need([c['source_polygon']for c in scope['existing_third_component_contacts']]==[13,28],'Inherited contacts changed')
 need(plan['tolerances']=={'strict_crossing':1e-7,'positive_volume':1e-9},'Tolerance changed')
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
 with tempfile.TemporaryDirectory(prefix='.v026-rebuild-',dir=out.parent)as stage:
  stage=Path(stage);model=stage/'candidate.blend';internal=stage/'build.json'
  cmd=[str(exe),'--background','--factory-startup','--disable-autoexec','--python-exit-code','1','--python',str(ROOT/'scripts/build.py'),'--','--source',str(src),'--plan',str(ROOT/'plan.json'),'--output',str(model),'--report',str(internal)]
  result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  need(result.returncode==0,'Builder failed before final publication:\n'+result.stdout[-12000:])
  preflight(source,output,report);need(sha(__file__)==wrapper_sha,'Wrapper changed during build')
  build=json.loads(internal.read_text());need(build['candidate_sha256']==sha(model)and build['hashes']['source']==SOURCE_SHA and build['hashes']['builder']==PINNED['scripts/build.py']and build['hashes']['helper']==PINNED['scripts/snapshot_support.py']and build['hashes']['plan']==PINNED['plan.json']and build['hashes']['scope']==PINNED['SCOPE.json'],'Internal receipt mismatch')
  receipt={'status':'Fresh guarded rebuild; independent semantic equivalence to accepted candidate still required','source_sha256':SOURCE_SHA,'source_unchanged':True,'wrapper_sha256':wrapper_sha,'pinned_runtime':PINNED,'output_sha256':sha(model),'output_bytes':model.stat().st_size,'output':str(out),'command':cmd,'builder_report':build,'rendered':False,'source_saved':False,'publication':'Exclusive hardlinks, temp inode captured before link; no fallback overwrite'}
  fd,t=tempfile.mkstemp(prefix='.v026-report-',suffix='.json',dir=rep.parent);os.close(fd);tmp_report=Path(t)
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
