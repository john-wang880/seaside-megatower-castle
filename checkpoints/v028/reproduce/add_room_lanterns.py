"""Add exactly two source-style room lantern copies to a verified unlit blockout."""
import argparse,json,hashlib,sys,os,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
COL='V028 | receiving chamber warm lanterns'
FIXTURE_PROOF_SHA='0593cb43d82776d8fe38ad92dbfc1cacb6748f6626c8bda6d2ba03264418b659'
SUFFIXES=['mounting plate','wall arm','lower cup','hood rim','rain hood','cage upright 0','cage upright 1','cage upright 2','cage upright 3','luminous flame','practical warm source']
def need(x,msg):
 if not x:raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def safe(p,exists=False):
 p=Path(p).expanduser().absolute();need(p.resolve()==p and '..' not in p.parts and all(not q.is_symlink() for q in [p,*p.parents]),'Alias refused');need(p.is_file() if exists else p.parent.is_dir() and not os.path.lexists(p),'Input/output state refused');return p

def main():
 need(not sys.flags.optimize,'Optimized Python refused');ap=argparse.ArgumentParser()
 for k in ['source','build-receipt','output','report']:ap.add_argument('--'+k,required=True)
 a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);src=safe(a.source,True);br=safe(a.build_receipt,True);out=safe(a.output);rp=safe(a.report)
 need(len({src,br,out,rp})==4 and out.suffix=='.blend' and rp.suffix=='.json','Role mismatch')
 receipt=json.loads(br.read_text());need(receipt['candidate_sha256']==sha(src) and receipt['source_sha256']=='37c0db0e67d0a0a57b7542c899f687d129a6b31208b43e03857a1f3d9e88a255','Wrong blockout source')
 proof=ROOT/'frozen_plan/route_fixture_plan.json';need(sha(proof)==FIXTURE_PROOF_SHA,'Fixture proof changed')
 pins={str(p):sha(p) for p in [src,br,Path(__file__),ROOT/'snapshot_support.py',proof]}
 import bpy
 from mathutils import Vector
 sys.path.insert(0,str(ROOT));import snapshot_support as sn
 need(not bpy.data.filepath,'Factory empty required');bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
 need(COL not in bpy.data.collections,'Owned collection exists');before=sn.snap();cs=sn.collections_snapshot();coll=bpy.data.collections.new(COL);bpy.context.scene.collection.children.link(coll)
 made=[];light_records=[];count=0
 for index,y in enumerate([34.,39.],1):
  delta=(9.6,y-38.65,0.)
  for suffix in SUFFIXES:
   original=bpy.data.objects['V013 | turn '+suffix];name='V028 | room '+str(index)+' '+suffix
   need(name not in bpy.data.objects and name not in getattr(bpy.data,'lights' if original.type=='LIGHT' else 'meshes'),'Name collision')
   need(not original.parent and not original.constraints and not original.modifiers,'Unexpected fixture dependencies')
   ob=original.copy();ob.data=original.data.copy();ob.name=name;ob.data.name=name;coll.objects.link(ob);ob.location=original.location+Vector(delta)
   need(ob.name==name and ob.data.name==name,'Native name mismatch');made.append(name)
   if original.type=='MESH':
    need(sn.mesh_snapshot(ob.data)==sn.mesh_snapshot(original.data),'Fixture geometry changed');ob.data.calc_loop_triangles();count+=len(ob.data.loop_triangles)
   else:
    need(original.type=='LIGHT' and original.data.type=='POINT','Unexpected light type')
    aa=sn.primitive(original.data);bb=sn.primitive(ob.data)
    for key in ['name','name_full']:aa.pop(key,None);bb.pop(key,None)
    need(aa==bb and sn.tree_snapshot(original.data.node_tree)==sn.tree_snapshot(ob.data.node_tree),'Light recipe changed')
    light_records.append({'name':name,'location':list(ob.location),'energy':ob.data.energy,'color':list(ob.data.color),'shadow_soft_size':ob.data.shadow_soft_size,'copied_from':original.name})
 need(count==1160,'Fixture triangle count changed');total=count+sum(q['triangles'] for q in receipt['mesh_counts']);need(total<=3160,'Combined budget exceeded')
 after=sn.snap()
 for category,old in before.items():
  if isinstance(old,dict):need(all(after[category].get(k)==v for k,v in old.items()),'Existing source changed '+category)
  else:need(after[category]==old,'Existing source changed '+category)
 c2=sn.collections_snapshot();need(all(c2['collections'].get(k)==v for k,v in cs['collections'].items()),'Old collection changed');need(c2['root_objects']==cs['root_objects'] and sorted(c2['root_children'])==sorted(cs['root_children']+[COL]),'Root changed')
 need(all(sha(p)==h for p,h in pins.items()),'Input changed')
 report={'status':'Unaccepted fixed-lit blockout; saved geometric and visual gates pending','input_sha256':pins,'canonical_source_sha256':receipt['source_sha256'],'architecture_receipt_sha256':sha(br),'new_objects':made,'new_collection':COL,'lights':light_records,'fixture_triangles':count,'combined_triangles':total,'all_preexisting_scene_data_unchanged':True,'rendered':False,'recipe':'Two exact current turn-lantern copies at fixed far-wall positions. No power, color, world, exposure or old-light changes.'}
 temps=[];published=[]
 try:
  def tmp(dest,suffix):
   fd,n=tempfile.mkstemp(prefix='.v028-lit-',suffix=suffix,dir=dest.parent);os.close(fd);p=Path(n);temps.append(p);return p
  model=tmp(out,'.blend');model.unlink();result=bpy.ops.wm.save_as_mainfile(filepath=str(model),copy=True,compress=True,check_existing=False);need('FINISHED' in result,'Save failed');need(all(sha(p)==h for p,h in pins.items()),'Pinned inputs changed')
  report.update(candidate_sha256=sha(model),candidate_bytes=model.stat().st_size);rr=tmp(rp,'.json');rr.write_text(json.dumps(report,indent=2)+'\n')
  for source,dest in [(model,out),(rr,rp)]:safe(dest);st=os.stat(source);os.link(source,dest);published.append((dest,st))
 except BaseException:
  for dest,st in reversed(published):
   now=os.lstat(dest)
   if (now.st_dev,now.st_ino)==(st.st_dev,st.st_ino):dest.unlink()
  raise
 finally:
  for p in temps:p.unlink(missing_ok=True)
 print(json.dumps({'sha256':report['candidate_sha256'],'lights':light_records,'combined_triangles':total}),flush=True)
if __name__=='__main__':main()
