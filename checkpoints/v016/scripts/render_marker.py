"""Reproduce or verify the matched actual offshore inspection camera; no model saves."""
import bpy,sys,argparse,json,hashlib,time
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
p=argparse.ArgumentParser();p.add_argument('--report',required=True);p.add_argument('--out');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=Path(bpy.data.filepath);sha=hashlib.sha256(source.read_bytes()).hexdigest();assert sha=='d44a4cdecd11dab152fd656c624755369e575a0f342e2eb0bc2460475c6f65eb'
m=json.loads((Path(__file__).resolve().parents[1]/'navigation/views.json').read_text());v=m['views']['offshore_marker'];s=bpy.context.scene;s.render.resolution_x=900;s.render.resolution_y=650;s.render.resolution_percentage=100
c=bpy.data.objects.new('Temporary matched offshore review',bpy.data.cameras.new('Temporary matched offshore review'));s.collection.objects.link(c);c.location=v['location'];c.rotation_euler=(Vector(v['target'])-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=v['lens'];c.data.clip_start=.05;c.data.clip_end=3000;s.camera=c;bpy.context.view_layer.update();points=[];rows=[];deps=bpy.context.evaluated_depsgraph_get()
NAMES=['Western citadel_West_Sea stack basalt', 'V004 | west old recess strips opened for selected upper and lower windows', 'V007 | western stonework with actual bridgehead passage', 'V012 | retained west rib facade with buried-route clearance', 'V012 | legacy ashlar with buried-route clearance']
names=NAMES+[o.name for o in bpy.data.objects if o.name.startswith('V016 |')]
for name in names:
 o=bpy.data.objects[name];assert not o.hide_render;eo=o.evaluated_get(deps);me=eo.to_mesh();ps=[eo.matrix_world@q.co for q in me.vertices];ps=ps if name.startswith('V016 |') else [q for q in ps if q.x>100 and q.y>170];points+=ps;rows.append({'object':name,'vertices':len(ps)});eo.to_mesh_clear()
pro=[world_to_camera_view(s,c,q) for q in points];inside=all(.075<=q.x<=.925 and .075<=q.y<=.925 and q.z>0 for q in pro);assert inside
r={'model_sha256':sha,'camera':v,'selected_objects':rows,'selected_vertices':len(points),'normalized_xy_bounds':[[min(q[k] for q in pro),max(q[k] for q in pro)] for k in [0,1]],'old_marker_rock_and_all_new_parts_inside_7_5_percent_margin':inside,'scope':'All evaluated vertices in audited offshore source components and4newparts; not whole-scene inventory. Matched camera, original source lighting/material/geometry untouched.'}
if a.out:
 s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=48;s.cycles.use_denoising=True;s.cycles.max_bounces=6;s.cycles.volume_bounces=1;s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(Path(a.out).resolve());s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.use_stamp=False;t=time.time();bpy.ops.render.render(write_still=True);r['render_seconds']=time.time()-t;r['image']=str(Path(a.out));r['lighting']='Actual scene; no diagnostic fill'
r['source_unchanged']=sha==hashlib.sha256(source.read_bytes()).hexdigest();assert r['source_unchanged'];Path(a.report).write_text(json.dumps(r,indent=2));print(json.dumps(r))
