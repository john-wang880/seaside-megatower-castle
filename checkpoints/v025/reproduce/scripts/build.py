"""Bounded exact evaluated-solid union. No rendering or canonical save."""
import argparse,collections,hashlib,json,os,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
SOURCE_SHA='89f9f6a8a57103d99100935b96624469ddf1fd52b9703e0d9177a352e735c856'
PLAN_SHA='08f3e9d3366d1a99704189486ddd822eb76f37d06959a8d98fbc89c3033ee065'
SCOPE_SHA='5cbedd667a89fd41c1ce0dc3137fea83792ec3b1548367508f5bed9dc1daa739'
HELPER_SHA='ef8b575c70fbb394bfd76cba93b97bc07a6c03abdfe7f4eb2752cfd236be6249'
def need(ok,message):
 if not ok:raise RuntimeError(message)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def safe(p,exists=False):
 p=Path(p).expanduser().absolute();need('..'not in p.parts and all(not x.is_symlink()for x in[p,*p.parents])and p.resolve()==p,'Aliased path refused')
 if exists:need(p.is_file(),'Missing input')
 else:need(p.parent.is_dir()and not os.path.lexists(p),'Output/report exists or parent missing')
 return p
def publish(pairs):
 made=[]
 try:
  for temp,dest in pairs:
   safe(dest);owned=os.stat(temp);os.link(temp,dest);made.append((dest,owned))
 except BaseException:
  for dest,owned in reversed(made):
   try:
    now=os.lstat(dest)
    if(now.st_dev,now.st_ino)==(owned.st_dev,owned.st_ino):os.unlink(dest)
   except FileNotFoundError:pass
  raise

