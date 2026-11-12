import bpy,sys,pathlib,hashlib
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parent;src=pathlib.Path(sys.argv[-1]);assert hashlib.sha256(src.read_bytes()).hexdigest()=='a6c9715064ae0ea8ee58f369f46ceb3352bfc84fb53687b30bffd35bf38bd9ce'
bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False)
s=bpy.context.scene;cam=bpy.data.objects.new('S31 facade survey',bpy.data.cameras.new('S31 facade survey'));s.collection.objects.link(cam);s.camera=cam;cam.location=(95,-100,100);cam.rotation_euler=(Vector((35,31,86))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=55;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.cycles.samples=16;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(P/'before.png');bpy.ops.render.render(write_still=True)
