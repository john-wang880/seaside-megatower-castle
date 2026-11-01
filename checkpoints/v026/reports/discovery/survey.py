import bpy,json,hashlib,collections
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path('work/lateral_coverage_v025');src=Path('work/v025/castle_v025.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();H=sha(src);assert H=='8a3590082c99a69d50d444f77165fae57fb611cf069cecda03fdf0c6c17cadd2'
bpy.ops.wm.open_mainfile(filepath=str(src.resolve()),use_scripts=False);s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();origcam=s.camera;arch=[];walls=[]
for o in s.objects:
 if o.type!='MESH' or o.hide_render or o.hide_get():continue
 if not any(t in o.name.lower()for t in ['citadel','tower','ashlar','masonry','facade','roof','crown','rib','bridge','v012','v009','v020','v021','v022','v024','v025']):continue
 if any(t in o.name.lower()for t in ['woodland','tree','wave','cloud','foam']):continue
 eo=o.evaluated_get(dg);m=eo.to_mesh();wv=[o.matrix_world@v.co for v in m.vertices];arch.extend(v for v in wv if -170<v.x<90 and -15<v.y<130)
 for f in m.polygons:
  n=o.matrix_world.to_3x3()@f.normal
  if abs(n.x)<.95 or f.area<100:continue
  vs=[wv[i]for i in f.vertices];lo=[min(v[k]for v in vs)for k in range(3)];hi=[max(v[k]for v in vs)for k in range(3)]
  if hi[2]<35:continue
  walls.append({'object':o.name,'evaluated_face':f.index,'bounds':[lo,hi],'normal':list(n),'area':f.area,'material':m.materials[f.material_index].name if m.materials else None,'vertex_count':len(f.vertices)})
 eo.to_mesh_clear()
cam=bpy.data.objects.new('READONLY west lateral overview',origcam.data.copy());s.collection.objects.link(cam);cam.location=(-480,-30,180);target=Vector((-35,55,105));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=45;cam.data.sensor_width=36;cam.data.sensor_fit='HORIZONTAL';cam.data.shift_x=cam.data.shift_y=0;cam.data.clip_start=.1;cam.data.clip_end=3000;s.render.resolution_x=1200;s.render.resolution_y=866;s.render.resolution_percentage=100;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
pr=[world_to_camera_view(s,cam,v)for v in arch];pb=[[min(v[k]for v in pr),max(v[k]for v in pr)]for k in range(3)]
def vol(o):
 mats=[m for m in o.data.materials if m] if o.type=='MESH' else []
 return bool(mats) and all(m.use_nodes and any(n.type=='OUTPUT_MATERIAL' and n.is_active_output and n.inputs['Volume'].is_linked and not n.inputs['Surface'].is_linked for n in m.node_tree.nodes)for m in mats)
def ray(a,b):
 a=Vector(a);d=(Vector(b)-a).normalized();skipped=[]
 for _ in range(40):
  ok,p,n,f,o,_=s.ray_cast(dg,a,d)
  if not ok:return {'hit':None,'skipped':skipped}
  if not o.hide_render and not o.hide_get() and not vol(o):return {'hit':{'object':o.name,'face':f,'point':list(p),'normal':list(n),'target_distance':(p-Vector(b)).length},'skipped':skipped}
  skipped.append(o.name);a=p+d*.001
 return {'hit':None,'skipped':skipped}
# Probe actual west-oriented large wall polygon centers; not backface/root certification.
points=[]
for w in walls:
 if w['normal'][0]>-.95:continue
 lo,hi=w['bounds'];q=[(lo[k]+hi[k])/2 for k in range(3)]
 if not (-160<q[0]<80 and -10<q[1]<130):continue
 r={k:ray(a,q) for k,a in {'hero':origcam.location,'rear':(-50,500,210),'lateral':cam.location}.items()};p=world_to_camera_view(s,cam,Vector(q));points.append({'wall':w,'target':q,'projection':list(p),'sightlines':r})
D={k:getattr(cam.data,k)for k in ['lens','sensor_width','sensor_height','sensor_fit','shift_x','shift_y','clip_start','clip_end']};matrix=[list(r)for r in cam.matrix_world]
R={'source_sha256':H,'source_unchanged':sha(src)==H,'units':{'system':s.unit_settings.system,'scale_length':s.unit_settings.scale_length,'length_unit':s.unit_settings.length_unit,'note':'Coordinate units; no global engineering calibration'},'source_scene_frame':s.frame_current,'large_lateral_faces':walls,'west_face_centroid_visibility':points,'camera':{'location':list(cam.location),'target':list(target),'matrix':matrix,'data':D,'resolution':[1200,866],'architecture_projection_bounds':pb,'vertices_sampled':len(pr),'all_in_frame_3percent':all(p.z>0 and .03<p.x<.97 and .03<p.y<.97 for p in pr)},'limits':'Finite polygon-center opaque rays only. Volume-only containers skipped geometrically, not hidden or optical visibility certified. Plain faces/shadows not defects. No model save or render.'}
(P/'survey.json').write_text(json.dumps(R,indent=2));(P/'views.json').write_text(json.dumps({'source_sha256':H,'source_scene_frame':s.frame_current,'resolution':[1200,866],'samples':80,'threads':8,'view_scope':'Elevated west lateral discovery, not walkthrough','views':{'west_lateral':{'location':list(cam.location),'target':list(target),'lens':45,'reference_matrix':matrix,'camera_data':D}}},indent=2));print('DONE',len(walls),len(points),pb)
