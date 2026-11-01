"""Guarded wrapper around the byte-exact executed builder; no runtime rewriting."""
import argparse,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE_SHA='89f9f6a8a57103d99100935b96624469ddf1fd52b9703e0d9177a352e735c856'
SOURCE_BYTES=47631759
PINNED={'scripts/SCOPE.json':'5cbedd667a89fd41c1ce0dc3137fea83792ec3b1548367508f5bed9dc1daa739','plan.json': '08f3e9d3366d1a99704189486ddd822eb76f37d06959a8d98fbc89c3033ee065', 'SCOPE.json': '5cbedd667a89fd41c1ce0dc3137fea83792ec3b1548367508f5bed9dc1daa739', 'scripts/build.py': '96302af06d49668eeae532b824f7bf405d9cdc82d6df15b501fc79dbd26900a8', 'scripts/snapshot_support.py': 'ef8b575c70fbb394bfd76cba93b97bc07a6c03abdfe7f4eb2752cfd236be6249'}
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
 need(all(len(n.encode('utf-8'))<=63 for n in [plan['collection'],plan['group'],plan['modifier']]+[f['replacement']for f in plan['frames']]),'Owned name exceeds native byte limit')
 need(plan['schema']=='v025-four-evaluated-frame-unions-v1'and plan['source_sha256']==SOURCE_SHA and plan['source_bytes']==SOURCE_BYTES,'Wrong plan source/schema')
 need(plan['object']==scope['target']=='V008 | gallery with genuine eastern approach portal'and plan['material']==scope['material']=='Citadel • aged gallery grey','Wrong object/material')
 need(scope['source_sha256']==SOURCE_SHA and scope['original_chain']==['Soft carved stone arrises','V024 | remove six evaluated solids after bevel']and scope['existing_owned_group']=='V024 | six original rear solids rollback','Inherited source chain/group scope changed')
 need(len(plan['frames'])==len(scope['groups'])==4 and len(plan['mapping'])==20,'Wrong four-group scope')
 raw=[];evaluated=[]
 for frame,g in zip(plan['frames'],scope['groups']):
  need(frame=={'ordinal':g['ordinal'],'replacement':g['replacement_object'],'plane_y':g['plane_y'],'seeds':g['evaluated_seeds']},'Frame identity mismatch')
  parts=[x for x in plan['mapping']if x['frame']==g['ordinal']]
  need(len(parts)==5 and [x['evaluated']['seed']for x in parts]==g['evaluated_seeds']and[x['raw']['seed']for x in parts]==g['raw_component_seeds'],'Five-solid mapping mismatch')
  ids=[i for x in parts for i in x['raw']['indices']];need(ids==g['raw_vertex_ids'],'Raw scope mismatch');raw+=ids
  for x in parts:
   need(x['raw']['indices']==list(range(x['raw']['seed'],x['raw']['seed']+8))and x['evaluated']['indices']==list(range(x['evaluated']['seed'],x['evaluated']['seed']+24)),'Component ID scope changed');evaluated+=x['evaluated']['indices']
 need(len(set(raw))==160 and len(set(evaluated))==480 and not set(raw)&set(range(16,64)),'Disjoint160/480 scope changed')
 need(plan['collection']==scope['collection']and plan['group']==scope['new_group']and plan['modifier']==scope['new_modifier'],'Owned names mismatch')
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
 with tempfile.TemporaryDirectory(prefix='.v025-rebuild-',dir=out.parent)as stage:
  stage=Path(stage);model=stage/'candidate.blend';internal=stage/'build.json'
  cmd=[str(exe),'--background','--factory-startup','--disable-autoexec','--python-exit-code','1','--python',str(ROOT/'scripts/build.py'),'--','--source',str(src),'--plan',str(ROOT/'plan.json'),'--output',str(model),'--report',str(internal)]
  result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  need(result.returncode==0,'Builder failed before final publication:\n'+result.stdout[-12000:])
  preflight(source,output,report);need(sha(__file__)==wrapper_sha,'Wrapper changed during build')
  build=json.loads(internal.read_text());need(build['candidate_sha256']==sha(model)and build['hashes']['source']==SOURCE_SHA and build['hashes']['builder']==PINNED['scripts/build.py']and build['hashes']['helper']==PINNED['scripts/snapshot_support.py']and build['hashes']['plan']==PINNED['plan.json']and build['hashes']['scope']==PINNED['SCOPE.json'],'Internal receipt mismatch')
  receipt={'status':'Fresh guarded rebuild; independent semantic equivalence to accepted candidate still required','source_sha256':SOURCE_SHA,'source_unchanged':True,'wrapper_sha256':wrapper_sha,'pinned_runtime':PINNED,'output_sha256':sha(model),'output_bytes':model.stat().st_size,'output':str(out),'command':cmd,'builder_report':build,'rendered':False,'source_saved':False,'publication':'Exclusive hardlinks, temp inode captured before link; no fallback overwrite'}
  fd,t=tempfile.mkstemp(prefix='.v025-report-',suffix='.json',dir=rep.parent);os.close(fd);tmp_report=Path(t)
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
