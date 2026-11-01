import bpy,sys,json,hashlib,copy,argparse,bmesh
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import snapshot_support as ss
from complement import complement_snapshot
if sys.flags.optimize:raise RuntimeError('Assertions required')
p=argparse.ArgumentParser()
for k in ['source','candidate','candidate-sha','scope','report','geometry']:p.add_argument('--'+k,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=Path(a.source).resolve();candidate=Path(a.candidate).resolve();scope=json.loads(Path(a.scope).read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();hashes={'source':sha(source),'candidate':sha(candidate)};assert hashes['source']==scope['source_sha256']=='89f9f6a8a57103d99100935b96624469ddf1fd52b9703e0d9177a352e735c856'and hashes['candidate']==a.candidate_sha;assert not Path(a.report).exists()and not Path(a.geometry).exists();TARGET=scope['target'];ids={i for g in scope['groups']for i in g['raw_vertex_ids']};seeds={i for g in scope['groups']for i in g['evaluated_seeds']};assert len(ids)==160 and len(seeds)==20

def snap():
 s=ss.snap();s['collections']=ss.collections_snapshot();s['scene_custom']=dict(bpy.context.scene.items())
 for n in ['Traveler | full length ivory skirt','Traveler | purple-red shoulder cape','Traveler | white tunic']:s['visible_evaluated'][n],_=ss.render_semantic_with_ui_report(s['visible_evaluated'][n])
 return s

def weights(me):return [(v.index,[(g.group,g.weight)for g in v.groups])for v in me.vertices if v.groups]
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);base=snap();o=bpy.data.objects[TARGET];oldmods=[ss.primitive(m)for m in o.modifiers];oldgroups=[ss.primitive(g)for g in o.vertex_groups];oldweights=weights(o.data);assert len(oldmods)==2 and len(oldgroups)==1 and len(oldweights)==48;dg=bpy.context.evaluated_depsgraph_get();eo=o.evaluated_get(dg);me=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg);parent=list(range(len(me.vertices)))
def root(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
for e in me.edges:
 x,y=map(root,e.vertices);parent[max(x,y)]=min(x,y)
removed={v.index for v in me.vertices if root(v.index)in seeds};assert len(removed)==480;faces=[f for f in me.polygons if not removed.intersection(f.vertices)];maps={'POINT':[v.index for v in me.vertices if v.index not in removed],'EDGE':[e.index for e in me.edges if not removed.intersection(e.vertices)],'FACE':[f.index for f in faces],'CORNER':[i for f in faces for i in f.loop_indices]};expected=complement_snapshot(me,maps);expected_weights=[(i,w)for i,w in weights(me)if i not in removed];groups=[]
for g in scope['groups']:
 solids=[]
 for seed in g['evaluated_seeds']:
  fs=[f for f in me.polygons if root(f.vertices[0])==seed];assert len(fs)==26
  solids.append({'seed':seed,'faces':[[list(o.matrix_world@me.vertices[i].co)for i in f.vertices]for f in fs]})
 groups.append({'ordinal':g['ordinal'],'plane_y':g['plane_y'],'object':g['replacement_object'],'original_convex_solids':solids})
eo.to_mesh_clear();bpy.ops.wm.open_mainfile(filepath=str(candidate),use_scripts=False);o=bpy.data.objects[TARGET];assert len(o.modifiers)==3 and [ss.primitive(m)for m in list(o.modifiers)[:2]]==oldmods;assert len(o.vertex_groups)==2 and [ss.primitive(g)for g in list(o.vertex_groups)[:1]]==oldgroups and o.vertex_groups[1].name==scope['new_group'];assert weights(o.data)==sorted(oldweights+[(i,[(1,1.)])for i in ids]),'Raw old/new weights changed'
m=o.modifiers[2];assert m.name==scope['new_modifier']and m.type=='MASK'and m.mode=='VERTEX_GROUP'and m.vertex_group==scope['new_group']and m.invert_vertex_group and m.threshold==.5 and not m.use_smooth and m.show_viewport and m.show_render and m.armature is None
cm=bpy.data.meshes.new('QA native mask control');co=bpy.data.objects.new('QA native mask control',cm);co.vertex_groups.new(name='existing');co.vertex_groups.new(name=scope['new_group']);bm=co.modifiers.new('existing BEVEL','BEVEL');co.modifiers.new('existing MASK','MASK');ref=co.modifiers.new(scope['new_modifier'],'MASK');ref.vertex_group=scope['new_group'];ref.invert_vertex_group=True;ref.threshold=.5;ref.use_smooth=False;bm.is_active=True;mp,rp=ss.primitive(m),ss.primitive(ref);diff={k:[mp[k],rp.get(k)]for k in mp if mp[k]!=rp.get(k)};assert set(diff)<={'persistent_uid','execution_time'},diff;bpy.data.objects.remove(co);bpy.data.meshes.remove(cm)
dg=bpy.context.evaluated_depsgraph_get();eo=o.evaluated_get(dg);me=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg);got=complement_snapshot(me,maps,True);assert got==expected,('Complement attributes',[k for k in got if got[k]!=expected[k]]);assert [(maps['POINT'][i],w)for i,w in weights(me)]==expected_weights,'Kept evaluated deform weights changed';eo.to_mesh_clear();unions=[]
for g in groups:
 u=bpy.data.objects[g['object']];assert u.type=='MESH'and u.data.users==1 and not u.modifiers and not u.vertex_groups and not u.constraints and not u.parent and not u.animation_data and not u.hide_get()and not u.hide_render and not u.hide_viewport;assert [list(r)for r in u.matrix_world]==[[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]];assert [m.name for m in u.data.materials]==[scope['material']]and all(f.material_index==0 and not f.use_smooth for f in u.data.polygons)
 bm=bmesh.new();bm.from_mesh(u.data);assert all(e.is_manifold and e.is_contiguous for e in bm.edges);v=bm.calc_volume(signed=True);assert v>0;bm.free();u.data.calc_loop_triangles();g.update({'union_triangles':[[list(u.matrix_world@u.data.vertices[i].co)for i in t.vertices]for t in u.data.loop_triangles],'union_polygons':[[list(u.matrix_world@u.data.vertices[i].co)for i in f.vertices]for f in u.data.polygons],'union_volume_blender':v});unions.append(u)
