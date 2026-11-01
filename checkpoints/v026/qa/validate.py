import sys
sys.dont_write_bytecode=True
if sys.flags.optimize:raise RuntimeError('Optimized Python refused')
import bpy,bmesh,json,hashlib,argparse,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import snapshot_support as ss
from complement import complement_snapshot
p=argparse.ArgumentParser()
for k in ['source','candidate','candidate-sha','report','geometry']:p.add_argument('--'+k,required=True)
p.add_argument('--negative',choices=['weight','hidden','material','old_union'])
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=Path(a.source);candidate=Path(a.candidate);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();hashes={'source':sha(source),'candidate':sha(candidate)}
assert hashes=={'source':'8a3590082c99a69d50d444f77165fae57fb611cf069cecda03fdf0c6c17cadd2','candidate':a.candidate_sha}
assert not Path(a.report).exists() and not Path(a.geometry).exists()
scope=json.loads((Path(__file__).parent/'SCOPE.json').read_text());name=scope['visible_object'];ids=set(scope['selected_raw_vertex_ids'])
def snap():
 s=ss.snap();s['collections']=ss.collections_snapshot();s['scene_custom']=dict(bpy.context.scene.items())
 for n in ['Traveler | full length ivory skirt','Traveler | purple-red shoulder cape','Traveler | white tunic']:s['visible_evaluated'][n],_=ss.render_semantic_with_ui_report(s['visible_evaluated'][n])
 return s
