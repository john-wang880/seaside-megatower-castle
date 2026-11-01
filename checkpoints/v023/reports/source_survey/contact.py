import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('work/path_arrival_v022');src=Path('work/v022/castle_v022.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();h=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src.resolve()),use_scripts=False);s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();path=next(o for o in s.objects if o.name.startswith('Narrow winding limestone footpath'));terrain=[o for o in s.objects if o.type=='MESH'and'headland'in o.name.lower()and not o.hide_render and not o.hide_get()];trees=[(o,BVHTree.FromObject(o,dg))for o in terrain];vs=[path.matrix_world@v.co for v in path.data.vertices]
def ground(p):
 hits=[]
 for o,t in trees:
  inv=o.matrix_world.inverted();loc,n,f,d=t.ray_cast(inv@Vector((p.x,p.y,100)),inv.to_3x3()@Vector((0,0,-1)),200)
  if loc is not None:
   q=o.matrix_world@loc;hits.append({'object':o.name,'face':f,'z':q.z})
 return max(hits,key=lambda q:q['z'])if hits else None
rows=[]
for row in range(88,113):
 for j in range(7):
  v=vs[row*7+j];g=ground(v);rows.append({'row':row,'column':j,'position':list(v),'terrain':g,'path_above_terrain':v.z-g['z']if g else None})
samples=[]
for f in path.data.polygons:
 r=min(f.vertices)//7
 if not 95<=r<=109:continue
 pts=[sum((vs[i]for i in f.vertices),Vector())/3]
 for a,b in zip(f.vertices,list(f.vertices[1:])+[f.vertices[0]]):pts.append((vs[a]+vs[b])*.5)
 for kind,p in enumerate(pts):
  g=ground(p);samples.append({'path_face':f.index,'row':r,'sample':'centroid'if kind==0 else'edge_midpoint','position':list(p),'terrain':g,'path_above_terrain':p.z-g['z']if g else None,'material':path.data.materials[f.material_index].name})
# The actual path does not end at the V009 apron. Measure closest surface to apron edge references.
t=BVHTree.FromObject(path,dg);near=[]
for y in[36.4,38,39.6]:
 apron=bpy.data.objects['V009 | terrain-following woodland entry apron'];candidates=[apron.matrix_world@v.co for v in apron.data.vertices if abs(v.co.x+91.5)<1e-4 and abs(v.co.y-y)<1e-4];assert candidates;q=max(candidates,key=lambda v:v.z)
 loc,n,face,dist=t.find_nearest(q);near.append({'apron_edge_point':list(q),'nearest_path_point':list(loc),'distance_coordinate_units':dist,'path_face':face})
# Finite centerline continuation probes identify terrain exposure and overhead structures, not navigation certification.
continuation=[]
for row in[95,98,101,104,107,110,113,116,119,122,126]:
 p=vs[row*7+3];g=ground(p);r={'row':row,'path_center':list(p),'terrain':g}
 for label,org,dr in[('up',p+Vector((0,0,.02)),Vector((0,0,1))),('down',p-Vector((0,0,.02)),Vector((0,0,-1)))]:
  for _ in range(60):
   ok,loc,n,face,o,m=s.ray_cast(dg,org,dr,distance=200)
   if not ok:break
   if o!=path and not o.hide_render and not o.hide_get():r[label]={'object':o.name,'face':face,'position':list(loc),'distance':(loc-p).length};break
   org=loc+dr*.001
 continuation.append(r)
center=[vs[i*7+3]for i in range(127)];grades=[]
for i in range(88,126):
 a,b=center[i:i+2];horizontal=math.hypot(b.x-a.x,b.y-a.y);grades.append({'rows':[i,i+1],'horizontal_distance':horizontal,'dz':b.z-a.z,'slope':(b.z-a.z)/horizontal})
(P/'contact.json').write_text(json.dumps({'source_sha256':h,'source_unchanged':sha(src)==h,'terrain_objects':[o.name for o in terrain],'vertex_samples':rows,'interior_samples':samples,'apron_to_path_nearest_samples':near,'path_continuation':continuation,'centerline_grades':grades,'units':'coordinate units, not globally calibrated metres'},indent=2));print('DZ',min(q['path_above_terrain']for q in samples),max(q['path_above_terrain']for q in samples),'BURIED',sum(q['path_above_terrain']<0 for q in samples),len(samples));print('APRON',near);print('END',continuation[-3:])
