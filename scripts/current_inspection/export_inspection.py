"""Opt-in latest-reviewed inspection-copy exporter; no rendering or autoexec."""
import argparse,hashlib,json,os,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from preflight import preflight,require,sha,publish_pair,CATALOG_SHA,GuardError
OWNER='castle-current-inspection-v1';TAG='castle_inspection_owner'
def collision_check(c):
 import bpy
 require(bpy.context.scene.get(c['marker']) is None,'Source already marked/marker collision; re-export only from canonical source')
 require(bpy.data.collections.get(c['collection']) is None,'Collection name collision; existing data never adopted')
 require(bpy.data.texts.get(c['text']) is None,'Text name collision; existing data never adopted')
 for key,v in c['views'].items():
  if v['existing']:
   o=bpy.data.objects.get(v['camera_name']);require(o is not None and o.type=='CAMERA','Original hero camera missing')
   require(max(abs(o.matrix_world[i][j]-v['matrix'][i][j]) for i in range(4) for j in range(4))<1e-5,'Original hero pose mismatch')
   for k,value in v['data'].items():
    actual=getattr(o.data,k);require(abs(actual-value)<1e-5 if isinstance(value,(int,float)) else actual==value,'Original hero gate mismatch')
  else:
   require(bpy.data.objects.get(v['camera_name']) is None and bpy.data.cameras.get(v['camera_name']+' data') is None,'Camera/data name collision: '+key)
 require(bpy.context.scene.camera==bpy.data.objects[c['views']['hero']['camera_name']],'Canonical default camera is not original hero; refuse changing source defaults')

def install(c,identity):
 import bpy
 from mathutils import Matrix
 collision_check(c)
 config={k:c[k] for k in ['collection','text','marker','views','source_sha256']};config['catalog_sha256']=CATALOG_SHA
 template=(ROOT/'ui_template.py').read_text(encoding='utf-8');code=template.replace('CONFIG = None  # Exporter replaces this assignment with literal reviewed config.','CONFIG = '+repr(config))
 require(code!=template,'UI template placeholder missing')
 collection=bpy.data.collections.new(c['collection']);collection[TAG]=OWNER;bpy.context.scene.collection.children.link(collection)
 for key,v in c['views'].items():
  if v['existing']:continue
  data=bpy.data.cameras.new(v['camera_name']+' data');data[TAG]=OWNER
  for k,value in v['data'].items():setattr(data,k,value)
  data.dof.use_dof=False;o=bpy.data.objects.new(v['camera_name'],data);o[TAG]=OWNER;o['bookmark_key']=key;collection.objects.link(o);o.matrix_world=Matrix(v['matrix'])
 text=bpy.data.texts.new(c['text']);text[TAG]=OWNER;text.write(code);text.use_module=False
 marker={'owner':OWNER,'catalog_sha256':CATALOG_SHA,'source_sha256':identity['source_sha256'],'source_bytes':identity['source_bytes'],'reviewed_version':identity['reviewed_version'],'manifest_sha256':identity['manifest_sha256'],'ui_text_sha256':hashlib.sha256(code.encode()).hexdigest(),'notice':'Derived inspection copy. Marker records export provenance only, not certification of later user edits.'}
 bpy.context.scene[c['marker']]=json.dumps(marker,ensure_ascii=False,sort_keys=True);bpy.context.view_layer.update();return marker

def export(repository,source,output,report):
 identity,c=preflight(repository,source,output,report,ROOT/'catalog.json')
 runtime={n:sha(ROOT/n) for n in ['export_inspection.py','preflight.py','catalog.json','ui_template.py']}
 import bpy
 require(bpy.app.version[:2]==(5,2),'Reviewed Blender5.2 build required; other versions not validated')
 require(not bpy.data.filepath,'Start Blender with --factory-startup and no positional .blend')
 bpy.ops.wm.open_mainfile(filepath=identity['source'],load_ui=False,use_scripts=False)
 # Re-read all bindings before mutation; no stale manifest/source assumption.
 again,_=preflight(repository,source,output,report,ROOT/'catalog.json');require(again==identity,'Preflight identity changed before installation');require(all(sha(ROOT/n)==h for n,h in runtime.items()),'Runtime changed')
 marker=install(c,identity);tmpfiles=[]
 try:
  def temp_for(dest,suffix):
   fd,path=tempfile.mkstemp(prefix='.inspection-',suffix=suffix,dir=str(Path(dest).parent));os.close(fd);tmpfiles.append(Path(path));return Path(path)
  model_tmp=temp_for(output,'.blend');model_tmp.unlink()
  result=bpy.ops.wm.save_as_mainfile(filepath=str(model_tmp),copy=True,compress=True,check_existing=False)
  require('FINISHED' in result and model_tmp.is_file(),'Inspection-copy save failed')
  again,_=preflight(repository,source,output,report,ROOT/'catalog.json');require(again==identity and all(sha(ROOT/n)==h for n,h in runtime.items()),'Source/manifest/runtime changed during export')
  receipt={**identity,'runtime_sha256':runtime,'output_sha256':sha(model_tmp),'output_bytes':model_tmp.stat().st_size,'source_unchanged':True,'source_saved':False,'rendered':False,'manual_text_only':True,'text_use_module':False,'default_camera':bpy.context.scene.camera.name,'added_cameras':15,'bookmark_count':16,'marker':marker,'scope':'Only owned cameras/collection/manualText/provenance marker added; original settings preserved. Independent deep QA is separate.'}
  rep_tmp=temp_for(report,'.json');rep_tmp.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  with open(rep_tmp,'rb') as f:os.fsync(f.fileno())
  with open(model_tmp,'rb') as f:os.fsync(f.fileno())
  publish_pair(model_tmp,output,rep_tmp,report)
  return receipt
 finally:
  for p in tmpfiles:
   if p.exists():p.unlink()

def main(argv=None):
 if argv is None:argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository-root',required=True);p.add_argument('--source',required=True);p.add_argument('--output',required=True);p.add_argument('--report',required=True);p.add_argument('--preflight-only',action='store_true');a=p.parse_args(argv)
 if a.preflight_only:result=preflight(a.repository_root,a.source,a.output,a.report,ROOT/'catalog.json')[0]
 else:result=export(a.repository_root,a.source,a.output,a.report)
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
