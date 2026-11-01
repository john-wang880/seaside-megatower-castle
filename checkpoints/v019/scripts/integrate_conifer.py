"""Explicit unaccepted one-tree integration; run only after final asset approval.
blender -b --disable-autoexec --python integrate_conifer.py -- --source ... --asset ...
 --asset-sha256 FINAL_SHA --output ... --report ... --snapshot-helper .../deep_snapshot.py
Never overwrites any output. Failure restores in-memory originals and removes owned imports.
"""
import argparse,sys,json,hashlib,collections,importlib.util,os
from pathlib import Path
SOURCE_SHA='c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd'
REJECTED_OLD_SHA='442e43e9af7ecfb8fe385c01f09f96c6eded6fef410a8dfe56eace6601c0fa27'
TARGET='V010 | woodland boughs with gate exit clearance'
COLLECTION='UNACCEPTED | v019 specialist foreground conifer'
GROUP='V019 candidate | reversible left tree foliage'
MODIFIER='V019 candidate | original foliage rollback mask'
SPECS=[('CONCEPT | radial articulated needle sprays','V019 candidate | articulated conifer foliage',['Fir needles — forest green','Sunlit needle tips','Cypress needles — deep blue green']),('CONCEPT | tapering connected boughs and shoots','V019 candidate | connected conifer boughs',['Pine bark'])]
SELECTED=tuple(range(90395,90693))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def parse():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['source','asset','asset-sha256','output','report','snapshot-helper']:p.add_argument('--'+n,required=True)
 return p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:])
