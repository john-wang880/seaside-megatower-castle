"""Opt-in exact two-pair box union candidate; canonical source is never saved.
Blender --background --disable-autoexec --python-exit-code 1 --python build.py --
 --source SOURCE --plan PLAN --output NEW.blend --report NEW.json
"""
import argparse,sys,json,hashlib,collections,os,tempfile
from pathlib import Path
SHA='673dbbadca22d3dd45dc2f2eb5bde4a9e66851c1ca137da5c2570efc67c77614'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not sys.flags.optimize,'Assertions must remain enabled'
 ap=argparse.ArgumentParser(description=__doc__)
 for k in ['source','plan','output','report']:ap.add_argument('--'+k,required=True)
 a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);paths=[Path(getattr(a,k))for k in ['source','plan','output','report']]
 assert not any(p.is_symlink()for p in paths),'No symlink paths'
 src,pp,out,rp=[p.resolve()for p in paths];assert len({src,pp,out,rp})==4 and not out.exists() and not rp.exists()
 assert out.suffix=='.blend' and rp.suffix=='.json' and sha(src)==SHA
 plan=json.loads(pp.read_text());assert plan['source_sha256']==SHA and len(plan['pairs'])==2
 code_sha=sha(__file__);plan_sha=sha(pp);helper_path=Path(__file__).resolve().with_name('deep_snapshot.py');helper_sha=sha(helper_path)
 import bpy,bmesh
 from mathutils import Matrix
 sys.path.insert(0,str(Path(__file__).resolve().parent));from deep_snapshot import mesh_snapshot,tree_snapshot,digest
 bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False)
 assert plan['collection']not in bpy.data.collections
 oldmeshes={m.name:mesh_snapshot(m)for m in bpy.data.meshes};oldmats={m.name:digest(tree_snapshot(m.node_tree))for m in bpy.data.materials}
 oldworld=digest(tree_snapshot(bpy.context.scene.world.node_tree));initial={k:{v.as_pointer()for v in getattr(bpy.data,k)}for k in ['objects','meshes','collections']};prepared=[]
 def face(m,f):return(tuple(tuple(m.vertices[i].co)for i in f.vertices),f.material_index,f.use_smooth)
 for sp in plan['pairs']:
  o=bpy.data.objects[sp['target']];assert o.type=='MESH' and o.data.users==1 and not o.modifiers and not o.vertex_groups and not o.data.shape_keys and not o.constraints and not o.animation_data and not o.parent
  assert all(o.matrix_world[r][c]==(1 if r==c else 0)for r in range(4)for c in range(4))
  assert sp['union_object']not in bpy.data.objects and sp['union_object']not in bpy.data.meshes
  assert o.data.materials[0].name==sp['material'];mat=o.data.materials[0]
  assert not any(l.from_node.bl_idname in ['ShaderNodeTexCoord','ShaderNodeObjectInfo','ShaderNodeParticleInfo']for l in mat.node_tree.links),'Mapping depends on object identity, UV or bounds'
  assert not any(n.bl_idname=='ShaderNodeGroup'for n in mat.node_tree.nodes),'Nested material mapping requires independent audit'
  selected=sorted(v['id']for c in sp['components']for v in c['vertices']);assert len(selected)==16 and len(set(selected))==16
  for comp in sp['components']:
   assert len(comp['vertices'])==8 and len(comp['faces'])==6
   expected={tuple(v['co'])for v in comp['vertices']};lo,hi=comp['bounds']
   assert expected=={(x,y,z)for x in[lo[0],hi[0]]for y in[lo[1],hi[1]]for z in[lo[2],hi[2]]}
   for v in comp['vertices']:assert tuple(o.data.vertices[v['id']].co)==tuple(v['co'])
   for f in comp['faces']:
    actual=o.data.polygons[f['id']];assert tuple(actual.vertices)==tuple(f['vertices']) and actual.material_index==0 and not actual.use_smooth
  c0,c1=sp['components'];assert c0['bounds'][0][1:]==c1['bounds'][0][1:] and c0['bounds'][1][1:]==c1['bounds'][1][1:]
  assert max(c0['bounds'][0][0],c1['bounds'][0][0])<min(c0['bounds'][1][0],c1['bounds'][1][0])
  chosen=set(selected);assert not any(bool(chosen.intersection(f.vertices)) and not set(f.vertices)<=chosen for f in o.data.polygons)
  assert sum(set(f.vertices)<=chosen for f in o.data.polygons)==12
  complement=collections.Counter(face(o.data,f)for f in o.data.polygons if not set(f.vertices)<=chosen)
  prepared.append((sp,o,selected,complement))
 createdmods=[];createdgroups=[];published=[];temp=None
 try:
  coll=bpy.data.collections.new(plan['collection']);bpy.context.scene.collection.children.link(coll);rows=[]
  for sp,o,ids,complement in prepared:
   group=o.vertex_groups.new(name=sp['group']);createdgroups.append((o,group.name));group.add(ids,1,'REPLACE')
   mod=o.modifiers.new(sp['modifier'],'MASK');createdmods.append((o,mod.name));mod.mode='VERTEX_GROUP';mod.vertex_group=group.name;mod.invert_vertex_group=True;mod.threshold=.5;mod.use_smooth=False
   lo=[min(c['bounds'][0][k]for c in sp['components'])for k in range(3)];hi=[max(c['bounds'][1][k]for c in sp['components'])for k in range(3)]
   vs=[(x,y,z)for x in[lo[0],hi[0]]for y in[lo[1],hi[1]]for z in[lo[2],hi[2]]];faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
   me=bpy.data.meshes.new(sp['union_object']);me.from_pydata(vs,[],faces);me.materials.append(bpy.data.materials[sp['material']]);me.update();ob=bpy.data.objects.new(sp['union_object'],me);coll.objects.link(ob)
   bm=bmesh.new();bm.from_mesh(me);assert all(e.is_manifold for e in bm.edges)and bm.calc_volume(signed=True)>0;volume=bm.calc_volume(signed=True);bm.free()
   bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();eo=o.evaluated_get(dg);em=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
   try:assert collections.Counter(face(em,f)for f in em.polygons)==complement,'Non-target face records changed'
   finally:eo.to_mesh_clear()
   rows.append({'target':o.name,'selected_vertices':ids,'removed_faces':[f['id']for c in sp['components']for f in c['faces']],'new_object':ob.name,'bounds':[lo,hi],'volume':volume,'material':sp['material'],'group':group.name,'modifier':mod.name,'vertices':8,'polygons':6,'triangles':12})
  # Only deliberate owned weights may differ in original raw mesh data.
  for sp,o,ids,_ in prepared:o.vertex_groups.remove(o.vertex_groups[sp['group']])
  assert all(mesh_snapshot(bpy.data.meshes[n])==v for n,v in oldmeshes.items()),'Raw original mesh changed beyond owned weights'
  for sp,o,ids,_ in prepared:
   g=o.vertex_groups.new(name=sp['group']);g.add(ids,1,'REPLACE');o.modifiers[sp['modifier']].vertex_group=g.name
  assert oldmats=={m.name:digest(tree_snapshot(m.node_tree))for m in bpy.data.materials}
  assert oldworld==digest(tree_snapshot(bpy.context.scene.world.node_tree)) and sha(src)==SHA and sha(pp)==plan_sha and sha(__file__)==code_sha and sha(helper_path)==helper_sha
  receipt={'status':'UNACCEPTED technical surface-union candidate','source_sha256':SHA,'plan_sha256':plan_sha,'script_sha256':code_sha,'snapshot_helper_sha256':helper_sha,'objects':rows,'checks':{'all_original_raw_meshes_exact_except_explicit_weights':True,'non_target_evaluated_face_records_exact':True,'original_material_graphs_and_world_exact':True,'analytic_pair_unions_exact_boxes':True},'allowed_deltas':['Two owned inverted Mask modifiers and two16-vertex weight groups','Two8-vertex union box meshes/objects in one owned collection'],'rollback':'Disable BOTH owned masks and hide BOTH union objects together. Raw source components retained.','limits':['Independent full-source and evaluated-attribute QA required','Visual disappearance of artifacts not yet tested; no structural certification']}
  out.parent.mkdir(parents=True,exist_ok=True);rp.parent.mkdir(parents=True,exist_ok=True)
  fd,tmp=tempfile.mkstemp(prefix='.v021-',suffix='.blend',dir=out.parent);os.close(fd);temp=Path(tmp)
  bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(temp),copy=True)
  assert sha(src)==SHA and sha(pp)==plan_sha and sha(__file__)==code_sha and sha(helper_path)==helper_sha
  receipt.update(candidate_sha256=sha(temp),candidate_bytes=temp.stat().st_size,source_unchanged=True)
  os.link(temp,out);published.append(out)
  with rp.open('x',encoding='utf-8')as f:published.append(rp);json.dump(receipt,f,indent=2)
  temp.unlink();temp=None;published.clear();print('UNION_BUILD_PASS',receipt['candidate_sha256'])
 except BaseException:
  for o,n in createdmods:
   if n in o.modifiers:o.modifiers.remove(o.modifiers[n])
  for o,n in createdgroups:
   if n in o.vertex_groups:o.vertex_groups.remove(o.vertex_groups[n])
  for k in ['objects','meshes','collections']:
   for q in list(getattr(bpy.data,k)):
    if q.as_pointer()not in initial[k]:getattr(bpy.data,k).remove(q,do_unlink=True)
  for p in published:p.unlink(missing_ok=True)
  if temp:temp.unlink(missing_ok=True)
  assert sha(src)==SHA
  raise
if __name__=='__main__':main()