def main():
 need(not sys.flags.optimize,'Optimized Python refused')
 ap=argparse.ArgumentParser()
 for k in ['source','plan','output','report']:ap.add_argument('--'+k,required=True)
 a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);src=safe(a.source,True);pp=safe(a.plan,True);out=safe(a.output);rp=safe(a.report);need(len({src,pp,out,rp})==4 and out.suffix.lower()=='.blend'and rp.suffix.lower()=='.json','Unsafe output roles')
 need(sha(pp)==PLAN_SHA and sha(ROOT/'SCOPE.json')==SCOPE_SHA and sha(ROOT/'snapshot_support.py')==HELPER_SHA,'Pinned plan/scope/helper mismatch');plan=json.loads(pp.read_text());need(sha(src)==SOURCE_SHA==plan['source_sha256']and src.stat().st_size==plan['source_bytes'],'Source mismatch')
 hashes={'source':SOURCE_SHA,'plan':sha(pp),'builder':sha(__file__),'helper':sha(ROOT/'snapshot_support.py'),'scope':sha(ROOT/'SCOPE.json')}
 import bpy,bmesh
 from mathutils import Vector
 from mathutils.bvhtree import BVHTree
 from mathutils.geometry import intersect_ray_tri
 sys.path.insert(0,str(ROOT));import snapshot_support as sn
 need(not bpy.data.filepath,'Factory-empty Blender required');bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
 o=bpy.data.objects[plan['object']];need(o.type=='MESH'and o.data.users==1 and not o.data.shape_keys and not o.parent and not o.constraints and not o.animation_data,'Unexpected source object state')
 need([m.name for m in o.modifiers]==['Soft carved stone arrises','V024 | remove six evaluated solids after bevel'] and o.modifiers[0].type=='BEVEL' and o.modifiers[0].use_clamp_overlap,'Source chain unexpected');mods_before=[sn.primitive(m)for m in o.modifiers];raw_before=sn.mesh_snapshot(o.data)
 need([g.name for g in o.vertex_groups]==['V024 | six original rear solids rollback'],'Source vertexgroups unexpected')
 groups_before=[sn.primitive(g)for g in o.vertex_groups];active_group_before=o.vertex_groups.active_index
 prior_union=bpy.data.objects['V024 | exact evaluated rear stepped union'];prior_union_before={'mesh':sn.mesh_snapshot(prior_union.data),'object':sn.primitive(prior_union)}
 mat=bpy.data.materials[plan['material']];need(o.data.materials[0]==mat,'Material mismatch')
 need(not any(l.from_node.bl_idname in ['ShaderNodeTexCoord','ShaderNodeObjectInfo','ShaderNodeParticleInfo','ShaderNodeGroup']for l in mat.node_tree.links),'Material object-coordinate dependencies require explicit review')
 mat_before=sn.digest({'properties':sn.primitive(mat),'nodes':sn.tree_snapshot(mat.node_tree)})
 for name,items in [(plan['collection'],bpy.data.collections)]+[(f['replacement'],items)for f in plan['frames']for items in [bpy.data.objects,bpy.data.meshes]]+[(plan['group'],o.vertex_groups),(plan['modifier'],o.modifiers)]:need(name not in items,'Owned name collision')
 dg=bpy.context.evaluated_depsgraph_get();eo=o.evaluated_get(dg);em=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
 selected=set();raw_ids=[];parts=[]
 def face_record(mesh,f):
  return(tuple(tuple(mesh.vertices[i].co)for i in f.vertices),f.material_index,f.use_smooth)
 for pair in plan['mapping']:
  ids=pair['evaluated']['indices'];raw=pair['raw']['indices'];need(len(ids)==24 and len(raw)==8,'Unexpected component sizes');selected.update(ids);raw_ids.extend(raw)
  fs=[f for f in em.polygons if set(f.vertices)<=set(ids)];need(len(fs)==26 and all(f.material_index==0 for f in fs),'Evaluated component mismatch')
  need(not any(set(f.vertices)&set(ids) and not set(f.vertices)<=set(ids) for f in em.polygons),'Component is connected outside scope')
  need([list(min(em.vertices[i].co[j]for i in ids)for j in range(3)),list(max(em.vertices[i].co[j]for i in ids)for j in range(3))]==pair['evaluated']['bounds'],'Evaluated bounds mismatch')
  remap={old:i for i,old in enumerate(ids)};parts.append({'frame':pair['frame'],'seed':pair['evaluated']['seed'],'vertices':[list(em.vertices[i].co)for i in ids],'faces':[[remap[i]for i in f.vertices]for f in fs],'smooth':[f.use_smooth for f in fs]})
 complement=collections.Counter(face_record(em,f)for f in em.polygons if not set(f.vertices)<=selected);input_total=len(em.vertices);eo.to_mesh_clear();need(len(selected)==480 and len(set(raw_ids))==160 and not set(raw_ids)&set(range(16,64)),'Selection cardinality or inherited weight overlap mismatch')
 need(all(len(n.encode('utf-8'))<=63 for n in [plan['collection'],plan['group'],plan['modifier']]+[f['replacement']for f in plan['frames']]),'Owned name exceeds native byte limit')
 coll=bpy.data.collections.new(plan['collection']);bpy.context.scene.collection.children.link(coll);need(coll.name==plan['collection'],'Collection name changed')
 def build_frame(frame,parts):
  created=[]
  for i,part in enumerate(parts):
   me=bpy.data.meshes.new(frame['replacement']if i==0 else 'V025 temporary evaluated operand '+str(i));me.from_pydata(part['vertices'],[],part['faces']);me.materials.append(mat)
   for f,smooth in zip(me.polygons,part['smooth']):f.use_smooth=smooth
   me.update();obj=bpy.data.objects.new(me.name,me);coll.objects.link(obj);obj.matrix_world=o.matrix_world.copy();created.append(obj)
  union=created[0];steps=[]
  for operand in created[1:]:
   mod=union.modifiers.new('V025 temporary exact union','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=operand;mod.use_self=False;mod.use_hole_tolerant=False
   with bpy.context.temp_override(object=union,active_object=union,selected_objects=[union],selected_editable_objects=[union]):result=bpy.ops.object.modifier_apply(modifier=mod.name)
   need('FINISHED'in result,'Exact union failed');steps.append({'operand':operand.name,'vertices':len(union.data.vertices),'faces':len(union.data.polygons)})
   mesh=operand.data;bpy.data.objects.remove(operand,do_unlink=True);bpy.data.meshes.remove(mesh)
  union.name=frame['replacement'];union.data.name=frame['replacement'];need(union.name==frame['replacement']and union.data.name==frame['replacement'],'Union object/mesh name changed');need(not union.modifiers,'Unexpected unapplied union modifier')
  # Closed, consistently directed edges and positive signed volume.
  edges=collections.defaultdict(list)
  for f in union.data.polygons:
   vs=list(f.vertices)
   for x,y in zip(vs,vs[1:]+vs[:1]):edges[tuple(sorted((x,y)))].append((x,y))
  need(all(len(v)==2 and v[0]==tuple(reversed(v[1]))for v in edges.values()),'Union not closed/oriented')
  bm=bmesh.new();bm.from_mesh(union.data);volume=bm.calc_volume(signed=True);bm.free();need(volume>plan['tolerances']['positive_volume'],'Nonpositive union volume')
  duplicate=collections.Counter(tuple(sorted(tuple(union.data.vertices[i].co)for i in f.vertices))for f in union.data.polygons);need(max(duplicate.values())==1,'Exact duplicate union polygons')
  need(all(f.material_index==0 and not f.use_smooth for f in union.data.polygons),'Material/smoothing unexpectedly changed')
  union.data.calc_loop_triangles();triangles=[tuple(t.vertices)for t in union.data.loop_triangles];coords=[v.co.copy()for v in union.data.vertices];bvh=BVHTree.FromPolygons(coords,triangles,all_triangles=True);strict=[];eps=plan['tolerances']['strict_crossing']
  for i,j in bvh.overlap(bvh):
   if i>=j or set(triangles[i])&set(triangles[j]):continue
   for ti,tj in[(triangles[i],triangles[j]),(triangles[j],triangles[i])]:
    a,b,c=[coords[k]for k in tj]
    for x,y in zip(ti,ti[1:]+ti[:1]):
     start,end=coords[x],coords[y];delta=end-start
     if delta.length<eps:continue
     hit=intersect_ray_tri(a,b,c,delta.normalized(),start,True)
     if hit is not None and eps<(hit-start).dot(delta.normalized())<delta.length-eps:
      # Reject transverse strict interior intersections, not shared boundary contacts.
      normal=(b-a).cross(c-a)
      if abs(normal.normalized().dot(delta.normalized()))>eps and min((b-a).cross(hit-a).length,(c-b).cross(hit-b).length,(a-c).cross(hit-c).length)>eps:strict.append([i,j])
  need(not strict,'Strict nonadjacent triangle crossings')
  return {'ordinal':frame['ordinal'],'name':union.name,'vertices':len(union.data.vertices),'faces':len(union.data.polygons),'triangles':len(triangles),'signed_volume':volume,'boolean_steps':steps}
 unions=[build_frame(frame,[p for p in parts if p['frame']==frame['ordinal']])for frame in plan['frames']]
 group=o.vertex_groups.new(name=plan['group']);group.add(raw_ids,1.0,'REPLACE');mask=o.modifiers.new(plan['modifier'],'MASK');mask.mode='VERTEX_GROUP';mask.vertex_group=group.name;mask.invert_vertex_group=True;mask.threshold=.5;mask.use_smooth=False
 need(group.name==plan['group']and mask.name==plan['modifier'],'Native group/Mask name changed')
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();eo=o.evaluated_get(dg);em=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
 need(input_total-len(em.vertices)==480,'Mask did not remove exactly480evaluated vertices');need(collections.Counter(face_record(em,f)for f in em.polygons)==complement,'Evaluated complement changed');eo.to_mesh_clear()
 for mod,state in zip(list(o.modifiers)[:2],mods_before):
  if state['is_active']:mod.is_active=True
 need([sn.primitive(m)for m in list(o.modifiers)[:2]]==mods_before,'Original modifier chain changed')
 # Reversible raw-source proof: remove only owned weights, compare all raw mesh attrs, then restore.
 o.vertex_groups.remove(group);need(sn.mesh_snapshot(o.data)==raw_before,'Raw rollback source changed');group=o.vertex_groups.new(name=plan['group']);group.add(raw_ids,1.0,'REPLACE');mask.vertex_group=group.name;o.vertex_groups.active_index=active_group_before;bpy.context.view_layer.update()
 need([sn.primitive(g)for g in list(o.vertex_groups)[:1]]==groups_before,'Inherited group changed')
 need({'mesh':sn.mesh_snapshot(prior_union.data),'object':sn.primitive(prior_union)}==prior_union_before,'Existing V024 union changed')
 need([sn.primitive(m)for m in list(o.modifiers)[:2]]==mods_before,'Original chain changed after rollback check')
 need(sn.digest({'properties':sn.primitive(mat),'nodes':sn.tree_snapshot(mat.node_tree)})==mat_before,'Existing material changed')
 need(sha(src)==SOURCE_SHA and sha(pp)==hashes['plan']and sha(__file__)==hashes['builder']and sha(ROOT/'snapshot_support.py')==hashes['helper'],'Inputs changed')
 receipt={'status':'Unaccepted technical candidate; independent occupied-set/exterior/complement QA and actual visual gate required','hashes':hashes,'object':o.name,'owned_names':{'collection':coll.name,'group':group.name,'modifier':mask.name,'replacements':[x['name']for x in unions]},'raw_weight_ids':raw_ids,'evaluated_removed':sorted(selected),'input_evaluated_parts':parts,'unions':unions,'checks':{'closed_oriented':True,'positive_volume':True,'no_exact_duplicate_polygons':True,'no_strict_nonadjacent_transverse_triangle_crossings':True,'exact_evaluated_complement_face_records':True,'original_bevel_exact':True,'original_full_modifier_chain_exact':True,'existing_group_exact':True,'existing_v024_union_exact':True,'actual_owned_names_exact':True,'raw_rollback_mesh_attributes_exact':True,'existing_material_exact':True},'material_mapping':'Existing shared Geometry Position material; original object transform copied, no material/node edits','cross_group_strategy':'Four separate frame unions preserve inherited neighboring overlap; no global union/disjointness claim','source_saved':False,'rendered':False}
 temps=[]
 try:
  def tmp(dest,suffix):
   fd,path=tempfile.mkstemp(prefix='.v025-',suffix=suffix,dir=dest.parent);os.close(fd);p=Path(path);temps.append(p);return p
  model=tmp(out,'.blend');model.unlink();result=bpy.ops.wm.save_as_mainfile(filepath=str(model),copy=True,compress=True,check_existing=False);need('FINISHED'in result,'Save failed')
  need(sha(src)==SOURCE_SHA and sha(pp)==PLAN_SHA and sha(ROOT/'SCOPE.json')==SCOPE_SHA and sha(ROOT/'snapshot_support.py')==HELPER_SHA and sha(__file__)==hashes['builder'],'Inputs changed after save');receipt.update(candidate_sha256=sha(model),candidate_bytes=model.stat().st_size,source_unchanged=True)
  report=tmp(rp,'.json');report.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');publish([(model,out),(report,rp)]);print(json.dumps({'candidate':str(out),'sha256':receipt['candidate_sha256'],'unions':receipt['unions']}),flush=True)
 finally:
  for p in temps:
   if p.exists():p.unlink()
if __name__=='__main__':main()
