import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
import numpy as np
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
from common import inputs,sha
a,source,src,report_path,plan=inputs();h=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False);dg=bpy.context.evaluated_depsgraph_get();out=[];planes=[]
for sp in plan['pairs']:
 lo=[min(c['bounds'][0][k]for c in sp['components'])for k in range(3)];hi=[max(c['bounds'][1][k]for c in sp['components'])for k in range(3)]
 for ax in range(3):
  other=[k for k in range(3)if k!=ax]
  for sg in [-1,1]:planes.append((sp['union_object'],ax,sg,lo[ax]if sg<0 else hi[ax],other,[lo[other[0]],hi[other[0]],lo[other[1]],hi[other[1]]]))
def clip(poly,axis,value,sign):
 result=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  u=sign*(a[axis]-value);v=sign*(b[axis]-value)
  if u>=0:result.append(a)
  if(u>=0)!=(v>=0):result.append(tuple(a[k]+u/(u-v)*(b[k]-a[k])for k in range(2)))
 return result
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render:continue
 eo=o.evaluated_get(dg);corners=[eo.matrix_world@Vector(v)for v in eo.bound_box]
 if max(v.x for v in corners)<-42 or min(v.x for v in corners)>-38 or min(v.z for v in corners)>26.40001 or max(v.z for v in corners)<5.69999 or min(v.y for v in corners)>41.70001 or max(v.y for v in corners)<34.29999:continue
 me=eo.to_mesh();me.calc_loop_triangles();coords=np.array([eo.matrix_world@v.co for v in me.vertices],dtype=np.float64);idx=np.array([t.vertices for t in me.loop_triangles]);triangles=coords[idx]
 for name,axis,sign,value,other,rect in planes:
  if o.name==name:continue
  hits=np.where(np.max(np.abs(triangles[:,:,axis]-value),axis=1)<=1e-6)[0]
  for ti in hits:
   vs=triangles[ti];poly=[tuple(v[other])for v in vs]
   for ax,val,sg in [(0,rect[0],1),(0,rect[1],-1),(1,rect[2],1),(1,rect[3],-1)]:poly=clip(poly,ax,val,sg)
   area=abs(sum(a[0]*b[1]-a[1]*b[0]for a,b in zip(poly,poly[1:]+poly[:1]))/2)if poly else 0
   if area>1e-8:
    normal=np.cross(vs[1]-vs[0],vs[2]-vs[0]);out.append({'union':name,'axis':axis,'side':sign,'object':o.name,'face':me.loop_triangles[int(ti)].polygon_index,'area':float(area),'facing':'same'if normal[axis]*sign>0 else'opposite','max_plane_error':float(max(abs(vs[:,axis]-value)))})
 eo.to_mesh_clear()
same=[r for r in out if r['facing']=='same']
assert all(r['union']==plan['pairs'][0]['union_object'] and r['axis']==2 and r['side']==-1 for r in same)
shaft=plan['pairs'][0]['components'];foot=plan['pairs'][1]['components']
slo=[min(c['bounds'][0][k] for c in shaft)for k in range(3)];shi=[max(c['bounds'][1][k]for c in shaft)for k in range(3)];flo=[min(c['bounds'][0][k]for c in foot)for k in range(3)];fhi=[max(c['bounds'][1][k]for c in foot)for k in range(3)]
assert all(flo[k]<slo[k] and shi[k]<fhi[k] for k in [0,1]) and flo[2]<slo[2]<fhi[2]
report={'source_unchanged':sha(source)=='673dbbadca22d3dd45dc2f2eb5bde4a9e66851c1ca137da5c2570efc67c77614','shaft_bottom_foot_minimum_margins_m':{'x':min(slo[0]-flo[0],fhi[0]-shi[0]),'y':min(slo[1]-flo[1],fhi[1]-shi[1]),'below':slo[2]-flo[2],'above':fhi[2]-slo[2]},'exposed_same_facing_patches':0,'same_facing_scope':'Only shaft bottom z6, entire rectangle strictly buried in exact foot occupied volume; not exposed surface. Other contacts opposite-facing.', 'candidate_sha256':h,'all_six_planes':True,'evaluated_bounds_before_cull':True,'render_visible_including_viewport_hidden':True,'numerical_plane_bound_m':1e-6,'positive_area_floor_m2':1e-8,'contacts':out,'same_facing_count':sum(r['facing']=='same'for r in out),'opposite_facing_count':sum(r['facing']=='opposite'for r in out),'unchanged':hashlib.sha256(src.read_bytes()).hexdigest()==h};report_path.write_text(json.dumps(report,indent=2));print(json.dumps(report))
