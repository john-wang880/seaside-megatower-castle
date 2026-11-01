import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
P=Path('work/west_lower_tier_v021');src=Path('work/v021/castle_v021.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();h=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src.resolve()),use_scripts=False);s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();survey=json.load(open(P/'survey.json'));rec=next(o for o in survey['objects']if 'retained west rib' in o['object']);comps={c['seed']:c for c in rec['components']}
def inside(seed,point):
 c=comps[seed];vs=[Vector(v['co'])for v in c['vertices']];ids={v['id']:i for i,v in enumerate(c['vertices'])};center=sum(vs,Vector())/len(vs);tree=BVHTree.FromPolygons([v-center for v in vs],[[ids[i]for i in f['vertices']]for f in c['faces']]);votes=[]
 for dr in [(1,.371,.613),(.217,1,.489),(.529,.193,1)]:
  dr=Vector(dr).normalized();p=Vector(point)-center;hits=0
  for _ in range(20):
   loc,n,fi,dist=tree.ray_cast(p,dr,1000)
   if loc is None:break
   hits+=1;p=loc+dr*.00001
  votes.append(bool(hits%2))
 return votes
contacts=[]
for seat,pt in[(96,[-120.44,85.3,79.3]),(192,[-120.44,85.3,103.4])]:contacts.append({'rib_seed':56,'seat_seed':seat,'strict_interior_witness':pt,'rib_three_ray_votes':inside(56,pt),'seat_three_ray_votes':inside(seat,pt)})
def halfspaces(seed,point):
 c=comps[seed];vs={v['id']:tuple(v['co'])for v in c['vertices']};center=tuple(sum(v[k]for v in vs.values())/len(vs)for k in range(3))
 def sub(a,b):return tuple(x-y for x,y in zip(a,b))
 def dot(a,b):return sum(x*y for x,y in zip(a,b))
 def cross(a,b):return(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
 rows=[]
 for f in c['faces']:
  a,b,cc=[vs[i]for i in f['vertices'][:3]];n=cross(sub(b,a),sub(cc,a));mag=dot(n,n)**.5;n=tuple(x/mag for x in n)
  if dot(n,sub(center,a))>0:n=tuple(-x for x in n)
  rows.append({'face':f['id'],'point_signed_distance':dot(n,sub(point,a)),'max_source_vertex_plane_distance':max(dot(n,sub(v,a))for v in vs.values())})
 # Retain measured nonplanarity; no planarity-tolerance waiver.
 assert max(r['point_signed_distance']for r in rows)<-.1
 winding=0
 for f in c['faces']:
  ids=f['vertices']
  for i in range(1,len(ids)-1):
   a,b,cc=[sub(vs[j],point)for j in [ids[0],ids[i],ids[i+1]]];la,lb,lc=[dot(v,v)**.5 for v in[a,b,cc]]
   winding+=2*math.atan2(dot(a,cross(b,cc)),la*lb*lc+dot(a,b)*lc+dot(b,cc)*la+dot(cc,a)*lb)
 normalized=winding/(4*math.pi);assert abs(abs(normalized)-1)<1e-8
 return {'plane_distances':rows,'signed_solid_angle_winding':normalized}
for r in contacts:
 r['rib_convex_plane_check']=halfspaces(r['rib_seed'],r['strict_interior_witness']);r['seat_convex_plane_check']=halfspaces(r['seat_seed'],r['strict_interior_witness'])
 r['method_note']='Exact source faces triangulated for double-precision signed solid-angle winding: magnitude1 proves interior. Source slight nonplanarity measured, not flattened. Witness more than0.1m behind each face plane. Initial floatBVH upperrib ray disagreed and is retained as diagnostic, not relabeled three-ray success.'

s.render.resolution_x=1200;s.render.resolution_y=866;s.render.resolution_percentage=100;d=s.camera.data.copy();cam=bpy.data.objects.new('READONLY west lowest shaft tier camera',d);s.collection.objects.link(cam);cam.location=(-98.25,3.5,98.5);target=Vector((-132,86,91));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=55;d.shift_x=d.shift_y=0;d.clip_start=.05;d.clip_end=10000;bpy.context.view_layer.update()
bounds=[[-148,83.5,76],[-117,91,107]];proj=[list(world_to_camera_view(s,cam,Vector((x,y,z))))for x in[bounds[0][0],bounds[1][0]]for y in[bounds[0][1],bounds[1][1]]for z in[bounds[0][2],bounds[1][2]]];margin=min(min(p[0],p[1],1-p[0],1-p[1])for p in proj)
rows=[]
pts=[('rib',(-120.444,84.57499694824219,z))for z in[80,84,88,92,96,100,102.8]]+[('lower_lancet_center',(x,86,90))for x in[-137,-128.9]]
for label,pt in pts:
 pt=Vector(pt);origin=cam.location.copy();dr=(pt-origin).normalized();row={'label':label,'target':list(pt),'projection':list(world_to_camera_view(s,cam,pt))}
 for _ in range(100):
  ok,loc,n,face,o,m=s.ray_cast(dg,origin,dr)
  if not ok:break
  if not o.hide_render and not o.hide_get():row.update(object=o.name,face=face,hit=list(loc),target_distance_error=(loc-pt).length);break
  origin=loc+dr*.001
 rows.append(row)
report={'source_sha256':h,'source_unchanged':sha(src)==h,'seat_contact_witnesses':contacts,'camera_location':list(cam.location),'target':list(target),'camera_matrix_world':[list(r)for r in cam.matrix_world],'camera_rotation_euler':list(cam.rotation_euler),'camera_data':{'lens':d.lens,'sensor_width':d.sensor_width,'sensor_height':d.sensor_height,'sensor_fit':d.sensor_fit,'shift_x':d.shift_x,'shift_y':d.shift_y,'clip_start':d.clip_start,'clip_end':d.clip_end,'type':d.type,'dof_use':d.dof.use_dof},'resolution':[1200,866],'target_bounds':bounds,'bounds_projection':proj,'minimum_frame_margin_fraction':margin,'visibility_samples':rows,'rendered':False,'saved':False};(P/'camera_preflight.json').write_text(json.dumps(report,indent=2));print('MARGIN',margin,'CONTACT',contacts,'RAYS',[(r['label'],r.get('object'),r.get('target_distance_error'))for r in rows]);assert margin>.04
