"""Remove only archived, unreferenced hidden intermediate forest copies."""
import bpy,hashlib,json,argparse,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=Path(bpy.data.filepath);out=Path(a.output).resolve();assert out!=source.resolve()
names=['V007 | woodland boughs minus gate-intersecting tree','V007 | woodland trunks minus gate-intersecting tree','V009 | woodland boughs with western approach clearance','V009 | woodland trunks with western approach clearance']
keep=['Dense western woodland | irregular three-dimensional needle boughs','Woodland tree trunks','V010 | woodland boughs with gate exit clearance','V010 | woodland trunks with gate exit clearance']
assert all(n in bpy.data.objects for n in keep)
user_map=bpy.data.user_map();removed=[]
for name in names:
 o=bpy.data.objects[name];m=o.data
 assert o.type=='MESH' and o.hide_render and o.hide_get() and m.users==1 and not m.use_fake_user
 assert not o.modifiers and not o.constraints and not o.parent and not o.children and not o.animation_data and not m.animation_data and not m.shape_keys
 assert all(isinstance(u,(bpy.types.Scene,bpy.types.Collection)) for u in user_map.get(o,set()))
 assert user_map.get(m,set())=={o}
 assert not any(name in t.as_string() for t in bpy.data.texts)
 removed.append({'object':name,'mesh':m.name,'vertices':len(m.vertices),'polygons':len(m.polygons),'rollback_commit':'38f9d594ea390e03b35a87921e6d0e7f19d232cc','mesh_users_before':m.users})
# Validate all candidates before mutating any data. Preserve every other source.
for name in names:
 o=bpy.data.objects[name];m=o.data;bpy.data.objects.remove(o,do_unlink=True);assert m.users==0;bpy.data.meshes.remove(m)
assert all(n in bpy.data.objects for n in keep)
bpy.context.preferences.filepaths.use_scripts_auto_execute=False;bpy.context.scene.render.filepath='//preview.png';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
r={'version':'v011','scope':'Only redundant hidden intermediate forest copies removed; full originals and latest visible geometry preserved. No architectural or lighting change.','runtime':bpy.app.version_string,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_bytes':source.stat().st_size,'output_bytes':out.stat().st_size,'removed':removed,'preserved_forest_objects':keep};Path(a.report).write_text(json.dumps(r,indent=2));print('V011_CONSOLIDATED',json.dumps(r))
