import bpy,sys,json,hashlib,collections,copy,argparse,bmesh
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import snapshot_support as ss
from complement import complement_snapshot
if sys.flags.optimize:raise RuntimeError('Assertions required')
p=argparse.ArgumentParser()
for k in ['source','candidate','candidate-sha','union','group','mask','collection','report','geometry']:p.add_argument('--'+k,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=Path(a.source).resolve();candidate=Path(a.candidate).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();hashes={'source':sha(source),'candidate':sha(candidate)}
assert hashes['source']=='c4b1dda3b8f70e4c8cb0171834b2150b6d7610f6296847362fd204b2dfa7ad51' and hashes['candidate']==a.candidate_sha
assert not Path(a.report).exists() and not Path(a.geometry).exists()
TARGET='V008 | gallery with genuine eastern approach portal';seeds=[56,80,104,128,152,176];ids=set(range(16,64))
def snap():
 s=ss.snap();s['collections']=ss.collections_snapshot();s['scene_custom']=dict(bpy.context.scene.items())
 for n in ['Traveler | full length ivory skirt','Traveler | purple-red shoulder cape','Traveler | white tunic']:s['visible_evaluated'][n],_=ss.render_semantic_with_ui_report(s['visible_evaluated'][n])
 return s
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);base=snap();o=bpy.data.objects[TARGET];assert len(o.modifiers)==1 and o.modifiers[0].type=='BEVEL' and not o.vertex_groups
oldmod=ss.primitive(o.modifiers[0]);dg=bpy.context.evaluated_depsgraph_get();eo=o.evaluated_get(dg);me=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
parent=list(range(len(me.vertices)))
def root(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
for e in me.edges:
 x,y=map(root,e.vertices);parent[max(x,y)]=min(x,y)
removed={v.index for v in me.vertices if root(v.index)in seeds};assert len(removed)==144
faces=[f for f in me.polygons if not removed.intersection(f.vertices)];maps={'POINT':[v.index for v in me.vertices if v.index not in removed],'EDGE':[e.index for e in me.edges if not removed.intersection(e.vertices)],'FACE':[f.index for f in faces],'CORNER':[i for f in faces for i in f.loop_indices]};expected=complement_snapshot(me,maps)
solids=[]
for seed in seeds:
 fs=[f for f in me.polygons if root(f.vertices[0])==seed];assert len(fs)==26
 solids.append({'seed':seed,'faces':[[list(o.matrix_world@me.vertices[i].co)for i in f.vertices]for f in fs]})
eo.to_mesh_clear();bpy.ops.wm.open_mainfile(filepath=str(candidate),use_scripts=False);o=bpy.data.objects[TARGET];assert len(o.modifiers)==2 and ss.primitive(o.modifiers[0])==oldmod
assert len(o.vertex_groups)==1 and o.vertex_groups[0].name==a.group
assert [(v.index,[(g.group,g.weight)for g in v.groups])for v in o.data.vertices if v.groups]==[(i,[(0,1.)])for i in sorted(ids)]
m=o.modifiers[1];assert m.name==a.mask and m.type=='MASK' and m.mode=='VERTEX_GROUP' and m.vertex_group==a.group and m.invert_vertex_group and m.threshold==.5 and not m.use_smooth and m.show_viewport and m.show_render and m.armature is None
# Compare all native mask properties to a temporary native control.
cm=bpy.data.meshes.new('QA mask control');co=bpy.data.objects.new('QA mask control',cm);co.vertex_groups.new(name=a.group);control_bevel=co.modifiers.new('QA existing bevel','BEVEL');ref=co.modifiers.new(a.mask,'MASK');ref.vertex_group=a.group;ref.invert_vertex_group=True;ref.threshold=.5;ref.use_smooth=False;control_bevel.is_active=True
mp,rp=ss.primitive(m),ss.primitive(ref);diff={k:[mp[k],rp.get(k)]for k in mp if mp[k]!=rp.get(k)};assert set(diff)<={'persistent_uid','execution_time'},diff;bpy.data.objects.remove(co);bpy.data.meshes.remove(cm)
dg=bpy.context.evaluated_depsgraph_get();eo=o.evaluated_get(dg);me=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg);got=complement_snapshot(me,maps,True);assert got==expected,('Complement differences',[k for k in got if got[k]!=expected[k]]);eo.to_mesh_clear()
u=bpy.data.objects[a.union];assert u.type=='MESH' and u.data.users==1 and not u.modifiers and not u.vertex_groups and not u.constraints and not u.parent and not u.animation_data and not u.hide_get()and not u.hide_render and not u.hide_viewport
assert [list(r)for r in u.matrix_world]==[[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]]
assert [m.name for m in u.data.materials]==['Citadel • aged gallery grey'];assert all(f.material_index==0 and not f.use_smooth for f in u.data.polygons)
bm=bmesh.new();bm.from_mesh(u.data);assert all(e.is_manifold and e.is_contiguous for e in bm.edges);volume=bm.calc_volume(signed=True);assert volume>0;bm.free();u.data.calc_loop_triangles()
geometry={'source_sha256':hashes['source'],'candidate_sha256':hashes['candidate'],'original_convex_solids':solids,'union_triangles':[[list(u.matrix_world@u.data.vertices[i].co)for i in t.vertices]for t in u.data.loop_triangles],'union_polygons':[[list(u.matrix_world@u.data.vertices[i].co)for i in f.vertices]for f in u.data.polygons],'union_volume_blender':volume}
active=snap();non=copy.deepcopy(active['visible_evaluated']);non.pop(TARGET);non.pop(u.name);old=copy.deepcopy(base['visible_evaluated']);old.pop(TARGET);assert non==old,'Other active evaluated geometry changed'
for _ in range(2):
 for enabled in [False,True]:
  m.show_viewport=m.show_render=enabled;u.hide_viewport=u.hide_render=not enabled;bpy.context.view_layer.update()
assert snap()==active,'Repeated state drift'
# Removal of only owned additions proves exact source rollback, including raw deform arrays.
o.modifiers.remove(m);o.vertex_groups.remove(o.vertex_groups[0]);mesh=u.data;bpy.data.objects.remove(u,do_unlink=True);bpy.data.meshes.remove(mesh);bpy.data.collections.remove(bpy.data.collections[a.collection]);bpy.context.view_layer.update();normal=snap();checks={k:normal[k]==base[k]for k in base};assert all(checks.values()),[k for k,v in checks.items()if not v]
assert sha(source)==hashes['source'] and sha(candidate)==hashes['candidate']
Path(a.geometry).write_text(json.dumps(geometry));Path(a.report).write_text(json.dumps({'pass':True,'input_sha256':hashes,'normalized_source_checks':checks,'actual_post_bevel_complement_exact':True,'kept_domains':{k:len(v)for k,v in maps.items()},'native_mask_runtime_differences':diff,'repeated_state_exact':True,'all_input_files_unchanged':True,'closed_consistent_positive_union':True,'scope':'No geometry acceptance from this export alone; run independent boundary partition.'},indent=2));print('PRESERVATION EXPORT PASS')
