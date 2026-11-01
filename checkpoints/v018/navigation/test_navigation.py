"""Independent Blender tests; source read-only, outputs confined to explicit test directory."""
import argparse,copy,hashlib,json,sys
from pathlib import Path
import bpy
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import navigation as nav
from deep_snapshot import snap,primitive
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--outdir',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=Path(a.source).resolve();out=Path(a.outdir).resolve();out.mkdir(parents=True,exist_ok=True)
source_hash=hashlib.sha256(source.read_bytes()).hexdigest();m=nav.load_manifest();expected_names={v['camera_name'] for v in m['views'].values() if 'camera_name' in v};expected_data={n+' data' for n in expected_names};checks={};details={}
def opened():bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=True,use_scripts=False)
def cols():return {c.name:{'props':primitive(c),'objects':sorted(o.name for o in c.objects),'children':sorted(x.name for x in c.children)} for c in bpy.data.collections}
def selected():return (bpy.context.view_layer.objects.active.name if bpy.context.view_layer.objects.active else None,sorted(o.name for o in bpy.context.selected_objects))
def same_original(base,new):
 diff={}
 for cat in ('meshes','objects','materials','lights','cameras','worlds','visible_evaluated'):
  diff[cat+'_changed']=[k for k in base[cat] if k not in new[cat] or base[cat][k]!=new[cat][k]]
  added=set(new[cat])-set(base[cat]);allowed=expected_names if cat=='objects' else expected_data if cat=='cameras' else set()
  diff[cat+'_unexpected_additions']=sorted(added-allowed)
  if cat in ('objects','cameras'):diff[cat+'_missing_additions']=sorted(allowed-added)
 bs=copy.deepcopy(base['scene']);ns=copy.deepcopy(new['scene']);bs.pop('camera');ns.pop('camera')
 diff['scene_except_active_camera']=[] if bs==ns else ['changed']
 for cat in ('libraries','texts'):diff[cat]=[] if base[cat]==new[cat] else ['changed']
 assert not any(diff.values()),diff
 return diff
opened();base=snap();basecols=cols();selection=selected();before_objects=set(bpy.data.objects.keys())
try:nav.install(m,'not_a_view');raise AssertionError('Unknown view accepted')
except ValueError:checks['unknown_view_rejected_before_mutation']=set(bpy.data.objects.keys())==before_objects
try:nav.export_viewer(source,'bend');raise AssertionError('Source overwrite accepted')
except ValueError:checks['source_overwrite_rejected']=True
sentinel=out/'must_not_overwrite.blend'
if not sentinel.exists():sentinel.write_bytes(b'NAVIGATION TEST SENTINEL')
assert sentinel.read_bytes()==b'NAVIGATION TEST SENTINEL'
try:nav.export_viewer(sentinel,'bend');raise AssertionError('Existing output accepted')
except FileExistsError:checks['existing_output_rejected']=sentinel.read_bytes()==b'NAVIGATION TEST SENTINEL'
assert set(bpy.data.objects.keys())==before_objects
nav.install(m,'bend');after=snap();details['original_data_differences']=same_original(base,after);checks['deep_original_data_unchanged']=True
checks['chosen_camera_selected_in_viewer']=selected()==(m['views']['bend']['camera_name'],[m['views']['bend']['camera_name']]);aftercols=cols();checks['original_collections_unchanged']=all(basecols[n]==aftercols[n] for n in basecols)
assert set(aftercols)-set(basecols)=={m['collection']}
nav.install(m,'bend');again=snap();checks['duplicate_install_idempotent']=again==after and cols()==aftercols
assert checks['duplicate_install_idempotent']
# V018 integration: ninth named view/eight new cameras, exact west-cap pose.
checks['nine_views_eight_review_cameras']=len(m['views'])==9 and len(expected_names)==8
checks['all_eight_owned_cameras_present']=all(n in bpy.data.objects and bpy.data.objects[n].type=='CAMERA' for n in expected_names)
nav.install(m,'west_crown');west_snapshot=snap();same_original(base,west_snapshot)
w=m['views']['west_crown'];cam=bpy.context.scene.camera
checks['west_crown_selected_exact_recipe']=(cam.name==w['camera_name'] and (cam.location-__import__('mathutils').Vector(w['location'])).length<1e-5 and abs(cam.data.lens-w['lens'])<1e-6)
checks['west_crown_switch_preserves_originals']=True
# Changing selection should alter only allowed active-camera/VIEW_3D state.
nav.install(m,'terminal');switched=snap();same_original(base,switched);checks['view_switch_preserves_originals']=True
v=m['views']['terminal'];spaces=[]
for sc in bpy.data.screens:
 for area in sc.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;r=sp.region_3d;spaces.append(r.view_perspective=='CAMERA' and sp.camera.name==v['camera_name'] and abs(sp.clip_start-.05)<1e-6 and sp.clip_end==3000 and (r.view_location-__import__('mathutils').Vector(v['target'])).length<1e-5)