active=snap();non=copy.deepcopy(active['visible_evaluated']);non.pop(TARGET)
for u in unions:non.pop(u.name)
old=copy.deepcopy(base['visible_evaluated']);old.pop(TARGET);assert non==old,'Other active evaluated geometry changed, including V024 union'
for _ in range(2):
 for enabled in [False,True]:
  m.show_viewport=m.show_render=enabled
  for u in unions:u.hide_viewport=u.hide_render=not enabled
  bpy.context.view_layer.update()
assert snap()==active,'Repeated state drift'
o.modifiers.remove(m);o.vertex_groups.remove(o.vertex_groups[1])
for u in unions:
 mesh=u.data;bpy.data.objects.remove(u,do_unlink=True);bpy.data.meshes.remove(mesh)
bpy.data.collections.remove(bpy.data.collections[scope['collection']]);bpy.context.view_layer.update();normal=snap();checks={k:normal[k]==base[k]for k in base};assert all(checks.values()),[k for k,v in checks.items()if not v];assert sha(source)==hashes['source']and sha(candidate)==hashes['candidate'];Path(a.geometry).write_text(json.dumps({'source_sha256':hashes['source'],'candidate_sha256':hashes['candidate'],'groups':groups}));Path(a.report).write_text(json.dumps({'pass':True,'input_sha256':hashes,'normalized_source_checks':checks,'all_kept_evaluated_attributes_and_deform_weights_exact':True,'old_v024_modifiers_group_union_protected':True,'kept_domains':{k:len(v)for k,v in maps.items()},'native_mask_runtime_differences':diff,'repeated_state_exact':True,'all_inputs_unchanged':True,'each_union_closed_consistent_positive':True,'scope':'Four individual union objects; inter-group original volume overlaps deliberately preserved.'},indent=2));print('FOUR GROUP PRESERVATION PASS')
