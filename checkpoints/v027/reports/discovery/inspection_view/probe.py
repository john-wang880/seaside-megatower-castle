import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
P=Path('work/interior_ceiling_v026');O=P/'inspection_view';src=Path('work/v026/castle_v026.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();H=sha(src)
if H!='efcd894acdc045a30f845f05267662957b656bc7fe0ee4cf48c05fc798b610ee':raise RuntimeError('source')
old=json.loads((P/'views.json').read_text());oldhash=sha(P/'views.json');v=old['views']['frame_0001'];loc=Vector(v['location']);dv=Vector(v['target'])-loc;yaw=math.atan2(dv.y,dv.x);pitch=math.radians(8);direction=Vector((math.cos(yaw)*math.cos(pitch),math.sin(yaw)*math.cos(pitch),math.sin(pitch)));target=loc+4*direction
bpy.ops.wm.open_mainfile(filepath=str(src.resolve()),use_scripts=False);s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();c=bpy.data.objects.new('READONLY ceiling inspection',bpy.data.cameras.new('READONLY ceiling inspection'));s.collection.objects.link(c);c.location=loc;c.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
for k,val in v['camera_data'].items():setattr(c.data,k,val)
bpy.context.view_layer.update();inv=c.matrix_world.inverted();W,Hh=old['resolution'];tx=c.data.sensor_width/(2*c.data.lens);ty=tx*Hh/W

def pr(p):
 q=inv@Vector(p);d=-q.z;xy=[(.5+q.x/d/(2*tx))*W,(.5-q.y/d/(2*ty))*Hh];return {'pixel':xy,'depth':d,'in_frame':d>0 and 0<=xy[0]<W and 0<=xy[1]<Hh}
def ray(p):
 d=Vector(p)-c.location;ok,q,n,f,o,_=s.ray_cast(dg,c.location,d.normalized(),distance=d.length+0.001);return {'object':o.name,'face':f,'point':list(q),'distance':(q-c.location).length,'target_distance':d.length}if ok else None
art=json.loads((P/'art_profile_review.json').read_text());profiles=[]
for p in art['profiles']:
 a=[pr(x)for x in p['intrados_samples']];profiles.append({'station_x':p['station_x'],'intrados_in_frame':sum(x['in_frame']for x in a),'intrados':a,'landmarks':{k:{**pr(pt),'first_hit':ray(pt)}for k,pt in p['landmarks'].items()}})
context=[]
for x in[-1.8,.4,2.6,4.45]:
 for y in[36.6,38,39.4]:
  for z in[29,31,32.8]:
   p=[x,y,z];context.append({'point':p,**pr(p),'first_hit':ray(p)})
lamps=[]
for o in s.objects:
 if o.type=='LIGHT' and o.name.startswith(('V013','V014')):lamps.append({'name':o.name,'point':list(o.matrix_world.translation),**pr(o.matrix_world.translation),'first_hit':ray(o.matrix_world.translation)})
# 5x5 near-plane rays, and six cardinal eye-neighborhood rays. Finite checks, not continuous camera-volume certification.
near=[]
for i in range(5):
 for j in range(5):
  local=Vector(((i/4*2-1)*tx*c.data.clip_start,(j/4*2-1)*ty*c.data.clip_start,-c.data.clip_start));p=c.matrix_world@local;near.append({'point':list(p),'first_hit':ray(p)})
eye=[]
for axis in range(3):
 for sign in[-1,1]:
  d=Vector((0,0,0));d[axis]=sign;ok,q,n,f,o,_=s.ray_cast(dg,c.location,d,distance=3);eye.append({'direction':list(d),'object':o.name if ok else None,'distance':(q-c.location).length if ok else None})
recipe={'location':list(loc),'target':list(target),'lens':26,'clip_start':.05,'clip_end':3000,'reference_matrix':[list(r)for r in c.matrix_world],'camera_data':{k:getattr(c.data,k)for k in v['camera_data']}}
(O/'views.json').write_text(json.dumps({'source_sha256':H,'source_scene_frame':s.frame_current,'resolution':[W,Hh],'samples':80,'threads':8,'views':{'ceiling_inspection':recipe},'scope':'NEW separate standing-eye inspection, same frame1 position/yaw/lens, pitch +8 degrees. Historical walk unchanged.'},indent=2))
report={'source_sha256':H,'source_unchanged':sha(src)==H,'historical_views_unchanged':sha(P/'views.json')==oldhash,'pitch_degrees':8,'yaw_degrees':math.degrees(yaw),'profiles':profiles,'context':context,'lights':lamps,'nearplane_samples':near,'eye_cardinal':eye,'limits':'Intrados is disclosed monotone shallow surrogate, not final circular geometry. Point projections and finite rays are feasibility only, not rendered readability/full near-volume collision proof.'};(O/'report.json').write_text(json.dumps(report,indent=2));print('COUNTS',[(p['station_x'],p['intrados_in_frame'])for p in profiles]);print('NEAR HITS',sum(p['first_hit']is not None for p in near));print('SOURCE',report['source_unchanged'])