checks['saved_viewports_have_camera_and_sane_pivot']=bool(spaces) and all(spaces)
viewer=out/'navigation_viewer_terminal.blend'
if viewer.exists():raise FileExistsError('Use a fresh test output directory')
report=nav.export_viewer(viewer,'terminal');checks['viewer_created']=viewer.is_file();checks['source_filepath_retained_after_copy_save']=Path(bpy.data.filepath).resolve()==source
bpy.ops.wm.open_mainfile(filepath=str(viewer),load_ui=True,use_scripts=False);restored=snap();same_original(base,restored);checks['viewer_reopen_originals_unchanged']=True;details['evaluated_ui_edge_selection_differences']={name:{'before':base['evaluated_edge_selection_ui'][name],'after':restored['evaluated_edge_selection_ui'][name]} for name in base['evaluated_edge_selection_ui'] if base['evaluated_edge_selection_ui'][name]!=restored['evaluated_edge_selection_ui'][name]};checks['viewer_reopen_selected_camera']=bpy.context.scene.camera.name==v['camera_name'];before=restored;nav.install(m,'terminal');checks['reopened_viewer_install_idempotent']=snap()==before
# Wrong-owner object name collision, even if object is harmless. No adoption.
opened();name=next(iter(sorted(expected_names)));intruder=bpy.data.objects.new(name,None);bpy.context.scene.collection.objects.link(intruder);objects=set(bpy.data.objects.keys());cameras=set(bpy.data.cameras.keys());collections=set(bpy.data.collections.keys())
try:nav.install(m,'bend');raise AssertionError('Object collision accepted')
except ValueError:checks['object_collision_rejected_without_partial_install']=(set(bpy.data.objects.keys())==objects and set(bpy.data.cameras.keys())==cameras and set(bpy.data.collections.keys())==collections)
opened();bad=bpy.data.collections.new(m['collection']);bpy.context.scene.collection.children.link(bad);objects=set(bpy.data.objects.keys())
try:nav.install(m,'bend');raise AssertionError('Collection collision accepted')
except ValueError:checks['collection_collision_rejected_without_partial_install']=set(bpy.data.objects.keys())==objects
opened();nav.install(m,'bend');cam=bpy.data.objects[m['views']['bend']['camera_name']];cam.location.x+=1;names=set(bpy.data.objects.keys())
try:nav.install(m,'bend');raise AssertionError('Modified owned camera accepted')
except ValueError:checks['changed_owned_camera_rejected_without_reset']=abs(cam.location.x-(m['views']['bend']['location'][0]+1))<1e-5 and set(bpy.data.objects.keys())==names
# Guard effective camera projection and delta transforms before selection mutation.
for label,mutate in [('projection_type',lambda cam:setattr(cam.data,'type','ORTHO')),('sensor_shift',lambda cam:setattr(cam.data,'shift_x',.1)),('delta_transform',lambda cam:setattr(cam,'delta_location',(1,0,0)))]:
 opened();nav.install(m,'bend');cam=bpy.data.objects[m['views']['bend']['camera_name']];mutate(cam);prior=selected();active=bpy.context.scene.camera
 try:nav.install(m,'terminal');raise AssertionError('Changed projection/pose accepted')
 except ValueError:checks[label+'_collision_rejected_before_selection']=selected()==prior and bpy.context.scene.camera==active
opened();nav.install(m,'bend');layer=next(l for l in bpy.context.view_layer.layer_collection.children if l.collection.name==m['collection']);layer.exclude=True;prior=selected();active=bpy.context.scene.camera
try:nav.install(m,'terminal');raise AssertionError('Excluded camera collection accepted')
except ValueError:checks['excluded_collection_rejected_before_selection']=selected()==prior and bpy.context.scene.camera==active
checks['evaluated_ui_exclusion_is_exact_boolean_edge_schema']=all(v['schema']==['.select_edge','BOOLEAN','EDGE'] and v['attribute']==v['edge_flags'] for data in (base,restored) for v in data['evaluated_edge_selection_ui'].values())
checks['source_bytes_unchanged']=hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
result={'source_sha256':source_hash,'checks':checks,'viewer':report,'details':details,'all_pass':all(checks.values()),'scope':'Only new owned cameras/collection plus active camera and saved VIEW_3D navigation state. Viewer selection explicitly changes to chosen camera; original object geometry/data preserved. Viewer file intentionally differs; canonical file bytes unchanged.'}
(out/'results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));assert result['all_pass']
