"""Integrate independently built local chamber geometry; no render or canonical save."""
import argparse,collections,hashlib,json,os,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
SOURCE='37c0db0e67d0a0a57b7542c899f687d129a6b31208b43e03857a1f3d9e88a255'
COLLECTION='V028 | reversible receiving chamber'
PAYLOAD_SHA='0d07d8ceb27f44cd3c612392d56b40921e60c7f8afaa522aa04f74c17df817f2'
MAPPING_SHA='411e305626b9316e2da9a70426265315b2b97a6e1579f8d2143271f2bcc7eb97'
REPLACEMENTS={'V028 | foundation outside chamber guard','V028 | ashlar outside chamber guard','V028 | east lining outside chamber guard','V028 | local receiving chamber shell'}
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def safe(p,exists=False):
 p=Path(p).expanduser().absolute();need('..' not in p.parts and p.resolve()==p and all(not q.is_symlink() for q in [p,*p.parents]),'Aliased path')
 need(p.is_file() if exists else p.parent.is_dir() and not os.path.lexists(p),'Missing input or occupied output')
 return p
def record(me,p):
 points=[tuple(me.vertices[i].co) for i in p.vertices];points=min(tuple(points[i:]+points[:i]) for i in range(len(points)))
 return points,p.material_index,p.use_smooth

