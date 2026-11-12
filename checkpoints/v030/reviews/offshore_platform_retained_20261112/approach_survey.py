import bpy,pathlib,sys,json
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parent
import hashlib
assert hashlib.sha256(pathlib.Path(sys.argv[-1]).read_bytes()).hexdigest()=='a6c9715064ae0ea8ee58f369f46ceb3352bfc84fb53687b30bffd35bf38bd9ce'
bpy.ops.wm.open_mainfile(filepath=sys.argv[-1],use_scripts=False)
r=[]
for o in bpy.data.objects:
 if o.name.startswith('V016'):
  me=o.data;me.calc_loop_triangles();r.append({'name':o.name,'vertices':[list(o.matrix_world@v.co)for v in me.vertices],'triangles':[list(t.vertices)for t in me.loop_triangles]})
(P/'stairs.json').write_text(json.dumps(r));s=bpy.context.scene;cam=bpy.data.objects.new('S31 temporary survey',bpy.data.cameras.new('S31 temporary survey'));s.collection.objects.link(cam);cam.location=(116,187.5,6.8);cam.rotation_euler=(Vector((115.7,192.2,7.0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=26;s.camera=cam;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.cycles.samples=16;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(P/'approach_before.png');bpy.ops.render.render(write_still=True)
