"""Read-only additive source preservation, plus authoritative evaluated geometry export."""
import argparse,hashlib,json,sys,copy
from pathlib import Path
import bpy
from mathutils import Vector
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import snapshot_support as ss
if sys.flags.optimize:raise RuntimeError('Optimization refused')
p=argparse.ArgumentParser()
for k in ['source','candidate','candidate-sha','report','geometry']:p.add_argument('--'+k,required=True)
p.add_argument('--negative',choices=['source_vertex','source_material'])
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
hashes={k:sha(getattr(a,k))for k in ['source','candidate']};assert hashes['source']=='efcd894acdc045a30f845f05267662957b656bc7fe0ee4cf48c05fc798b610ee';assert hashes['candidate']==a.candidate_sha
for k in ['report','geometry']:assert not Path(getattr(a,k)).exists()
NAME='V027 | single oblique lower rock buttress';COLL='V027 | far-cliff buttress study'
def snap(path):
 bpy.ops.wm.open_mainfile(filepath=str(Path(path).resolve()),load_ui=True,use_scripts=False)
 if Path(path).resolve()==Path(a.candidate).resolve() and a.negative:
  if a.negative=='source_vertex':bpy.data.objects['V002 | western headland with solid rock shore'].data.vertices[0].co.x+=.125
  else:
   material=bpy.data.materials['V002 | varied salt-weathered coastal slate'];material.diffuse_color[0]=.123456
 d=ss.snap();d['collections']=ss.collections_snapshot();d['scene_custom']=dict(bpy.context.scene.items());return d
left=snap(a.source);right=snap(a.candidate);added={}
for cat in ['meshes','objects','visible_evaluated']:
 assert set(right[cat])-set(left[cat])=={NAME},(cat,'unexpected new IDs');added[cat]=right[cat].pop(NAME)
assert set(right['collections']['collections'])-set(left['collections']['collections'])=={COLL};c=right['collections']['collections'].pop(COLL);assert c['objects']==[NAME]and c['children']==[] and not c['hide_render'] and not c['hide_viewport'];assert COLL in right['collections']['root_children'];right['collections']['root_children'].remove(COLL)
ui=[]
for name in ['Traveler | full length ivory skirt','Traveler | purple-red shoulder cape','Traveler | white tunic']:
 assert any(x['type']=='SUBSURF'for x in left['objects'][name]['modifiers'])
 l,lu=ss.render_semantic_with_ui_report(left['visible_evaluated'][name]);r,ru=ss.render_semantic_with_ui_report(right['visible_evaluated'][name]);left['visible_evaluated'][name]=l;right['visible_evaluated'][name]=r;ui.append({'object':name,'source':lu,'candidate':ru})
checks={k:left[k]==right[k]for k in left};changed={k:[n for n in set(left[k])|set(right[k])if left[k].get(n)!=right[k].get(n)]for k in left if isinstance(left[k],dict)and not checks[k]}
# Export evaluated candidate and every render-visible broadphase neighbor; original model never saved.
deps=bpy.context.evaluated_depsgraph_get();o=bpy.data.objects[NAME];eo=o.evaluated_get(deps);bb=[eo.matrix_world@Vector(x)for x in eo.bound_box];lo=[min(v[k]for v in bb)for k in range(3)];hi=[max(v[k]for v in bb)for k in range(3)]
exports={};broad=[]
for o in bpy.data.objects:
 if o.type!='MESH' or o.hide_render:continue
 eo=o.evaluated_get(deps);bb=[eo.matrix_world@Vector(x)for x in eo.bound_box];ol=[min(v[k]for v in bb)for k in range(3)];oh=[max(v[k]for v in bb)for k in range(3)];separation=sum(max(ol[k]-hi[k],lo[k]-oh[k],0)**2 for k in range(3))**.5
 broad.append({'object':o.name,'evaluated_bounds':[ol,oh],'object_box_separation':separation,'hide_viewport':o.hide_viewport,'visible_get':o.visible_get()})
 if separation>0:continue
 me=eo.to_mesh(preserve_all_data_layers=True,depsgraph=deps);me.calc_loop_triangles();exports[o.name]={'vertices':[list(eo.matrix_world@v.co)for v in me.vertices],'faces':[list(f.vertices)for f in me.polygons],'triangles':[list(t.vertices)for t in me.loop_triangles],'triangle_polygons':[t.polygon_index for t in me.loop_triangles],'materials':[s.material.name if s.material else None for s in eo.material_slots],'face_materials':[f.material_index for f in me.polygons],'matrix':[list(row)for row in eo.matrix_world]};eo.to_mesh_clear()
Path(a.geometry).write_text(json.dumps({'input_sha256':hashes,'candidate_bounds':[lo,hi],'broadphase':broad,'objects':exports}));unchanged=all(sha(getattr(a,k))==v for k,v in hashes.items());result={'pass':all(checks.values())and unchanged,'input_sha256':hashes,'checks':checks,'changed_names':changed,'new_mesh_object':NAME,'new_collection':COLL,'added_records':added,'traveler_derived_UI':ui,'inputs_unchanged':unchanged};Path(a.report).write_text(json.dumps(result,indent=2));assert result['pass'],changed;print('PRESERVATION PASS')
