"""Strict additive-only preservation. All original raw weights included, no model save."""
import argparse,bpy,copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import snapshot_support as ss
p=argparse.ArgumentParser()
for k in ['source','candidate','specification','report']:p.add_argument('--'+k,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();source_sha=sha(a.source);candidate_sha=sha(a.candidate);assert source_sha=='e71778349c4c65eafbda3eb0a3d0753cd11e1b368a3456c4de1db2f4c0f8647a';assert not Path(a.report).exists();cfg=json.loads(Path(a.specification).read_text());names=set(cfg['added_objects']);collection=cfg['added_collection'];assert names and all(n.startswith('V020 candidate |') for n in names)
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(Path(path).resolve()),use_scripts=False,load_ui=True);x=ss.snap();x['collections']=ss.collections_snapshot();x['scene_custom']=dict(bpy.context.scene.items());return x
base=snapshot(a.source);actual=snapshot(a.candidate);changes={};additions={};removals={};ui=[]
UI={'Traveler | full length ivory skirt','Traveler | purple-red shoulder cape','Traveler | white tunic'}
for cat in ['objects','meshes','materials','lights','cameras','worlds','visible_evaluated']:
 additions[cat]=sorted(set(actual[cat])-set(base[cat]));removals[cat]=sorted(set(base[cat])-set(actual[cat]));changes[cat]=[]
 for name in base[cat].keys()&actual[cat].keys():
  x,y=base[cat][name],actual[cat][name]
  if cat=='visible_evaluated' and name in UI:
   assert any(m['type']=='SUBSURF' for m in base['objects'][name]['modifiers']) and any(m['type']=='SUBSURF' for m in actual['objects'][name]['modifiers']);x,ux=ss.render_semantic_with_ui_report(x);y,uy=ss.render_semantic_with_ui_report(y);ui.append({'object':name,'before':ux,'after':uy})
  if x!=y:changes[cat].append(name)
for cat in ['scene','scene_custom','texts','libraries']:changes[cat]=[] if base[cat]==actual[cat] else ['changed']
for name,value in base['collections']['collections'].items():
 if actual['collections']['collections'].get(name)!=value:changes.setdefault('original_collections',[]).append(name)
newcols=set(actual['collections']['collections'])-set(base['collections']['collections']);assert newcols=={collection};col=actual['collections']['collections'][collection];assert col['objects']==sorted(names) and not col['children'];assert actual['collections']['root_children']==sorted(base['collections']['root_children']+[collection]) and actual['collections']['root_objects']==base['collections']['root_objects']
for name in names:
 o=bpy.data.objects[name];assert o.type=='MESH' and o.data.name==name and not o.parent and not o.constraints and not o.animation_data;assert [m.name for m in o.data.materials]==cfg['materials'][name];assert not o.hide_render and not o.hide_viewport and not o.hide_get()
allowed=all(set(additions[cat])==(names if cat in ['objects','meshes','visible_evaluated'] else set()) for cat in additions);passed=not any(changes.values()) and not any(removals.values()) and allowed;assert sha(a.source)==source_sha and sha(a.candidate)==candidate_sha
r={'pass':passed,'source_sha256':source_sha,'candidate_sha256':candidate_sha,'specification_sha256':sha(a.specification),'changes':changes,'additions':additions,'removals':removals,'additions_exact':allowed,'derived_ui_edge_reports':ui,'source_and_candidate_unchanged':True,'scope':'All original persistent and evaluated data, including original forest/deform weights, must remain exact. Only explicitly named additive meshes/objects and one collection allowed. Geometric placement/contact acceptance separate.'};Path(a.report).write_text(json.dumps(r,indent=2));assert passed,'Original scene preservation failure'