bpy.ops.wm.open_mainfile(filepath=str(source.resolve()),use_scripts=False);base=snap();o=bpy.data.objects[name];raw=ss.mesh_snapshot(o.data);hidden_before=ss.primitive(bpy.data.objects[scope['hidden_original_object']]);assert o.data.users==2
dg=bpy.context.evaluated_depsgraph_get();eo=o.evaluated_get(dg);me=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg);base_eval=ss.mesh_snapshot(me);kept=[f for f in me.polygons if not ids.intersection(f.vertices)];maps={'POINT':[v.index for v in me.vertices if v.index not in ids],'EDGE':[e.index for e in me.edges if not ids.intersection(e.vertices)],'FACE':[f.index for f in kept],'CORNER':[i for f in kept for i in f.loop_indices]};expected=complement_snapshot(me,maps)
solids=[{'seed':s['seed'],'faces':[[list(o.matrix_world@me.vertices[i].co)for i in me.polygons[fi].vertices]for fi in s['face_ids']]}for s in scope['components']]
eo.to_mesh_clear();bpy.ops.wm.open_mainfile(filepath=str(candidate.resolve()),use_scripts=False);o=bpy.data.objects[name];hidden=bpy.data.objects[scope['hidden_original_object']];original=bpy.data.meshes[scope['original_shared_mesh']];u=bpy.data.objects[scope['union_object']]
if a.negative=='weight':o.vertex_groups[scope['group']].add([8],1.,'REPLACE')
if a.negative=='hidden':original.vertices[0].co.x+=.1
if a.negative=='material':u.data.materials[0]=bpy.data.materials[scope['original_data_slot_material']]
if a.negative=='old_union':bpy.data.objects['V024 | exact evaluated rear stepped union'].data.vertices[0].co.x+=.1
assert hidden.data==original and original.users==1 and ss.mesh_snapshot(original)==raw and ss.primitive(hidden)==hidden_before
assert o.data.name==scope['owned_derivative_mesh']and o.data.users==1 and o.data!=original
assert len(o.vertex_groups)==1 and o.vertex_groups[0].name==scope['group']
assert [(v.index,[(g.group,g.weight)for g in v.groups])for v in o.data.vertices if v.groups]==[(i,[(0,1.)])for i in sorted(ids)]
assert [(s.link,s.material.name)for s in o.material_slots]==[('OBJECT',scope['effective_material'])]
assert [m.name for m in o.data.materials]==[scope['original_data_slot_material']]
assert len(o.modifiers)==1;m=o.modifiers[0];assert m.name==scope['modifier']and m.type=='MASK'and m.mode=='VERTEX_GROUP'and m.vertex_group==scope['group']and m.invert_vertex_group and m.threshold==.5 and not m.use_smooth and m.show_render and m.show_viewport and m.armature is None
cm=bpy.data.meshes.new('QA native Mask defaults');co=bpy.data.objects.new('QA native Mask defaults',cm);co.vertex_groups.new(name=scope['group']);ref=co.modifiers.new(scope['modifier'],'MASK');ref.vertex_group=scope['group'];ref.invert_vertex_group=True;ref.threshold=.5;ref.use_smooth=False
mp,rp=ss.primitive(m),ss.primitive(ref);maskdiff={k:[mp[k],rp.get(k)]for k in mp if mp[k]!=rp.get(k)};assert set(maskdiff)<={'persistent_uid','execution_time'},maskdiff;bpy.data.objects.remove(co);bpy.data.meshes.remove(cm)
assert u.data.name==scope['union_mesh']and u.data.users==1 and len(u.data.vertices)==20 and len(u.data.polygons)==14
assert not u.modifiers and not u.vertex_groups and not u.parent and not u.constraints and not u.animation_data and not u.hide_render and not u.hide_viewport and not u.hide_get()
assert [list(r)for r in u.matrix_world]==[[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]]
assert [s.material.name for s in u.material_slots]==[scope['effective_material']]
assert all(f.material_index==0 and not f.use_smooth for f in u.data.polygons)
dg=bpy.context.evaluated_depsgraph_get();eo=o.evaluated_get(dg);me=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg);assert complement_snapshot(me,maps,True)==expected;eo.to_mesh_clear()
bm=bmesh.new();bm.from_mesh(u.data);assert all(e.is_manifold and e.is_contiguous for e in bm.edges);volume=bm.calc_volume(signed=True);assert volume>0;bm.free();u.data.calc_loop_triangles()
geometry={'source_sha256':hashes['source'],'candidate_sha256':hashes['candidate'],'original_convex_solids':solids,'union_triangles':[[list(u.matrix_world@u.data.vertices[i].co)for i in t.vertices]for t in u.data.loop_triangles],'union_polygons':[[list(u.matrix_world@u.data.vertices[i].co)for i in f.vertices]for f in u.data.polygons],'union_volume_blender':volume}
active=snap();non=copy.deepcopy(active['visible_evaluated']);non.pop(name);non.pop(u.name);old=copy.deepcopy(base['visible_evaluated']);old.pop(name);assert non==old,'Other active evaluated mesh changed'
for _ in range(2):
 m.show_viewport=m.show_render=False;u.hide_viewport=u.hide_render=True;bpy.context.view_layer.update();eo=o.evaluated_get(dg);me=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg);low=ss.mesh_snapshot(me);payload=low['debug_payload'];assert payload['weights']==[(i,[(0,1.)])for i in sorted(ids)];payload['weights']=[];low['hash']=ss.digest(payload);assert low==base_eval;eo.to_mesh_clear()
 m.show_viewport=m.show_render=True;u.hide_viewport=u.hide_render=False;bpy.context.view_layer.update();assert snap()==active
# Exact source graph restored, not just LOW visibility.
derivative=o.data;o.modifiers.remove(m);o.vertex_groups.remove(o.vertex_groups[0]);assert ss.mesh_snapshot(derivative)==raw;o.data=original;bpy.data.meshes.remove(derivative);um=u.data;bpy.data.objects.remove(u,do_unlink=True);bpy.data.meshes.remove(um);bpy.data.collections.remove(bpy.data.collections[scope['collection']]);bpy.context.view_layer.update();assert original.users==2 and hidden.data==o.data
normal=snap();checks={k:normal[k]==base[k]for k in base};assert all(checks.values()),[k for k,v in checks.items()if not v]
assert sha(source)==hashes['source']and sha(candidate)==hashes['candidate'];Path(a.geometry).write_text(json.dumps(geometry));Path(a.report).write_text(json.dumps({'pass':True,'hashes':hashes,'normalized_full_scene_checks':checks,'native_low_and_repeat':True,'full_pointer_rollback_users2':True,'active_original_users1_derivative_users1':True,'shared_hidden_original_exact':True,'effective_object_material_exact':True,'complement_all_attributes_exact':True,'closed_oriented_positive':True,'scope':'Boundary and adjacency proofs separate; models never saved.'},indent=2));print('V026 PRESERVATION PASS')
