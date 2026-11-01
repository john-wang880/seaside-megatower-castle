import bpy,sys,json,hashlib,copy,collections,bmesh
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parent))
import snapshot_support as ss
from complement import complement_snapshot
from common import inputs,sha
a,source,candidate,report_path,plan=inputs()
hashes={'source':sha(source),'candidate':sha(candidate)}
def snap():
 r=ss.snap();r['collections']=ss.collections_snapshot();r['scene_custom']=dict(bpy.context.scene.items())
 for n in ['Traveler | full length ivory skirt','Traveler | purple-red shoulder cape','Traveler | white tunic']:
  r['visible_evaluated'][n],_=ss.render_semantic_with_ui_report(r['visible_evaluated'][n])
 return r
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False)
base=snap();maps={};comps={};rawprops={}
for sp in plan['pairs']:
 o=bpy.data.objects[sp['target']];m=o.data;ids={v['id'] for c in sp['components'] for v in c['vertices']};faces=[f for f in m.polygons if not ids.intersection(f.vertices)]
 assert len(m.polygons)-len(faces)==12
 mp={'POINT':[v.index for v in m.vertices if v.index not in ids],'EDGE':[e.index for e in m.edges if not ids.intersection(e.vertices)],'FACE':[f.index for f in faces],'CORNER':[i for f in faces for i in f.loop_indices]}
 maps[o.name]=mp;comps[o.name]=complement_snapshot(m,mp);rawprops[o.name]=ss.primitive(o)
bpy.ops.wm.open_mainfile(filepath=str(candidate),use_scripts=False)
checks={};rows=[];dg=bpy.context.evaluated_depsgraph_get()
for sp in plan['pairs']:
 o=bpy.data.objects[sp['target']];ids={v['id'] for c in sp['components'] for v in c['vertices']};mod=o.modifiers[0]
 assert len(o.modifiers)==len(o.vertex_groups)==1 and o.vertex_groups[0].name==sp['group']
 assert [(v.index,[(g.group,g.weight) for g in v.groups]) for v in o.data.vertices if v.groups]==[(i,[(0,1.0)]) for i in sorted(ids)]
 assert mod.name==sp['modifier'] and mod.type=='MASK' and mod.mode=='VERTEX_GROUP' and mod.vertex_group==sp['group'] and mod.invert_vertex_group and mod.threshold==.5 and not mod.use_smooth and mod.show_viewport and mod.show_render and mod.armature is None
 eo=o.evaluated_get(dg);me=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
 got=complement_snapshot(me,maps[o.name],True);assert got==comps[o.name],('complement',o.name,[k for k in got if got[k]!=comps[o.name][k]])
 eo.to_mesh_clear()
 u=bpy.data.objects[sp['union_object']];m=u.data
 lo=[min(c['bounds'][0][k] for c in sp['components']) for k in range(3)];hi=[max(c['bounds'][1][k] for c in sp['components']) for k in range(3)]
 assert len(m.vertices)==8 and len(m.polygons)==6 and {tuple(v.co) for v in m.vertices}=={(x,y,z)for x in[lo[0],hi[0]]for y in[lo[1],hi[1]]for z in[lo[2],hi[2]]}
 assert [list(r) for r in u.matrix_world]==[[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]] and not u.modifiers and not u.vertex_groups and not u.hide_render and not u.hide_viewport
 assert [x.name for x in m.materials]==[sp['material']] and all(f.material_index==0 and not f.use_smooth for f in m.polygons)
 bm=bmesh.new();bm.from_mesh(m);assert all(e.is_manifold and e.is_contiguous for e in bm.edges);vol=bm.calc_volume(signed=True);assert vol>0;bm.free()
 for f in m.polygons:
  axis=max(range(3),key=lambda k:abs(f.normal[k]));assert abs(f.normal[axis])==1 and all(v.co[axis]==(hi[axis] if f.normal[axis]>0 else lo[axis]) for v in [m.vertices[i] for i in f.vertices])
 def volume(bounds):return (F(bounds[1][0])-F(bounds[0][0]))*(F(bounds[1][1])-F(bounds[0][1]))*(F(bounds[1][2])-F(bounds[0][2]))
 a,b=[c['bounds'] for c in sp['components']];inter=[[max(a[0][k],b[0][k])for k in range(3)],[min(a[1][k],b[1][k])for k in range(3)]]
 assert a[0][1:]==b[0][1:] and a[1][1:]==b[1][1:] and inter[1][0]>inter[0][0]
 assert volume(a)+volume(b)-volume(inter)==volume([lo,hi])
 rows.append({'object':u.name,'bounds':[lo,hi],'volume':vol,'exact_occupied_union':True,'all_attribute_complement_exact':True,'kept_domain_counts':{k:len(v)for k,v in maps[o.name].items()}})
checks['active_complements_geometry']=True
print('ACTIVE PASS',flush=True)
# Paired rollback, repeated assignments, actual evaluated equality.
for iteration in range(2):
 for sp in plan['pairs']:
  o=bpy.data.objects[sp['target']];o.modifiers[0].show_viewport=False;o.modifiers[0].show_render=False
  u=bpy.data.objects[sp['union_object']];u.hide_viewport=True;u.hide_render=True
 bpy.context.view_layer.update()
rollback=snap();expected=base['visible_evaluated']
for sp in plan['pairs']:
 record=rollback['visible_evaluated'][sp['target']]['mesh'];payload=record['debug_payload'];ids=sorted(v['id']for c in sp['components']for v in c['vertices'])
 assert payload['weights']==[(i,[(0,1.0)])for i in ids]
 payload['weights']=[];record['hash']=ss.digest(payload)
assert rollback['visible_evaluated']==expected,('Rollback evaluated mismatch',[n for n in expected if rollback['visible_evaluated'].get(n)!=expected[n]])
checks['rollback_repeated_evaluated_exact']=True
# Remove only explicitly owned additions in memory to independently compare every persisted field.
for sp in plan['pairs']:
 o=bpy.data.objects[sp['target']];o.modifiers.remove(o.modifiers[0]);o.vertex_groups.remove(o.vertex_groups[0]);u=bpy.data.objects[sp['union_object']];m=u.data;bpy.data.objects.remove(u,do_unlink=True);bpy.data.meshes.remove(m)
bpy.data.collections.remove(bpy.data.collections[plan['collection']]);bpy.context.view_layer.update()
normalized=snap();checks['normalized_full_source']={k:normalized[k]==base[k]for k in base}
diff={k:[n for n in base[k] if base[k][n]!=normalized[k].get(n)] for k in base if isinstance(base[k],dict) and base[k]!=normalized[k]}
report={'input_sha256':hashes,'checks':checks,'differences':diff,'parts':rows,'pass':all(checks['normalized_full_source'].values()),'source_unchanged':sha(source)==hashes['source'],'candidate_unchanged':sha(candidate)==hashes['candidate']}
report_path.write_text(json.dumps(report,indent=2));assert report['pass'],diff
print('FULL PASS',flush=True)