def main():
 a=parse();source=Path(a.source).resolve();asset=Path(a.asset).resolve();output=Path(a.output).resolve();report=Path(a.report).resolve()
 assert len(a.asset_sha256)==64 and all(c in '0123456789abcdef' for c in a.asset_sha256),'Explicit final lowercase SHA required'
 assert a.asset_sha256!=REJECTED_OLD_SHA,'Pre-attachment asset must not be integrated'
 assert sha(source)==SOURCE_SHA and sha(asset)==a.asset_sha256
 assert len({source,asset,output,report})==4 and not output.exists() and not report.exists(),'No input/output alias or overwrite'
 assert output.suffix=='.blend' and report.suffix=='.json'
 import bpy
 spec=importlib.util.spec_from_file_location('integration_snapshot',str(Path(a.snapshot_helper).resolve()));sn=importlib.util.module_from_spec(spec);spec.loader.exec_module(sn)
 bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
 target=bpy.data.objects[TARGET]
 assert target.data.users==1 and not target.modifiers and not target.vertex_groups
 assert len(target.data.vertices)>max(SELECTED)
 for _,name,_ in SPECS:assert name not in bpy.data.objects and name not in bpy.data.meshes,'Owned-name collision'
 assert COLLECTION not in bpy.data.collections and GROUP not in target.vertex_groups and MODIFIER not in target.modifiers
 selected=set(SELECTED)
 removed=[f.index for f in target.data.polygons if all(v in selected for v in f.vertices)]
 assert len(removed)==496
 assert not any(any(v in selected for v in f.vertices) and not all(v in selected for v in f.vertices) for f in target.data.polygons),'Mask crosses connected component'
 def face(m,f):return (tuple(tuple(m.vertices[v].co) for v in f.vertices),f.material_index,f.use_smooth)
 complement=collections.Counter(face(target.data,f) for f in target.data.polygons if not all(v in selected for v in f.vertices))
 old_meshes={m.name:sn.mesh_snapshot(m) for m in bpy.data.meshes}
 old_mats={m.name:sn.digest(sn.tree_snapshot(m.node_tree)) for m in bpy.data.materials}
 # Track every library-created data ID so rollback cannot touch a pre-existing ID.
 id_types=['objects','meshes','materials','collections','images','node_groups','textures','actions','armatures','cameras','lights','worlds']
 initial={k:{v.as_pointer() for v in getattr(bpy.data,k)} for k in id_types}
 imported=[];group=None;mod=None;coll=None;reserved=[]
 try:
  expected_materials={n:bpy.data.materials[n] for _,_,names in SPECS for n in names}
  with bpy.data.libraries.load(str(asset),link=False) as (available,requested):
   assert all(n in available.objects for n,_,_ in SPECS)
   requested.objects=[n for n,_,_ in SPECS]
  imported=list(requested.objects)
  for obj,(oldname,newname,matnames) in zip(imported,SPECS):
   assert obj and obj.type=='MESH' and not obj.modifiers and not obj.constraints and not obj.animation_data and not obj.parent
   assert not obj.vertex_groups and not obj.data.shape_keys
   assert all(abs(obj.matrix_world[r][c]-(1 if r==c else 0))<1e-10 for r in range(4) for c in range(4))
   assert len(obj.material_slots)==len(matnames)
   # Imported duplicate suffixes are irrelevant: validate material order by original library names.
   for slot,name in zip(obj.material_slots,matnames):
    assert slot.material and (slot.material.name==name or slot.material.name.startswith(name+'.')),(slot.material.name,name)
   for j,name in enumerate(matnames):obj.data.materials[j]=expected_materials[name]
   obj.name=newname;obj.data.name=newname
   assert obj.name==newname and obj.data.name==newname
  coll=bpy.data.collections.new(COLLECTION);bpy.context.scene.collection.children.link(coll)
  for obj in imported:coll.objects.link(obj)
  # Drop only newly imported unused dependencies; no original ID is ever eligible.
  for key in ['materials','node_groups','images','textures','actions']:
   for data in list(getattr(bpy.data,key)):
    if data.as_pointer() not in initial[key] and data.users==0:getattr(bpy.data,key).remove(data)
  assert set(bpy.data.materials.keys())==set(old_mats),'Library left duplicate materials'
  group=target.vertex_groups.new(name=GROUP);group.add(SELECTED,1.0,'REPLACE')
  mod=target.modifiers.new(MODIFIER,'MASK');mod.vertex_group=group.name;mod.invert_vertex_group=True;mod.threshold=.5
  bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();eo=target.evaluated_get(dg);em=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
  try:assert collections.Counter(face(em,f) for f in em.polygons)==complement,'Non-target evaluated faces changed'
  finally:eo.to_mesh_clear()
  # Only weights are permitted on the source mesh: temporarily remove/restore group for exact raw snapshot.
  target.vertex_groups.remove(group);group=None
  assert all(sn.mesh_snapshot(bpy.data.meshes[n])==v for n,v in old_meshes.items()),'Original raw meshes changed'
  group=target.vertex_groups.new(name=GROUP);group.add(SELECTED,1.0,'REPLACE');mod.vertex_group=group.name
  assert {m.name:sn.digest(sn.tree_snapshot(m.node_tree)) for m in bpy.data.materials}==old_mats,'Material graph changed'
  assert not (set(bpy.data.objects.keys())-set(n for n in bpy.data.objects.keys() if bpy.data.objects[n].as_pointer() in initial['objects']))-{x[1] for x in SPECS}
  rows=[]
  for obj in imported:
   obj.data.calc_loop_triangles();rows.append({'object':obj.name,'mesh':obj.data.name,'vertices':len(obj.data.vertices),'polygons':len(obj.data.polygons),'triangles':len(obj.data.loop_triangles),'materials':[m.name for m in obj.data.materials],'matrix_world':[list(r) for r in obj.matrix_world]})
  receipt={'status':'UNACCEPTED ACTUAL-SCENE CANDIDATE','source_sha256':SOURCE_SHA,'asset_sha256':a.asset_sha256,'source':str(source),'asset':str(asset),'collection':COLLECTION,'objects':rows,'mask':{'object':TARGET,'group':GROUP,'modifier':MODIFIER,'vertex_ids':list(SELECTED),'removed_faces':removed,'invert_vertex_group':True,'threshold':.5,'show_in_editmode':mod.show_in_editmode,'show_on_cage':mod.show_on_cage,'use_smooth':mod.use_smooth},'allowed_deltas':['Two new mesh objects, one new collection','298 weights in one new group and one inverted MASK modifier on original visible foliage'],'checks':{'all_original_raw_meshes_exact_without_owned_weights':True,'non_target_evaluated_face_records_exact':True,'all_existing_material_graphs_exact':True,'original_wood_unmodified':True},'limits':['Independent full-source/evaluated-attribute preservation validation still required','Original entire woody object retained intentionally; exposed bough conflict is a visual-review question','Not a route-clearance or visual acceptance result']}
  for p in [output,report]:
   p.parent.mkdir(parents=True,exist_ok=True);fd=os.open(str(p),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd);reserved.append(p)
  bpy.context.preferences.filepaths.save_version=0
  bpy.ops.wm.save_as_mainfile(filepath=str(output),copy=True)
  assert sha(source)==SOURCE_SHA and sha(asset)==a.asset_sha256
  receipt.update(candidate_sha256=sha(output),candidate_bytes=output.stat().st_size,source_unchanged=True,asset_unchanged=True)
  report.write_text(json.dumps(receipt,indent=2));reserved.clear();print('INTEGRATION_PASS',receipt['candidate_sha256'],flush=True)
 except BaseException:
  if mod and mod.name in target.modifiers:target.modifiers.remove(mod)
  if group and group.name in target.vertex_groups:target.vertex_groups.remove(group)
  for key in id_types:
   for data in list(getattr(bpy.data,key)):
    if data.as_pointer() not in initial[key]:
     try:getattr(bpy.data,key).remove(data,do_unlink=True)
     except TypeError:getattr(bpy.data,key).remove(data)
  for p in reserved:p.unlink(missing_ok=True)
  assert sha(source)==SOURCE_SHA and sha(asset)==a.asset_sha256
  raise
if __name__=='__main__':main()
