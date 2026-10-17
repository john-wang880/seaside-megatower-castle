"""Unchanged-light, repeatable close and skyline review cameras. Does not save scene."""
import argparse,bpy,hashlib,json,os,sys,time
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--views',default='main,west,hero');p.add_argument('--output-dir',required=True);p.add_argument('--prefix',required=True);p.add_argument('--samples',type=int,default=20);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source_sha=hashlib.sha256(open(bpy.data.filepath,'rb').read()).hexdigest()
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=a.samples;s.cycles.use_denoising=True;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.06
s.cycles.max_bounces=6;s.cycles.diffuse_bounces=3;s.cycles.glossy_bounces=3;s.cycles.transmission_bounces=4;s.cycles.volume_bounces=1
s.render.resolution_x=1000;s.render.resolution_y=750;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=3;s.render.use_persistent_data=True
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.use_stamp=False
for k in ['use_stamp_filename','use_stamp_date','use_stamp_time']:
 if hasattr(s.render,k):setattr(s.render,k,False)
config={'main':((67,-57,148),(35.3,29,141),66),'west':((-94,0,124),(-133,86,121),67),'hero':((115,-470,24),(-35,35,85),43),'main_tower':((145,-165,132),(35,43,129),50),'west_tower':((-52,-68,134),(-133,100,130),50)}
os.makedirs(a.output_dir,exist_ok=True)
for view in a.views.split(','):
 loc,target,lens=config[view];cd=bpy.data.cameras.new('V004 review '+view);c=bpy.data.objects.new('V004 review '+view,cd);s.collection.objects.link(c);c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;cd.clip_end=3000;s.camera=c
 if view=='hero':
  s.render.resolution_x=900;s.render.resolution_y=600;s.cycles.samples=16;s.cycles.adaptive_threshold=.08
 else:
  s.render.resolution_x=1000;s.render.resolution_y=1000 if view.endswith('_tower') else 750;s.cycles.samples=a.samples;s.cycles.adaptive_threshold=.06
 s.render.filepath=os.path.join(os.path.abspath(a.output_dir),a.prefix+'_'+view+'.png');t=time.time();bpy.ops.render.render(write_still=True)
 r={'input_filename':os.path.basename(bpy.data.filepath),'input_sha256':source_sha,'view':view,'location':loc,'target':target,'lens':lens,'resolution':[s.render.resolution_x,s.render.resolution_y],'samples':s.cycles.samples,'engine':'Cycles CPU','threads':3,'elapsed_seconds':time.time()-t,'scene_saved':False,'lighting_world_and_exposure_unchanged':True}
 with open(os.path.splitext(s.render.filepath)[0]+'.json','w') as f:json.dump(r,f,indent=2)
 print(json.dumps(r),flush=True)
