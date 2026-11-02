"""Independent additive saved-source preservation and actual geometry extraction; no save/render."""
import argparse,copy,json,hashlib,sys
from pathlib import Path
sys.dont_write_bytecode=True
if sys.flags.optimize:raise RuntimeError('Optimized Python refused')
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent));import snapshot_support as ss
SOURCE='4f838529d32cbf6a0314cc0a23b3dd1703b73d80c5db146fb4d323697b882df5';COL='V030 | reversible stores fittings';MAT='V030 | subdued stores timber';NAMES=[f'V030 | {s} three-bay rack'for s in ['south','north']]+[f'V030 | {s} supply bin {i}'for s in ['south','north']for i in [0,2]]
def need(v,msg):
 if not v:raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def visibility():
 def layer(l):return {'name':l.name,'collection':l.collection.name,'exclude':l.exclude,'hide_viewport':l.hide_viewport,'children':[layer(c)for c in l.children]}
 return {v.name:{'objects':{o.name:{'eye_hidden':o.hide_get(view_layer=v),'selected':o.select_get(view_layer=v)}for o in v.objects},'active':v.objects.active.name if v.objects.active else None,'layers':layer(v.layer_collection)}for v in bpy.context.scene.view_layers}
def snap():
 bpy.context.view_layer.update();d=ss.snap();d.update(collections=ss.collections_snapshot(),scene_custom=dict(bpy.context.scene.items()),visibility=visibility());return d
def normalized(s):
 s=copy.deepcopy(s);ui=[]
 for n in ['Traveler | full length ivory skirt','Traveler | purple-red shoulder cape','Traveler | white tunic']:
  need(any(m['type']=='SUBSURF'for m in s['objects'][n]['modifiers']),'Named derived UI exception');s['visible_evaluated'][n],r=ss.render_semantic_with_ui_report(s['visible_evaluated'][n]);ui.append({'object':n,'record':r})
 return s,ui
def main():
 ap=argparse.ArgumentParser()
 for x in ['source','candidate','candidate-sha','build-report','report','geometry']:ap.add_argument('--'+x,required=True)
 a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);need(sha(a.source)==SOURCE and sha(a.candidate)==a.candidate_sha,'Model identity');need(not Path(a.report).exists()and not Path(a.geometry).exists(),'New output required');receipt=json.loads(Path(a.build_report).read_text());need(receipt['candidate_sha256']==a.candidate_sha and receipt['source_sha256']==SOURCE,'Receipt identity');need({m['name']for m in receipt['new_meshes']}==set(NAMES),'Exact owned names');pins={p:sha(p)for p in [a.source,a.candidate,a.build_report]}
 bpy.ops.wm.open_mainfile(filepath=str(Path(a.source).resolve()),load_ui=True,use_scripts=False);old=snap();bpy.ops.wm.open_mainfile(filepath=str(Path(a.candidate).resolve()),load_ui=True,use_scripts=False);actual=snap();new=copy.deepcopy(actual)
 for cat,names in [('objects',NAMES),('meshes',NAMES),('visible_evaluated',NAMES),('materials',[MAT])]:
  need(set(new[cat])-set(old[cat])==set(names),'Additive category scope '+cat)
  for n in names:new[cat].pop(n)
 need(set(new['collections']['collections'])-set(old['collections']['collections'])=={COL},'Collection scope');c=new['collections']['collections'].pop(COL);need(c['objects']==sorted(NAMES)and not c['children']and not c['properties']and not any(c[k]for k in ['hide_viewport','hide_render','hide_select']),'Owned collection state');new['collections']['root_children'].remove(COL)
 for layer in new['visibility'].values():
  for n in NAMES:need(layer['objects'].pop(n)=={'eye_hidden':False,'selected':False},'New object visibility/selection')
  layer['layers']['children']=[c for c in layer['layers']['children']if c['collection']!=COL]
 l,lu=normalized(old);r,ru=normalized(new);checks={k:l[k]==r[k]for k in l};need(all(checks.values()),'Source drift '+str([k for k,v in checks.items()if not v]));exports=[]
 for name in NAMES:
  o=bpy.data.objects[name];m=o.data;spec=next(x for x in receipt['new_meshes']if x['name']==name);need(o.type=='MESH'and m.name==name and m.users==1 and not o.modifiers and not o.constraints and not o.vertex_groups and o.parent is None and not o.animation_data and not m.animation_data,'Owned dependencies');need(list(o.users_collection)==[bpy.data.collections[COL]],'Owned membership');need([list(r)for r in o.matrix_world]==[[float(i==j)for j in range(4)]for i in range(4)],'Identity transform');need([(s.link,s.material.name)for s in o.material_slots]==[('DATA',MAT)],'One local material slot');need([list(v.co)for v in m.vertices]==spec['vertices']and [list(f.vertices)for f in m.polygons]==spec['faces'],'Saved/report geometry identity');need(not m.uv_layers and not m.color_attributes and not m.shape_keys and not getattr(m,'has_custom_normals',False),'Unexpected mesh data');need(all(f.material_index==0 and not f.use_smooth for f in m.polygons),'Face shading');m.calc_loop_triangles();exports.append({'name':name,'vertices':[list(v.co)for v in m.vertices],'faces':[list(f.vertices)for f in m.polygons],'triangles':[list(t.vertices)for t in m.loop_triangles],'triangle_polygons':[t.polygon_index for t in m.loop_triangles],'components':spec['components']})
 mat=bpy.data.materials[MAT];need(mat.users==6 and mat.use_nodes,'Material ownership');graph=ss.tree_snapshot(mat.node_tree)
 # Full rollback deletes only new owned IDs in memory; source data and every old visibility remain exact.
 for name in NAMES:
  mesh=bpy.data.objects[name].data;bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True);bpy.data.meshes.remove(mesh)
 bpy.data.collections.remove(bpy.data.collections[COL]);bpy.data.materials.remove(mat);rollback,rollui=normalized(snap());need(rollback==l,'Full additive rollback drift');need(all(sha(p)==v for p,v in pins.items()),'Input changed')
 Path(a.geometry).write_text(json.dumps({'candidate_sha256':a.candidate_sha,'meshes':exports,'material_graph':graph},indent=2)+'\n');Path(a.report).write_text(json.dumps({'pass':True,'input_sha256':pins,'candidate_sha256':a.candidate_sha,'source_categories':checks,'derived_UI_only':{'source':lu,'candidate':ru,'rollback':rollui},'full_additive_rollback':True,'new_objects':NAMES,'new_material':MAT,'geometry_export_sha256':sha(a.geometry),'saved_or_rendered':False},indent=2)+'\n');print('FITTINGS SAVED PRESERVATION PASS')
if __name__=='__main__':main()
