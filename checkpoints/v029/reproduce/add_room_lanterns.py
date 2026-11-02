"""Add exactly two source-style room lantern copies to a verified unlit blockout."""
import argparse,json,hashlib,sys,os,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
COL='V029 | stores warm lanterns'
FIXTURE_PROOF_SHA='ecfd6c77be1d976bdbbb4f764095ba31d294baea87924cf774e394d935a67369'
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
 receipt=json.loads(br.read_text());need(receipt['candidate_sha256']==sha(src) and receipt['source_sha256']=='f0d135e0c6e554b5ae7c520ef9ccefc61e2a7c4abc3129eef1d3d4118bca8096','Wrong blockout source')
 proof=ROOT/'frozen_plan/route_fixture_plan.json';need(sha(proof)==FIXTURE_PROOF_SHA,'Fixture proof changed')
 independent=ROOT/'frozen_plan/fixture_view_proof.json'
 need(sha(independent)=='4975010ca274cee88277bc14e4af9bd0c5618df2c07b167194b4ee2c72c35cdd','Independent fixture proof changed')
 pins={str(p):sha(p) for p in [src,br,Path(__file__),ROOT/'snapshot_support.py',proof,independent]}
 import bpy
 from mathutils import Matrix
 sys.path.insert(0,str(ROOT));import snapshot_support as sn
 need(not bpy.data.filepath,'Factory empty required');bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
 need(COL not in bpy.data.collections,'Owned collection exists');before=sn.snap();cs=sn.collections_snapshot();coll=bpy.data.collections.new(COL);bpy.context.scene.collection.children.link(coll)
 made=[];light_records=[];count=0
 fixture_plan=json.loads(proof.read_text())
 for spec in fixture_plan['lamps']:
  index=spec['id'];delta=Matrix(spec['rigid_matrix'])
  for suffix in SUFFIXES:
   original=bpy.data.objects['V028 | room 1 '+suffix];name='V029 | stores '+str(index)+' '+suffix
   need(name not in bpy.data.objects and name not in getattr(bpy.data,'lights' if original.type=='LIGHT' else 'meshes'),'Name collision')
   need(not original.parent and not original.constraints and not original.modifiers,'Unexpected fixture dependencies')
   ob=original.copy();ob.data=original.data.copy();ob.name=name;ob.data.name=name;coll.objects.link(ob);ob.matrix_world=delta @ original.matrix_world
   need(ob.name==name and ob.data.name==name,'Native name mismatch');made.append(name)
   if original.type=='MESH':
    need(sn.mesh_snapshot(ob.data)==sn.mesh_snapshot(original.data),'Fixture geometry changed');ob.data.calc_loop_triangles();count+=len(ob.data.loop_triangles)
   else:
    need(original.type=='LIGHT' and original.data.type=='POINT','Unexpected light type')
    aa=sn.primitive(original.data);bb=sn.primitive(ob.data)
    for key in ['name','name_full']:aa.pop(key,None);bb.pop(key,None)
    need(aa==bb and sn.tree_snapshot(original.data.node_tree)==sn.tree_snapshot(ob.data.node_tree),'Light recipe changed')
    light_records.append({'name':name,'location':list(ob.location),'energy':ob.data.energy,'color':list(ob.data.color),'shadow_soft_size':ob.data.shadow_soft_size,'copied_from':original.name})
 need(count==1160,'Fixture triangle count changed');total=count+sum(q['triangles'] for q in receipt['mesh_counts']);need(total<=9160,'Combined budget exceeded')
 after=sn.snap()
 for category,old in before.items():
  if isinstance(old,dict):need(all(after[category].get(k)==v for k,v in old.items()),'Existing source changed '+category)
  else:need(after[category]==old,'Existing source changed '+category)
 c2=sn.collections_snapshot();need(all(c2['collections'].get(k)==v for k,v in cs['collections'].items()),'Old collection changed');need(c2['root_objects']==cs['root_objects'] and sorted(c2['root_children'])==sorted(cs['root_children']+[COL]),'Root changed')
 need(all(sha(p)==h for p,h in pins.items()),'Input changed')
 report={'status':'Unaccepted fixed-lit blockout; saved geometric and visual gates pending','input_sha256':pins,'canonical_source_sha256':receipt['source_sha256'],'architecture_receipt_sha256':sha(br),'new_objects':made,'new_collection':COL,'lights':light_records,'fixture_triangles':count,'combined_triangles':total,'all_preexisting_scene_data_unchanged':True,'rendered':False,'recipe':'Two current receiving-lantern copies at fixed staggered side-wall positions with signed-axis rigid rotations. No power, color, world, exposure or old-light changes.'}
 temps=[];published=[]
 try:
  def tmp(dest,suffix):
   fd,n=tempfile.mkstemp(prefix='.v029-lit-',suffix=suffix,dir=dest.parent);os.close(fd);p=Path(n);temps.append(p);return p
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
