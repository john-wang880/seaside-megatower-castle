"""Read-only v018 landscape evidence audit. Never saves a Blender scene."""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

SOURCE_SHA = "c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--source", required=True, type=Path, help="Canonical v018 .blend")
parser.add_argument("--output-dir", required=True, type=Path, help="New, nonexistent evidence directory")
parser.add_argument("--skip-render", action="store_true", help="Collect geometry/material evidence only")
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
src = args.source.resolve(strict=True)
if not src.is_file() or src.suffix.lower() != ".blend":
    parser.error("source must be a .blend file")
sha = lambda: hashlib.sha256(src.read_bytes()).hexdigest()
before = sha()
if before != SOURCE_SHA:
    parser.error("source SHA256 is not the accepted v018")
D = args.output_dir.absolute()
if D.exists() or D.is_symlink():
    parser.error("output directory already exists; refusing overwrite")
if not D.parent.is_dir():
    parser.error("output parent must already exist")
import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=str(src), use_scripts=False)
D.mkdir(exist_ok=False)  # Exclusive reservation; no existing output is overwritten.
s = bpy.context.scene
out={'source':str(src),'sha_before':before,'objects':[],'samples':[]}
for o in bpy.data.objects:
 if o.type=='MESH' and any(t in o.name.lower() for t in ['headland','coastal rock','grass','meadow']):
  vs=[o.matrix_world@Vector(v) for v in o.bound_box]
  out['objects'].append({'name':o.name,'visible_render':not o.hide_render,'mesh':o.data.name,'mesh_users':o.data.users,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'smooth_faces':sum(p.use_smooth for p in o.data.polygons),'min':[min(v[i] for v in vs) for i in range(3)],'max':[max(v[i] for v in vs) for i in range(3)],'materials':[m.name if m else None for m in o.data.materials],'modifiers':[(m.name,m.type) for m in o.modifiers],'vertex_groups':[g.name for g in o.vertex_groups]})
m=bpy.data.materials['Meadow and slate | slope-based procedural strata'];out['material']={'name':m.name,'users':m.users,'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links],'nodes':[]}
for n in m.node_tree.nodes:
 r={'name':n.name,'type':n.type};r['defaults']={i.name:(list(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value) for i in n.inputs if hasattr(i,'default_value') and not i.is_linked}
 if hasattr(n,'color_ramp'):r['ramp']=[(e.position,list(e.color)) for e in n.color_ramp.elements]
 out['material']['nodes'].append(r)
# Exact hero rays for selected pixels, exclude hidden objects explicitly by per-object cast.
cam=s.camera; frame=cam.data.view_frame(scene=s); xmin=min(v.x/-v.z for v in frame);xmax=max(v.x/-v.z for v in frame);ymin=min(v.y/-v.z for v in frame);ymax=max(v.y/-v.z for v in frame)
obs=[o for o in bpy.context.view_layer.objects if o.type=='MESH' and not o.hide_render and not o.hide_get()];deps=bpy.context.evaluated_depsgraph_get()
for px,py in [(680,610),(700,630),(740,620),(770,600),(800,625),(850,610),(900,630),(930,655)]:
 dr=(cam.matrix_world.to_3x3()@Vector((xmin+(xmax-xmin)*px/1200,ymax-(ymax-ymin)*py/866,-1))).normalized();origin=cam.matrix_world.translation;hits=[]
 for o in obs:
  e=o.evaluated_get(deps);inv=e.matrix_world.inverted();h,l,n,f=e.ray_cast(inv@origin,(inv.to_3x3()@dr).normalized())
  if h:
   w=e.matrix_world@l;hits.append(((w-origin).length,o.name,list(w),f,list(e.matrix_world.to_3x3()@n)))
 hits.sort();out['samples'].append({'pixel':[px,py],'nearest':hits[:3]})
with D.joinpath('audit.json').open('x') as f:
 json.dump(out,f,indent=2)

if args.skip_render:
    after = sha()
    if after != before:
        raise RuntimeError("source changed during read-only audit")
    with (D / "inspection_receipt.json").open("x") as f:
        json.dump({"source_sha_before": before, "source_sha_after": after,
                   "saved_model": False, "rendered": False,
                   "blender_version": bpy.app.version_string}, f, indent=2)
    print("AUDIT_COMPLETE_NO_RENDER")
else:
    # One actual-light, same-perspective bounded enlargement; no new scene geometry.
    r=s.render;receipt={'source_sha':before,'camera':cam.name,'matrix_world':[list(x) for x in cam.matrix_world],'lens':cam.data.lens,'original_resolution':[r.resolution_x,r.resolution_y,r.resolution_percentage],'samples':s.cycles.samples,'max_bounces':s.cycles.max_bounces,'world':s.world.name,'exposure':s.view_settings.exposure,'view_transform':s.view_settings.view_transform,'crop_hero_pixels':[620,575,980,695],'lighting_changed':False,'saved_model':False}
    r.resolution_x=3600;r.resolution_y=2598;r.resolution_percentage=100;r.use_border=True;r.use_crop_to_border=True;r.border_min_x=620/1200;r.border_max_x=980/1200;r.border_min_y=1-695/866;r.border_max_y=1-575/866;r.threads_mode='FIXED';r.threads=8;r.filepath=str(D/'hero_slope_detail.png');t=time.time();bpy.ops.render.render(write_still=True);receipt['elapsed_seconds']=time.time()-t;receipt['source_sha_after']=sha();assert sha()==before;receipt['image_sha256']=hashlib.sha256((D/'hero_slope_detail.png').read_bytes()).hexdigest()
    with D.joinpath('render_receipt.json').open('x') as f:
     json.dump(receipt,f,indent=2)
    print('AUDIT_COMPLETE')
