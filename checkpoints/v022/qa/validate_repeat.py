"""Full persistent/evaluated semantic equality to accepted v022 single rib candidate, no saves."""
import argparse,bpy,copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import snapshot_support as ss
if sys.flags.optimize:raise RuntimeError('Assertions required; optimized Python unsupported')
p=argparse.ArgumentParser()
for k in ['accepted','rebuilt','report']:p.add_argument('--'+k,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();hashes={k:sha(getattr(a,k)) for k in ['accepted','rebuilt']};assert hashes['accepted']=='99156d901f9d498b86bae4834a642d1d9110dc6e4e3a4273bca64fda17a9dfd2';assert not Path(a.report).exists()
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(Path(path).resolve()),load_ui=True,use_scripts=False);x=ss.snap();x['collections']=ss.collections_snapshot();x['scene_custom']=dict(bpy.context.scene.items());return x
left=snapshot(a.accepted);right=snapshot(a.rebuilt);ui=[]
for name in ['Traveler | full length ivory skirt','Traveler | purple-red shoulder cape','Traveler | white tunic']:
 assert any(m['type']=='SUBSURF' for m in left['objects'][name]['modifiers']) and any(m['type']=='SUBSURF' for m in right['objects'][name]['modifiers']);l,lu=ss.render_semantic_with_ui_report(left['visible_evaluated'][name]);r,ru=ss.render_semantic_with_ui_report(right['visible_evaluated'][name]);ui.append({'object':name,'before':lu,'after':ru});left['visible_evaluated'][name]=l;right['visible_evaluated'][name]=r
checks={k:left[k]==right[k] for k in left};changed={k:sorted(name for name in set(left[k])|set(right[k]) if left[k].get(name)!=right[k].get(name)) for k in left if not checks[k] and isinstance(left[k],dict)};unchanged=all(sha(getattr(a,k))==v for k,v in hashes.items());report={'pass':all(checks.values()) and unchanged,'input_sha256':hashes,'category_checks':checks,'changed_names':changed,'derived_traveler_ui_edge_records':ui,'inputs_unchanged':unchanged,'scope':'Exact full persistent source/new mesh attributes, topology, normals, weights, materials/nodegraphs, transforms, world/lights/cameras/settings/collections and evaluated render geometry. Only established three SUBSURF garments derived edge-selection UI metadata recorded separately; no geometric tolerance.'};Path(a.report).write_text(json.dumps(report,indent=2));assert report['pass'],'Semantic repeat differs'
