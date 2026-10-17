"""Economical, repeatable composition preview. Never saves the loaded scene."""
import argparse
import bpy
import json
import os
import sys
import time
from mathutils import Vector

p=argparse.ArgumentParser()
p.add_argument('--camera',choices=['hero','aerial','bridge','crown'],required=True)
p.add_argument('--output',required=True)
p.add_argument('--samples',type=int,default=16)
p.add_argument('--also-crown',action='store_true',help='Reuse scene data for one additional close architectural QA view.')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
s=bpy.context.scene
if a.camera=='hero':
    c=bpy.data.objects.get('V002 | full coastal skyline camera')
    if not c:
        cd=bpy.data.cameras.new('Composition-only full skyline camera')
        c=bpy.data.objects.new('Composition-only full skyline camera',cd)
        s.collection.objects.link(c)
        c.location=(115,-470,24)
        c.rotation_euler=(Vector((-35,35,85))-c.location).to_track_quat('-Z','Y').to_euler()
        cd.lens=43; cd.clip_end=3000
    s.camera=c
elif a.camera=='aerial':
    s.camera=bpy.data.objects['04 | Full three dimensional scene']
elif a.camera=='bridge':
    s.camera=bpy.data.objects['03 | Stone bridge and western curtain wall']
else:
    cd=bpy.data.cameras.new('Temporary crown QA camera')
    c=bpy.data.objects.new('Temporary crown QA camera',cd); s.collection.objects.link(c)
    c.location=(98,-61,207)
    c.rotation_euler=(Vector((35,43,184))-c.location).to_track_quat('-Z','Y').to_euler()
    cd.lens=45; cd.clip_end=3000; s.camera=c
s.render.engine='CYCLES'; s.cycles.device='CPU'
s.cycles.samples=a.samples; s.cycles.use_denoising=True
s.cycles.use_adaptive_sampling=True; s.cycles.adaptive_threshold=.08
s.cycles.max_bounces=6; s.cycles.diffuse_bounces=3; s.cycles.glossy_bounces=3
s.cycles.transmission_bounces=4; s.cycles.volume_bounces=1
s.render.resolution_x=900; s.render.resolution_y=600; s.render.resolution_percentage=100
s.render.threads_mode='FIXED'; s.render.threads=3
s.render.use_persistent_data=True
s.render.image_settings.file_format='PNG'; s.render.image_settings.color_mode='RGB'
# Blender otherwise embeds the absolute project filename even when no stamp is burned in.
s.render.use_stamp=False
for key in ['use_stamp_filename','use_stamp_date','use_stamp_time']:
    if hasattr(s.render,key): setattr(s.render,key,False)
s.render.filepath=os.path.abspath(a.output)
os.makedirs(os.path.dirname(s.render.filepath),exist_ok=True)
t=time.time(); bpy.ops.render.render(write_still=True)
report={'input_filename':os.path.basename(bpy.data.filepath),'camera':s.camera.name,
        'position':list(s.camera.location),'rotation':list(s.camera.rotation_euler),'lens':s.camera.data.lens,
        'resolution':[900,600],'samples':a.samples,'engine':'Cycles CPU','threads':3,
        'render_seconds':time.time()-t,'autoexec_enabled':bpy.context.preferences.filepaths.use_scripts_auto_execute,
        'output_filename':os.path.basename(s.render.filepath),'scene_saved':False}
with open(os.path.splitext(s.render.filepath)[0]+'.json','w') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
if a.also_crown and a.camera!='crown':
    cd=bpy.data.cameras.new('Temporary crown QA camera')
    c=bpy.data.objects.new('Temporary crown QA camera',cd); s.collection.objects.link(c)
    c.location=(98,-61,207)
    c.rotation_euler=(Vector((35,43,184))-c.location).to_track_quat('-Z','Y').to_euler()
    cd.lens=45; cd.clip_end=3000; s.camera=c
    s.render.filepath=os.path.splitext(os.path.abspath(a.output))[0]+'_crown_detail.png'
    t=time.time(); bpy.ops.render.render(write_still=True)
    report.update(camera=c.name,position=list(c.location),rotation=list(c.rotation_euler),lens=cd.lens,
                  render_seconds=time.time()-t,output_filename=os.path.basename(s.render.filepath))
    with open(os.path.splitext(s.render.filepath)[0]+'.json','w') as f:json.dump(report,f,ensure_ascii=False,indent=2)
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
