"""Import-safe stdlib guards; no bpy, installation, network or rendering."""
import hashlib,json,math,os,re,sys
from pathlib import Path
CATALOG_SHA='0f672d7de20ff37d32f9922cbaa26d4e58d1e7dbd7bb9abf7a0e3c3879ec7d1b'
VERSION=30
SOURCE_SHA='9f020b7ec6eda309d674653598b169f65ba5dc1d1f194ffa31323f6393feda35'
SOURCE_BYTES=47842841
class GuardError(ValueError):pass
def require(ok,message):
 if not ok:raise GuardError(message)
def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def unaliased(value):
 p=Path(value).expanduser().absolute()
 require('..' not in p.parts,'Parent traversal aliases are not accepted')
 for item in [p,*p.parents]:
  require(not item.is_symlink(),'Symlink path rejected: '+str(item))
 require(p.resolve()==p,'Path alias rejected: '+str(p))
 return p
def load_catalog(path):
 p=unaliased(path);require(p.is_file() and sha(p)==CATALOG_SHA,'Reviewed camera catalog hash mismatch')
 c=json.loads(p.read_text(encoding='utf-8'))
 require(c['schema']=='castle-current-inspection-catalog-v1' and c['reviewed_version']==VERSION and c['source_sha256']==SOURCE_SHA and c['source_bytes']==SOURCE_BYTES,'Unsupported catalog/source binding')
 require(len(c['views'])==20 and c['views']['hero']['existing'],'Catalog must contain twenty reviewed views')
 names=[]
 for k,v in c['views'].items():
  m=v['matrix'];require(len(m)==4 and all(len(row)==4 for row in m) and all(isinstance(x,(int,float)) and math.isfinite(x) for row in m for x in row),'Invalid camera matrix')
  d=v['data'];require(d['type']=='PERSP' and d['sensor_fit'] in ['AUTO','HORIZONTAL','VERTICAL'] and d['lens']>0 and 0<d['clip_start']<d['clip_end'],'Invalid camera data')
  names.append(v['camera_name'])
 require(len(names)==len(set(names)),'Duplicate camera name')
 return c
def latest_manifest(repository):
 root=unaliased(repository);require(root.is_dir(),'Repository root is not a directory');base=root/'checkpoints';require(base.is_dir(),'Missing checkpoints directory');unaliased(base)
 found=[]
 for d in base.iterdir():
  match=re.fullmatch(r'v([0-9]+)',d.name)
  if match and os.path.lexists(d/'MANIFEST.json'):
   unaliased(d);unaliased(d/'MANIFEST.json');found.append((int(match[1]),d/'MANIFEST.json'))
 require(bool(found),'No versioned checkpoint manifests')
 nums=[v for v,p in found];require(len(nums)==len(set(nums)),'Ambiguous numeric checkpoint versions')
 version,path=max(found,key=lambda item:item[0]);require(version==VERSION,'Latest checkpoint v%d is not reviewed by this catalog; no fallback'%version)
 m=json.loads(path.read_text(encoding='utf-8'));require(m.get('format')=='blend-zstd-frames-v1','Unsupported checkpoint format')
 require(m.get('model_sha256')==SOURCE_SHA and m.get('model_bytes')==SOURCE_BYTES and m.get('model')=='castle_v030.blend','Latest manifest source binding mismatch')
 return root,path,m
def new_destination(value,suffix):
 p=unaliased(value);require(p.suffix.lower()==suffix,'Expected '+suffix+' destination');require(p.parent.is_dir(),'Destination parent must already exist');require(not os.path.lexists(p),'Destination already exists (including dangling link): '+str(p));return p
def preflight(repository,source,output,report,catalog):
 require(sys.flags.optimize==0,'Optimized Python is not supported: integrity guards must remain enabled')
 c=load_catalog(catalog);root,mp,m=latest_manifest(repository);src=unaliased(source);require(src.is_file(),'Source is not a regular file');require(src.stat().st_size==SOURCE_BYTES,'Source byte count does not match latest manifest');require(sha(src)==SOURCE_SHA,'Source SHA does not match latest reviewed checkpoint')
 out=new_destination(output,'.blend');rep=new_destination(report,'.json');require(len({src,out,rep})==3,'Source/output/report aliases are forbidden')
 for dest in [out,rep]:require(not dest.is_relative_to(root/'checkpoints'),'Do not write derived copies into immutable checkpoints')
 return {'repository':str(root),'manifest':str(mp),'manifest_sha256':sha(mp),'source':str(src),'source_sha256':SOURCE_SHA,'source_bytes':SOURCE_BYTES,'output':str(out),'report':str(rep),'catalog_sha256':CATALOG_SHA,'reviewed_version':VERSION},c

def publish_pair(temp_output,output,temp_report,report):
 """Exclusive atomic publication per file; rollback only our still-owned inode."""
 created=[]
 try:
  for temp,dest in [(temp_output,output),(temp_report,report)]:
   dest=unaliased(dest);require(not os.path.lexists(dest),'Publish destination appeared: '+str(dest));owned=os.stat(temp);os.link(temp,dest);created.append((dest,owned))
 except BaseException:
  for dest,st in reversed(created):
   try:
    now=os.lstat(dest)
    if (now.st_dev,now.st_ino)==(st.st_dev,st.st_ino):os.unlink(dest)
   except FileNotFoundError:pass
  raise
 return [str(p) for p,_ in created]
