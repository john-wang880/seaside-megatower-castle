import bpy,json,hashlib,collections,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path('work/rear_landward_v023');src=Path('work/v023/castle_v023.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();h=sha(src);assert h=='c4b1dda3b8f70e4c8cb0171834b2150b6d7610f6296847362fd204b2dfa7ad51';bpy.ops.wm.open_mainfile(filepath=str(src.resolve()),use_scripts=False);s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();inventory=[];comps=[];archverts=[]
for o in s.objects:
 if o.type!='MESH'or o.hide_render or o.hide_get():continue
 bb=[o.matrix_world@Vector(v)for v in o.bound_box];lo=[min(v[k]for v in bb)for k in range(3)];hi=[max(v[k]for v in bb)for k in range(3)];inventory.append({'object':o.name,'bounds':[lo,hi],'raw_counts':[len(o.data.vertices),len(o.data.polygons)]})
 architecture=any(q in o.name.lower()for q in ['citadel','tower','ashlar','masonry','facade','roof','crown','rib','v012','v009','bridge','v020','v021','v022'])and not any(q in o.name.lower()for q in ['woodland','tree','wave','cloud','foam'])
 if not architecture:continue
 eo=o.evaluated_get(dg);m=eo.to_mesh();world=[o.matrix_world@v.co for v in m.vertices];archverts.extend(v for v in world if -170<v.x<90 and -15<v.y<130)
 if 'slate' in o.name.lower()or len(m.vertices)>80000:eo.to_mesh_clear();continue
 parent=list(range(len(m.vertices)))
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for e in m.edges:
  a,b=map(root,e.vertices);parent[max(a,b)]=min(a,b)
 groups=collections.defaultdict(list);fg=collections.defaultdict(list)
 for v in m.vertices:groups[root(v.index)].append(v.index)
 for f in m.polygons:fg[root(f.vertices[0])].append(f)
 for seed,ids in groups.items():
  vs=[world[i]for i in ids];a=[min(v[k]for v in vs)for k in range(3)];b=[max(v[k]for v in vs)for k in range(3)]
  if not ((a[0]<83 and b[0]>-10 and a[1]<125 and b[1]>55 and a[2]<80 and b[2]>15)or(a[0]<-110 and b[0]>-160 and a[1]<125 and b[1]>100 and a[2]<90 and b[2]>20)):continue
  nf=[f for f in fg[seed]if(o.matrix_world.to_3x3()@f.normal).y>.6]
  comps.append({'object':o.name,'seed':seed,'bounds':[a,b],'vertex_count':len(ids),'face_count':len(fg[seed]),'north_face_count':len(nf),'north_area':sum(f.area for f in nf),'north_face_ids':[f.index for f in nf],'material_indices':sorted({f.material_index for f in fg[seed]}),'material_slots':[x.name if x else None for x in m.materials]})
 eo.to_mesh_clear()
cam=bpy.data.objects.new('READONLY rear landward overview',s.camera.data.copy());s.collection.objects.link(cam);cam.location=(-50,500,210);target=Vector((-35,55,105));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=45;cam.data.sensor_fit='HORIZONTAL';cam.data.sensor_width=36;cam.data.shift_x=cam.data.shift_y=0;cam.data.clip_start=.1;cam.data.clip_end=3000;s.render.resolution_x=1200;s.render.resolution_y=866;s.render.resolution_percentage=100;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();pr=[world_to_camera_view(s,cam,v)for v in archverts];pb=[[min(p[k]for p in pr),max(p[k]for p in pr)]for k in range(3)];assert all(p.z>0 and .03<p.x<.97 and .03<p.y<.97 for p in pr),pb
# Volume-only container boundaries are not opaque surfaces; keep all actual scene visibility unchanged.
def volume_only(ob):
 mats=[m for m in ob.data.materials if m]
 if not mats:return False
 for m in mats:
  outs=[n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output]if m.use_nodes else []
  if not outs or any(n.inputs['Surface'].is_linked or not n.inputs['Volume'].is_linked for n in outs):return False
 return True
volume_containers=[o.name for o in s.objects if o.type=='MESH' and volume_only(o)]
# Finite actual opaque-surface hit classification; optical transmittance remains unmeasured.
def ray(origin,direction):
 origin=Vector(origin);direction=Vector(direction).normalized()
 for _ in range(40):
  ok,p,n,fi,ob,mat=s.ray_cast(dg,origin,direction)
  if not ok:return None
  if not ob.hide_render and not ob.hide_get() and not volume_only(ob):return {'object':ob.name,'face':fi,'point':list(p),'normal':list(n),'evaluated_face_index':fi}
  origin=p+direction*.001
 return None
facade=[]
for x in[-145,-135,-125,0,20,35,50,70]:
 for z in[30,40,55,75,110,160]:facade.append({'north_probe_origin':[x,220,z],'hit':ray((x,220,z),(0,-1,0))})
floors=[]
for x in[-145,-130,-115,-5,5,20,40,60,75]:
 for y in[60,75,90,110,125]:floors.append({'xy':[x,y],'hit':ray((x,y,240),(0,0,-1))})
path=bpy.data.objects['Narrow winding limestone footpath | conformed to meadow'];endpoint=path.matrix_world@path.data.vertices[126*7+3].co
points={'main rear upper wall':(35,62.5,160),'main rear lower mass':(35,65,45),'north terrace terminal':(4.45,60.5,32.625),'west rear shaft':(-133,112,135),'west path endpoint':tuple(endpoint),'bridge rear midpoint':(-40,41.2,20),'main rear shore':(40,95,6)};sight=[]
for label,q in points.items():
 q=Vector(q);hit=ray(cam.location,q-cam.location);p=world_to_camera_view(s,cam,q);sight.append({'label':label,'target':list(q),'projection':list(p),'first_hit':hit,'distance_from_target':(Vector(hit['point'])-q).length if hit else None})
result={'source_scene_frame':s.frame_current,'volume_only_containers_skipped_for_rays':volume_containers,'source_sha256':h,'source_unchanged':sha(src)==h,'units':'coordinate units; no global engineering calibration','objects':inventory,'selected_rear_components':comps,'north_horizontal_probes':facade,'top_surface_probes':floors,'path_endpoint':list(endpoint),'camera':{'location':list(cam.location),'target':list(target),'matrix_world':[list(r)for r in cam.matrix_world],'data':{k:getattr(cam.data,k)for k in ['lens','sensor_width','sensor_height','sensor_fit','shift_x','shift_y','clip_start','clip_end']},'resolution':[1200,866],'actual_main_architecture_vertex_projection_bounds':pb,'projected_vertex_count':len(pr),'target_sightlines':sight},'limits':'No saved scene/render. Finite probes do not certify walkable access, structural integrity or all rear details. Volume cloud box boundaries are skipped for opaque-surface classification, not hidden for render; no optical transmittance claim.'};(P/'survey.json').write_text(json.dumps(result,indent=2));print('DONE',len(comps),pb)
