import bpy,argparse,sys,json,time,hashlib,resource
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--view',default='bridge');p.add_argument('--samples',type=int,default=16);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=a.samples;s.cycles.use_denoising=True;s.cycles.max_bounces=6;s.cycles.volume_bounces=1
s.render.resolution_x=1200;s.render.resolution_y=866;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4
views={'terrace':((4.45,61,34.5),(4.45,49,30.5),32),'arrival':((4.45,56.8,34.1),(4.45,65,34.1),28),'bend':((4.45,38.1,30.6),(4.45,49,31),28),'west_approach':((-102,21,35),(-79,38,26),42),'east_portal':((-25,37.2,31.5),(-7.5,38,29.8),38),'east':((-29,17,38),(-8,38,28.5),42),'portal':((-43,32,31.7),(-65,38,29),45),'bridge':((-52,-63,56),(-42,34,30),48),'bridge_top':((-50,-25,100),(-40,40,27),48),'hero':((115,-470,24),(-35,35,85),43)}
loc,target,lens=views[a.view];c=bpy.data.objects.new('Review camera',bpy.data.cameras.new('Review camera'));s.collection.objects.link(c);c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_end=3000;s.camera=c
s.render.filepath=str(Path(a.out).resolve());s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.use_stamp=False
source_sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();start=time.time();bpy.ops.render.render(write_still=True)
assert source_sha==hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(), 'Source changed during rendering'
Path(a.out).with_suffix('.json').write_text(json.dumps({'source':Path(bpy.data.filepath).name,'sha256':source_sha,'runtime':bpy.app.version_string,'camera':[loc,target,lens],'samples':a.samples,'seconds':time.time()-start,'saved':False,'peak_rss_linux_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'lighting':'actual scene practical lanterns; original world and lights retained; no diagnostic lights'},indent=2))
