import bpy,argparse,sys,json,time,hashlib,resource
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--view',required=True);p.add_argument('--out',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
manifest_bytes=Path(a.manifest).read_bytes();manifest_start_sha=hashlib.sha256(manifest_bytes).hexdigest();m=json.loads(manifest_bytes);v=m['views'][a.view];source=Path(bpy.data.filepath);sha=hashlib.sha256(source.read_bytes()).hexdigest();assert sha==m['source_sha256']
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=24;s.cycles.use_denoising=True;s.cycles.max_bounces=6;s.cycles.volume_bounces=1;s.render.resolution_x=720;s.render.resolution_y=520;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4
if 'existing_camera' in v:c=bpy.data.objects[v['existing_camera']];assert c.type=='CAMERA'
else:
 c=bpy.data.objects.new('Temporary still '+a.view,bpy.data.cameras.new('Temporary still '+a.view));s.collection.objects.link(c);c.location=v['location'];c.rotation_euler=(Vector(v['target'])-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=v['lens'];c.data.clip_start=v.get('clip_start',.05);c.data.clip_end=v.get('clip_end',3000)
s.camera=c;s.render.filepath=str(Path(a.out).resolve());s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.use_stamp=False
start=time.time();bpy.ops.render.render(write_still=True);assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
r={'view':a.view,'source':source.name,'source_sha256':sha,'view_manifest_sha256':manifest_start_sha,'manifest_hash_timing':'render-start bytes snapshot','preset':v,'actual_camera':{'location':list(c.location),'rotation_euler':list(c.rotation_euler),'lens':c.data.lens,'clip_start':c.data.clip_start,'clip_end':c.data.clip_end},'resolution':[720,520],'samples':24,'seconds':time.time()-start,'peak_rss_linux_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'runtime':bpy.app.version_string,'lighting':'Actual existing world/lights/exposure unchanged. No diagnostic fill or hidden geometry.','scope':'Independent camera still, not simulated walking or a dynamic navigation proof.','source_saved':False}
Path(a.out).with_suffix('.json').write_text(json.dumps(r,indent=2))
