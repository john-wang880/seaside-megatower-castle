import bpy,argparse,sys,json,time,hashlib
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.use_denoising=True;s.cycles.max_bounces=6;s.cycles.volume_bounces=0
s.render.resolution_x=900;s.render.resolution_y=650;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4
hidden=[]
for o in bpy.data.objects:
 if o.type=='LIGHT' or o.name.startswith(('Volume cloud','Air perspective')):
  if not o.hide_render:hidden.append(o.name)
  o.hide_render=True
w=bpy.data.worlds.new('Diagnostic neutral world');w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.72,.76,.8,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.7;s.world=w
loc=(4.45,38.1,30.6);target=(4.45,49,31);lens=28
c=bpy.data.objects.new('Diagnostic review camera',bpy.data.cameras.new('Diagnostic review camera'));s.collection.objects.link(c);c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_end=3000;s.camera=c
for name,position,aim,power,size in [('entrance',(-6,38,31),(0,38,29),450,3),('hall',(3,38,31.5),(4.45,43,29),350,3),('corridor',(4.45,47,32),(4.45,51,30),350,3),('terrace',(4.45,59,36),(4.45,52,31),900,5)]:
 d=bpy.data.lights.new('Diagnostic '+name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=(1,1,1);o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=position;o.rotation_euler=(Vector(aim)-o.location).to_track_quat('-Z','Y').to_euler()
s.view_settings.view_transform='AgX';s.view_settings.exposure=0
s.render.filepath=str(Path(a.out).resolve());s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.use_stamp=False
source_sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();start=time.time();bpy.ops.render.render(write_still=True)
assert source_sha==hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
Path(a.out).with_suffix('.json').write_text(json.dumps({'label':'LOCAL v012 prototype, not accepted. Diagnostic neutral lighting; final scene lighting unchanged. Actual model geometry and materials, identical before/after camera and inspection lights.','source':Path(bpy.data.filepath).name,'sha256':source_sha,'runtime':bpy.app.version_string,'camera':[loc,target,lens],'samples':16,'seconds':time.time()-start,'saved':False,'hidden_original_lights_and_atmosphere':hidden},indent=2))