def main():
 need(not sys.flags.optimize,'Optimized Python refused')
 ap=argparse.ArgumentParser()
 for key in ['source','payload','output','report']:ap.add_argument('--'+key,required=True)
 a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);src=safe(a.source,True);payloadpath=safe(a.payload,True);out=safe(a.output);rp=safe(a.report)
 need(len({src,payloadpath,out,rp})==4 and out.suffix=='.blend' and rp.suffix=='.json','Role/path mismatch')
 need(sha(payloadpath)==PAYLOAD_SHA,'Unreviewed geometry payload');payload=json.loads(payloadpath.read_text());need(sha(src)==SOURCE and payload['source_sha256']==SOURCE,'Wrong source')
 mappingpath=ROOT/'frozen_plan/target_mapping_proof.json';need(sha(mappingpath)==MAPPING_SHA,'Frozen target mapping changed')
 mapping=json.loads(mappingpath.read_text());expected_targets={t['object']:t for t in mapping['targets']}
 need({t['object'] for t in payload['targets']}==set(expected_targets) and len(payload['targets'])==3,'Wrong target names')
 for t in payload['targets']:
  ref=expected_targets[t['object']];need(t['raw_vertex_ids']==ref['vertex_ids'] and t['evaluated_seed']==ref['raw_and_evaluated_seed'],'Wrong target component')
  need(all(t[k].startswith('V028 | ') and len(t[k].encode())<=63 for k in ['group_name','mask_name']),'Invalid owned control names')
 need({m['name'] for m in payload['meshes']}==REPLACEMENTS and len(payload['meshes'])==4,'Wrong replacement names')
 pins={str(p):sha(p) for p in [src,payloadpath,Path(__file__),ROOT/'snapshot_support.py',mappingpath]}
 import bpy,bmesh
 sys.path.insert(0,str(ROOT));import snapshot_support as sn
 need(not bpy.data.filepath,'Factory-empty Blender required');bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
 need(COLLECTION not in bpy.data.collections,'Owned collection exists')
 need(len(payload['targets'])==3 and len(payload['meshes'])==4,'Unexpected ownership scope')
 before=sn.snap();beforecollections=sn.collections_snapshot();targets={};raw_without_weights={};expected={}
 for t in payload['targets']:
  o=bpy.data.objects[t['object']];ids=set(t['raw_vertex_ids']);need(o.type=='MESH' and o.data.users==1 and not o.modifiers and not o.vertex_groups,'Target dependencies changed')
  need(len(ids)==len(t['raw_vertex_ids']) and all(0<=i<len(o.data.vertices) for i in ids),'Invalid target indices')
  need(all(not v.groups for v in o.data.vertices),'Unexpected source weights')
  need(all(all(i in ids for i in p.vertices) or all(i not in ids for i in p.vertices) for p in o.data.polygons),'Partial component mask')
  need(t['group_name'] not in o.vertex_groups and t['mask_name'] not in o.modifiers,'Owned control collision')
  targets[o.name]=o;raw_without_weights[o.data.name]=sn.mesh_snapshot(o.data,ignore_owned_weights=True)
  expected[o.name]=collections.Counter(record(o.data,p) for p in o.data.polygons if not any(i in ids for i in p.vertices))
 need(sum(len(t['raw_vertex_ids']) for t in payload['targets'])==148,'Wrong mask scope')
 coll=bpy.data.collections.new(COLLECTION);bpy.context.scene.collection.children.link(coll)
 made=[];mesh_counts=[];mat=bpy.data.materials['Citadel • weathered limestone']
 for spec in payload['meshes']:
  name=spec['name'];need(name not in bpy.data.objects and name not in bpy.data.meshes and len(name.encode())<=63,'Replacement name collision/length')
  need(spec['material_index']==0 and spec['use_smooth'] is False,'Unexpected material/smoothing')
  need(spec['uniform_attributes']=={'select_vertex':True,'select_edge':True,'select_face':True,'sharp_face':True,'edge_seam':False,'edge_sharp':False},'Unexpected source attributes')
  me=bpy.data.meshes.new(name);me.from_pydata(spec['vertices'],[],spec['faces']);me.update();me.materials.append(mat)
  for v in me.vertices:v.select=True
  for e in me.edges:e.select=True;e.use_seam=False;e.use_edge_sharp=False
  for p in me.polygons:p.select=True;p.use_smooth=False;p.material_index=0
  me.update();need([list(v.co) for v in me.vertices]==spec['vertices'],'Payload is not native float32 normalized')
  need([list(p.vertices) for p in me.polygons]==spec['faces'],'Native topology changed')
  edges=collections.defaultdict(list)
  for p in me.polygons:
   vv=list(p.vertices)
   for x,y in zip(vv,vv[1:]+vv[:1]):edges[tuple(sorted((x,y)))].append((x,y))
  need(all(len(q)==2 and q[0]==tuple(reversed(q[1])) for q in edges.values()),'Replacement not closed/oriented')
  need(all(p.area>0 for p in me.polygons),'Zero-area polygon')
  bm=bmesh.new();bm.from_mesh(me);volume=bm.calc_volume(signed=True);bm.free();need(volume>0,'Nonpositive replacement volume')
  me.calc_loop_triangles();mesh_counts.append({'name':name,'vertices':len(me.vertices),'faces':len(me.polygons),'triangles':len(me.loop_triangles),'volume':volume})
  o=bpy.data.objects.new(name,me);coll.objects.link(o);made.append(o)
 need(sum(c['triangles'] for c in mesh_counts)<=2000,'Architecture blockout triangle budget exceeded')
 def add_controls():
  for t in payload['targets']:
   o=targets[t['object']];g=o.vertex_groups.new(name=t['group_name']);g.add(t['raw_vertex_ids'],1,'REPLACE');m=o.modifiers.new(t['mask_name'],'MASK');m.mode='VERTEX_GROUP';m.vertex_group=g.name;m.invert_vertex_group=True;m.threshold=.5;m.use_smooth=False
   need(g.name==t['group_name'] and m.name==t['mask_name'],'Native control name changed')
  bpy.context.view_layer.update()
 def remove_controls():
  for t in payload['targets']:
   o=targets[t['object']];o.modifiers.remove(o.modifiers[t['mask_name']]);o.vertex_groups.remove(o.vertex_groups[t['group_name']])
  bpy.context.view_layer.update()
 add_controls();dg=bpy.context.evaluated_depsgraph_get()
 for name,o in targets.items():
  eo=o.evaluated_get(dg);me=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
  need(collections.Counter(record(me,p) for p in me.polygons)==expected[name],'Non-target evaluated face complement changed');eo.to_mesh_clear()
  need(sn.mesh_snapshot(o.data,ignore_owned_weights=True)==raw_without_weights[o.data.name],'Raw source data changed beyond owned weights')
 remove_controls();rollback=sn.snap()
 for category,old in before.items():
  if isinstance(old,dict):need(all(rollback[category].get(k)==v for k,v in old.items()),'Full original rollback changed '+category)
  else:need(rollback[category]==old,'Full original rollback changed '+category)
 add_controls();after=sn.snap();targetmesh={o.data.name for o in targets.values()}
 for category,old in before.items():
  if isinstance(old,dict):
   exempt=set(targets) if category in ['objects','visible_evaluated'] else targetmesh if category=='meshes' else set()
   need(all(after[category].get(k)==v for k,v in old.items() if k not in exempt),'Untargeted source changed '+category)
  else:need(after[category]==old,'Source changed '+category)
 cs=sn.collections_snapshot();need(all(cs['collections'].get(k)==v for k,v in beforecollections['collections'].items()),'Old collection changed')
 need(cs['root_objects']==beforecollections['root_objects'] and sorted(cs['root_children'])==sorted(beforecollections['root_children']+[COLLECTION]),'Root membership changed')
 need(all(sha(p)==h for p,h in pins.items()),'Pinned inputs changed')
 report={'status':'Unaccepted architecture blockout; independent saved geometry/fixture/visual gates pending','source_sha256':SOURCE,'payload_sha256':sha(payloadpath),'mesh_counts':mesh_counts,'targets':payload['targets'],'owned_collection':COLLECTION,'full_source_rollback_pass':True,'source_raw_except_owned_weights_pass':True,'evaluated_target_complements_pass':True,'other_source_categories_pass':True,'old_collections_pass':True,'lights_added':False,'rendered':False,'source_saved':False,'input_sha256':pins}
 temps=[];published=[]
 try:
  def tmp(dest,suffix):
   fd,n=tempfile.mkstemp(prefix='.v028-',suffix=suffix,dir=dest.parent);os.close(fd);p=Path(n);temps.append(p);return p
  model=tmp(out,'.blend');model.unlink();res=bpy.ops.wm.save_as_mainfile(filepath=str(model),copy=True,compress=True,check_existing=False);need('FINISHED' in res,'Save failed');need(all(sha(p)==h for p,h in pins.items()),'Pinned inputs changed during save')
  report.update(candidate_sha256=sha(model),candidate_bytes=model.stat().st_size);rr=tmp(rp,'.json');rr.write_text(json.dumps(report,indent=2)+'\n')
  for source,dest in [(model,out),(rr,rp)]:safe(dest);st=os.stat(source);os.link(source,dest);published.append((dest,st))
 except BaseException:
  for dest,st in reversed(published):
   now=os.lstat(dest)
   if (now.st_dev,now.st_ino)==(st.st_dev,st.st_ino):dest.unlink()
  raise
 finally:
  for p in temps:p.unlink(missing_ok=True)
 print(json.dumps({'candidate':str(out),'sha256':report['candidate_sha256'],'mesh_counts':mesh_counts}),flush=True)
if __name__=='__main__':main()
