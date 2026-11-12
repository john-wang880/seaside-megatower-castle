import bpy,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=sys.argv[-1],use_scripts=False)
from mathutils import Vector
for name in ['V030 | north three-bay rack','V030 | south three-bay rack','V029 | local stores shell']:
 o=bpy.data.objects[name];vs=[o.matrix_world@v.co for v in o.data.vertices];print(name,[(min(v[i] for v in vs),max(v[i] for v in vs)) for i in range(3)],'materials',[m.name for m in o.data.materials])
s=bpy.context.scene;cam=bpy.data.objects.new('survey',bpy.data.cameras.new('survey'));s.collection.objects.link(cam);cam.location=(15.4,36.2,30.6);cam.rotation_euler=(Vector((20,36.8,30))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=23;s.camera=cam;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.cycles.samples=16;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(P/'before.png');bpy.ops.render.render(write_still=True)
