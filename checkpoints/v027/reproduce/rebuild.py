"""Guarded wrapper around the byte-exact executed builder; no runtime rewriting."""
import argparse,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE_SHA='efcd894acdc045a30f845f05267662957b656bc7fe0ee4cf48c05fc798b610ee'
SOURCE_BYTES=47680699
PINNED={'plan.json': '2d4673f76244d1c7d1bf40f002370e219f35db7198ba413a309a6008f0384e78', 'scripts/build.py': '6da85e129267f3e5bac597c8635ea1741c1744ed0e147ec3f5816220f23b19a1', 'scripts/plan.json': '2d4673f76244d1c7d1bf40f002370e219f35db7198ba413a309a6008f0384e78', 'scripts/snapshot_support.py': 'ef8b575c70fbb394bfd76cba93b97bc07a6c03abdfe7f4eb2752cfd236be6249', 'scripts/support_envelope.json': '8fe6d70b4b6f24b5ae83a4bfb2df3734d3644f5ca2fa229a20478e1cae60352e'}
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
def validate_scope(plan):
 need(plan['source_sha256']==SOURCE_SHA and plan['source_bytes']==SOURCE_BYTES,'Wrong source')
 names=['collection','object','mesh']
 need(all(isinstance(plan[k],str)and 0<len(plan[k].encode('utf-8'))<=63 for k in names),'Owned UTF8 name length')
 need(plan['collection']=='V027 | first hall ceiling bay study'and plan['object']==plan['mesh']=='V027 | three pointed bays with high wall bands','Owned names changed')
 need(plan['material']=='Citadel • weathered limestone','Material changed')
 need(plan['stations']==[-1.8,.4,2.6]and plan['bounds']==[[-2.5,36.56,31.98],[3.2,39.44,32.82]],'Scope changed')
 need(plan['triangle_budget']==2000 and plan['arch_depth']==.28 and plan['courses']==7,'Art scope changed')
 need([plan[k]for k in ['spring_z','crown_z','crown_top','groove_y_width','groove_depth','groove_side_depth']]==[32.15,32.5,32.82,.008,.006,.004],'Profile changed')
def preflight(source,output,report,root=ROOT):
 need(not sys.flags.optimize,'Optimized Python is refused')
 for name,h in PINNED.items():need(sha(safe(root/name,True))==h,'Runtime/plan/scope hash mismatch: '+name)
 plan=json.loads((root/'plan.json').read_text());validate_scope(plan)
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
 with tempfile.TemporaryDirectory(prefix='.hall-v027-rebuild-',dir=out.parent)as stage:
  stage=Path(stage);model=stage/'candidate.blend';internal=stage/'build.json'
  cmd=[str(exe),'--background','--factory-startup','--disable-autoexec','--python-exit-code','1','--python-expr','import sys; sys.dont_write_bytecode=True','--python',str(ROOT/'scripts/build.py'),'--','--source',str(src),'--output',str(model),'--report',str(internal)]
  env=dict(os.environ);env['PYTHONDONTWRITEBYTECODE']='1'
  result=subprocess.run(cmd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  need(result.returncode==0,'Builder failed before final publication:\n'+result.stdout[-12000:])
  preflight(source,output,report);need(sha(__file__)==wrapper_sha,'Wrapper changed during build')
  build=json.loads(internal.read_text());need(build['candidate_sha256']==sha(model)and build['source_sha256']==SOURCE_SHA and build['builder_sha256']==PINNED['scripts/build.py']and build['pinned_inputs']=={k:PINNED['scripts/'+k]for k in ['plan.json','support_envelope.json','snapshot_support.py']},'Internal receipt mismatch')
  receipt={'status':'Fresh guarded rebuild; independent semantic equivalence to accepted candidate still required','source_sha256':SOURCE_SHA,'source_unchanged':True,'wrapper_sha256':wrapper_sha,'pinned_runtime':PINNED,'output_sha256':sha(model),'output_bytes':model.stat().st_size,'output':str(out),'command':cmd,'builder_report':build,'rendered':False,'source_saved':False,'publication':'Exclusive hardlinks, temp inode captured before link; no fallback overwrite'}
  fd,t=tempfile.mkstemp(prefix='.hall-v027-report-',suffix='.json',dir=rep.parent);os.close(fd);tmp_report=Path(t)
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
