"""Read-only independent fixed fixture copies, full prior-state and native geometry export."""
import argparse,json,hashlib,sys,copy
from pathlib import Path
sys.dont_write_bytecode=True
if sys.flags.optimize:raise RuntimeError('Optimization refused')
import bpy
from mathutils import Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import snapshot_support as ss
S='103be14556a9bbc96b26033b2b6016f0038d980ca7b3e69da792671e3f85ac60';C='bd3a7561ad19d5eabf41b89cbd8f9637480090d1824d58a67cffeff53952e286';COL='V028 | receiving chamber warm lanterns'
p=argparse.ArgumentParser()
for k in ['source','candidate','report','geometry']:p.add_argument('--'+k,required=True)
p.add_argument('--candidate-sha',default=C);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);C=a.candidate_sha;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(a.source)==S and sha(a.candidate)==C;assert not Path(a.report).exists() and not Path(a.geometry).exists()
def snap():
 d=ss.snap();d['collections']=ss.collections_snapshot();d['scene_custom']=dict(bpy.context.scene.items());return d
bpy.ops.wm.open_mainfile(filepath=str(Path(a.source).resolve()),load_ui=True,use_scripts=False);left=snap();bpy.ops.wm.open_mainfile(filepath=str(Path(a.candidate).resolve()),load_ui=True,use_scripts=False);right=snap();suffixes=['mounting plate','wall arm','lower cup','hood rim','rain hood','cage upright 0','cage upright 1','cage upright 2','cage upright 3','luminous flame','practical warm source'];names=['V028 | room '+str(i)+' '+s for i in (1,2) for s in suffixes];mesh_names=[n for n in names if not n.endswith('practical warm source')];light_names=[n for n in names if n not in mesh_names]
for cat,wanted in [('objects',names),('meshes',mesh_names),('visible_evaluated',mesh_names),('lights',light_names)]:
 assert set(right[cat])-set(left[cat])==set(wanted),cat
 for n in wanted:right[cat].pop(n)
assert set(right['collections']['collections'])-set(left['collections']['collections'])=={COL};co=right['collections']['collections'].pop(COL);assert co['objects']==sorted(names) and not co['children'] and not co['properties'] and not any(co[k] for k in ('hide_render','hide_viewport','hide_select'));right['collections']['root_children'].remove(COL)
ui=[]
for n in ['Traveler | full length ivory skirt','Traveler | purple-red shoulder cape','Traveler | white tunic']:
 l,lu=ss.render_semantic_with_ui_report(left['visible_evaluated'][n]);r,ru=ss.render_semantic_with_ui_report(right['visible_evaluated'][n]);left['visible_evaluated'][n]=l;right['visible_evaluated'][n]=r;ui.append({'object':n,'source':lu,'candidate':ru})
checks={k:left[k]==right[k] for k in left};assert all(checks.values()),[k for k,v in checks.items() if not v]
exports=[];copies=[];count=0
for index,y in [(1,34.),(2,39.)]:
 for suffix in suffixes:
  original=bpy.data.objects['V013 | turn '+suffix];o=bpy.data.objects['V028 | room '+str(index)+' '+suffix];delta=(9.6,y-38.65,0.);expected=Matrix.Translation(delta)@original.matrix_world
  assert o.matrix_world==expected and o.data.users==1 and o.data is not original.data and not o.parent and not o.constraints and not o.modifiers and not o.vertex_groups and not o.hide_render and not o.hide_viewport and not o.hide_get()
  p0=ss.primitive(original);p1=ss.primitive(o)
  for k in ('name','name_full','data','location','matrix_world','matrix_local','matrix_basis'):
   p0.pop(k,None);p1.pop(k,None)
  assert p0==p1,('object properties',o.name,[k for k in p0 if p0[k]!=p1.get(k)])
  if o.type=='MESH':
   assert ss.mesh_snapshot(o.data)==ss.mesh_snapshot(original.data);assert [(s.link,s.material.name) for s in o.material_slots]==[(s.link,s.material.name) for s in original.material_slots]
   me=o.data;me.calc_loop_triangles();count+=len(me.loop_triangles);exports.append({'object':o.name,'seed':0,'vertices':[list(o.matrix_world@v.co) for v in me.vertices],'local_faces':[list(f.vertices) for f in me.polygons],'local_triangles':[list(t.vertices) for t in me.loop_triangles]})
  else:
   p0=ss.primitive(original.data);p1=ss.primitive(o.data)
   for k in ('name','name_full'):p0.pop(k,None);p1.pop(k,None)
   assert p0==p1 and ss.tree_snapshot(original.data.node_tree)==ss.tree_snapshot(o.data.node_tree)
  copies.append({'name':o.name,'source':original.name,'exact_native_translation':list(delta),'type':o.type,'matrix':[list(r) for r in o.matrix_world]})
assert count==1160 and sha(a.source)==S and sha(a.candidate)==C
Path(a.geometry).write_text(json.dumps({'candidate_sha256':C,'components':exports}));Path(a.report).write_text(json.dumps({'pass':True,'source_unlit_sha256':S,'candidate_sha256':C,'all_preexisting_categories':checks,'copies':copies,'new_fixture_triangles':count,'derived_UI_only':ui,'limits':'Exact two native template copies and unchanged preexisting scene. Actual fixture route/contact checks use exported saved geometry separately.'},indent=2));print('LIT PRESERVATION AND EXACT TEMPLATE COPIES PASS')
