import bpy,json,math,hashlib,argparse,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
p=argparse.ArgumentParser();p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);original_sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
light=bpy.data.objects['V014 | landing marker practical warm source'];lp=light.matrix_world.translation;deps=bpy.context.evaluated_depsgraph_get();visible=[]
for o in bpy.data.objects:
 if o.type!='MESH' or o.hide_render or not o.visible_shadow or o.name.startswith(('Volume cloud','Air perspective')):continue
 eo=o.evaluated_get(deps);vs=[eo.matrix_world@Vector(v) for v in eo.bound_box];bb=([min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]);visible.append((o,eo,eo.matrix_world.inverted(),bb))
def segment_box(a,b,bb):
 lo,hi=0,1
 for k in range(3):
  d=b[k]-a[k]
  if abs(d)<1e-10:
   if not bb[0][k]<=a[k]<=bb[1][k]:return False
  else:
   p,q=(bb[0][k]-a[k])/d,(bb[1][k]-a[k])/d;lo=max(lo,min(p,q));hi=min(hi,max(p,q))
   if hi<lo:return False
 return True
camera=bpy.data.objects.new('TEMP arrival projection',bpy.data.cameras.new('TEMP arrival projection'));bpy.context.scene.collection.objects.link(camera);camera.location=(4.45,56.8,34.1);camera.rotation_euler=(Vector((4.45,65,34.1))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=28;bpy.context.scene.camera=camera;bpy.context.scene.render.resolution_x=900;bpy.context.scene.render.resolution_y=650;bpy.context.view_layer.update()
rows=[]
for x in [3.85,4.15,4.45,4.75,5.05]:
 for y in [58,58.5,59,59.5,60,60.5]:
  pt=Vector((x,y,32.627));hits=[]
  for o,eo,inv,bb in visible:
   if not segment_box(pt,lp,bb):continue
   origin=inv@pt;delta=inv@lp-origin;length=delta.length
   if length<1e-9:continue
   h,v,n,i=eo.ray_cast(origin,delta/length,distance=length-1e-4)
   if h:
    world=eo.matrix_world@v;hits.append({'object':o.name,'point':list(world),'distance_from_floor':(world-pt).length})
  uv=world_to_camera_view(bpy.context.scene,camera,pt);delta=lp-pt;cos=max(0,delta.z/delta.length)
  rows.append({'floor_point':list(pt),'light_visible':not hits,'closest_occluder':min(hits,key=lambda q:q['distance_from_floor']) if hits else None,'horizontal_arrival_pixel':[uv.x*900,(1-uv.y)*650],'in_frame':0<=uv.x<=1 and 0<=uv.y<=1,'distance':delta.length,'cosine':cos,'unoccluded_inverse_square_cosine_factor':cos/(delta.length**2)})
Path(a.report).write_text(json.dumps({'model_sha256':original_sha,'source_unchanged':original_sha==hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'light_position':list(lp),'rows':rows,'scope':'Direct geometric visibility at30 sampled central terminal-floor positions. Surface/light visibility only, no volumetric attenuation or photometric certification. Horizontal camera projection diagnoses image-ROI scope.'},indent=2));print('visible',sum(r['light_visible'] for r in rows),'inframe',sum(r['in_frame'] for r in rows))
