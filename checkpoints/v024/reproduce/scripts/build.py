"""Bounded exact evaluated-solid union. No rendering or canonical save."""
import argparse,collections,hashlib,json,os,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
SOURCE_SHA='c4b1dda3b8f70e4c8cb0171834b2150b6d7610f6296847362fd204b2dfa7ad51'
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
 plan=json.loads(pp.read_text());need(sha(src)==SOURCE_SHA==plan['source_sha256']and src.stat().st_size==plan['source_bytes'],'Source mismatch')
 hashes={'source':SOURCE_SHA,'plan':sha(pp),'builder':sha(__file__),'helper':sha(ROOT/'snapshot_support.py')}
 import bpy,bmesh
 from mathutils import Vector
 from mathutils.bvhtree import BVHTree
 from mathutils.geometry import intersect_ray_tri
 sys.path.insert(0,str(ROOT));import snapshot_support as sn
 need(not bpy.data.filepath,'Factory-empty Blender required');bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
 o=bpy.data.objects[plan['object']];need(o.type=='MESH'and o.data.users==1 and not o.data.shape_keys and not o.parent and not o.constraints and not o.animation_data,'Unexpected source object state')
 need(len(o.modifiers)==1 and o.modifiers[0].type=='BEVEL'and o.modifiers[0].use_clamp_overlap,'Source bevel state unexpected');bevel_before=sn.primitive(o.modifiers[0]);raw_before=sn.mesh_snapshot(o.data)
 need(not o.vertex_groups,'Source vertexgroups unexpected')
 mat=bpy.data.materials[plan['material']];need(o.data.materials[0]==mat,'Material mismatch')
 need(not any(l.from_node.bl_idname in ['ShaderNodeTexCoord','ShaderNodeObjectInfo','ShaderNodeParticleInfo','ShaderNodeGroup']for l in mat.node_tree.links),'Material object-coordinate dependencies require explicit review')
 mat_before=sn.digest({'properties':sn.primitive(mat),'nodes':sn.tree_snapshot(mat.node_tree)})
 for name,items in [(plan['collection'],bpy.data.collections),(plan['replacement'],bpy.data.objects),(plan['replacement'],bpy.data.meshes)]:need(name not in items,'Owned name collision')
 dg=bpy.context.evaluated_depsgraph_get();eo=o.evaluated_get(dg);em=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
 selected=set();raw_ids=[];parts=[]
 def face_record(mesh,f):
  return(tuple(tuple(mesh.vertices[i].co)for i in f.vertices),f.material_index,f.use_smooth)
 for pair in plan['mapping']:
  ids=pair['evaluated']['indices'];raw=pair['raw']['indices'];need(len(ids)==24 and len(raw)==8,'Unexpected component sizes');selected.update(ids);raw_ids.extend(raw)
  fs=[f for f in em.polygons if set(f.vertices)<=set(ids)];need(len(fs)==26 and all(f.material_index==0 for f in fs),'Evaluated component mismatch')
  need(not any(set(f.vertices)&set(ids) and not set(f.vertices)<=set(ids) for f in em.polygons),'Component is connected outside scope')
  need([list(min(em.vertices[i].co[j]for i in ids)for j in range(3)),list(max(em.vertices[i].co[j]for i in ids)for j in range(3))]==pair['evaluated']['bounds'],'Evaluated bounds mismatch')
  remap={old:i for i,old in enumerate(ids)};parts.append({'seed':pair['evaluated']['seed'],'vertices':[list(em.vertices[i].co)for i in ids],'faces':[[remap[i]for i in f.vertices]for f in fs],'smooth':[f.use_smooth for f in fs]})
 complement=collections.Counter(face_record(em,f)for f in em.polygons if not set(f.vertices)<=selected);input_total=len(em.vertices);eo.to_mesh_clear();need(len(selected)==144 and len(set(raw_ids))==48,'Selection cardinality mismatch')
 coll=bpy.data.collections.new(plan['collection']);bpy.context.scene.collection.children.link(coll);created=[]
 for i,part in enumerate(parts):
  me=bpy.data.meshes.new(plan['replacement']if i==0 else 'V024 temporary evaluated operand '+str(i));me.from_pydata(part['vertices'],[],part['faces']);me.materials.append(mat)
  for f,smooth in zip(me.polygons,part['smooth']):f.use_smooth=smooth
  me.update();obj=bpy.data.objects.new(me.name,me);coll.objects.link(obj);obj.matrix_world=o.matrix_world.copy();created.append(obj)
 union=created[0];steps=[]
 for operand in created[1:]:
  mod=union.modifiers.new('V024 temporary exact union','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=operand;mod.use_self=False;mod.use_hole_tolerant=False
  with bpy.context.temp_override(object=union,active_object=union,selected_objects=[union],selected_editable_objects=[union]):result=bpy.ops.object.modifier_apply(modifier=mod.name)
  need('FINISHED'in result,'Exact union failed');steps.append({'operand':operand.name,'vertices':len(union.data.vertices),'faces':len(union.data.polygons)})
  mesh=operand.data;bpy.data.objects.remove(operand,do_unlink=True);bpy.data.meshes.remove(mesh)
 union.name=plan['replacement'];union.data.name=plan['replacement'];need(not union.modifiers,'Unexpected unapplied union modifier')
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
 group=o.vertex_groups.new(name=plan['group']);group.add(raw_ids,1.0,'REPLACE');mask=o.modifiers.new(plan['modifier'],'MASK');mask.mode='VERTEX_GROUP';mask.vertex_group=group.name;mask.invert_vertex_group=True;mask.threshold=.5;mask.use_smooth=False
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();eo=o.evaluated_get(dg);em=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
 need(input_total-len(em.vertices)==144,'Mask did not remove exactly144evaluated vertices');need(collections.Counter(face_record(em,f)for f in em.polygons)==complement,'Evaluated complement changed');eo.to_mesh_clear()
 o.modifiers[0].is_active=bevel_before['is_active']
 bevel_after=sn.primitive(o.modifiers[0]);diff={k:[bevel_before.get(k),bevel_after.get(k)]for k in set(bevel_before)|set(bevel_after)if bevel_before.get(k)!=bevel_after.get(k)}
 print('BEVEL_DIFF',json.dumps(diff),flush=True)
 need(not diff,'Original global bevel changed')
 # Reversible raw-source proof: remove only owned weights, compare all raw mesh attrs, then restore.
 o.vertex_groups.remove(group);need(sn.mesh_snapshot(o.data)==raw_before,'Raw rollback source changed');group=o.vertex_groups.new(name=plan['group']);group.add(raw_ids,1.0,'REPLACE');mask.vertex_group=group.name;bpy.context.view_layer.update()
 need(sn.digest({'properties':sn.primitive(mat),'nodes':sn.tree_snapshot(mat.node_tree)})==mat_before,'Existing material changed')
 need(sha(src)==SOURCE_SHA and sha(pp)==hashes['plan']and sha(__file__)==hashes['builder']and sha(ROOT/'snapshot_support.py')==hashes['helper'],'Inputs changed')
 receipt={'status':'Unaccepted technical candidate; independent occupied-set/exterior/complement QA and actual visual gate required','hashes':hashes,'object':o.name,'owned_names':{k:plan[k]for k in ['collection','replacement','group','modifier']},'raw_weight_ids':raw_ids,'evaluated_removed':sorted(selected),'input_evaluated_parts':parts,'boolean_steps':steps,'union':{'vertices':len(union.data.vertices),'faces':len(union.data.polygons),'triangles':len(triangles),'signed_volume':volume},'checks':{'closed_oriented':True,'positive_volume':True,'no_exact_duplicate_polygons':True,'no_strict_nonadjacent_transverse_triangle_crossings':True,'exact_evaluated_complement_face_records':True,'original_bevel_exact':True,'raw_rollback_mesh_attributes_exact':True,'existing_material_exact':True},'material_mapping':'Existing shared Geometry Position material; original object transform copied, no material/node edits','deferred_components':20,'source_saved':False,'rendered':False}
 temps=[]
 try:
  def tmp(dest,suffix):
   fd,path=tempfile.mkstemp(prefix='.v024-',suffix=suffix,dir=dest.parent);os.close(fd);p=Path(path);temps.append(p);return p
  model=tmp(out,'.blend');model.unlink();result=bpy.ops.wm.save_as_mainfile(filepath=str(model),copy=True,compress=True,check_existing=False);need('FINISHED'in result,'Save failed')
  need(sha(src)==SOURCE_SHA,'Canonical source changed');receipt.update(candidate_sha256=sha(model),candidate_bytes=model.stat().st_size,source_unchanged=True)
  report=tmp(rp,'.json');report.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');publish([(model,out),(report,rp)]);print(json.dumps({'candidate':str(out),'sha256':receipt['candidate_sha256'],'union':receipt['union']}),flush=True)
 finally:
  for p in temps:
   if p.exists():p.unlink()
if __name__=='__main__':main()
