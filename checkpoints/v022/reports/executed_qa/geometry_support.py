"""Evaluated whole-component geometry and disposable exact Boolean measurements."""
import bpy,bmesh,collections,math
from mathutils import Vector

def shape(key,vertices,faces,triangles=None):
 vs=[tuple(v) for v in vertices];fs=[tuple(f) for f in faces];counts=collections.defaultdict(list)
 for f in fs:
  for a,b in zip(f,f[1:]+f[:1]):counts[tuple(sorted((a,b)))].append((a,b))
 closed=all(len(v)==2 and v[0]==v[1][::-1] for v in counts.values()) and bool(fs)
 bm=bmesh.new();bv=[bm.verts.new(v) for v in vs]
 for f in fs:bm.faces.new([bv[i] for i in f])
 volume=bm.calc_volume(signed=True);vertex_manifold=all(v.is_manifold for v in bm.verts if v.link_faces);bm.free()
 return {'key':key,'vertices':vs,'faces':fs,'triangles':triangles,'bounds':[[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]],'closed_oriented':closed and vertex_manifold,'signed_volume':volume}
def overlap(a,b,eps=0):return all(min(a[1][k],b[1][k])-max(a[0][k],b[0][k])>eps for k in range(3))
def evaluated_components(obj,deps):
 eo=obj.evaluated_get(deps);me=eo.to_mesh(preserve_all_data_layers=True,depsgraph=deps);me.calc_loop_triangles();parent=list(range(len(me.vertices)))
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for edge in me.edges:
  x,y=map(root,edge.vertices);parent[max(x,y)]=min(x,y)
 groups=collections.defaultdict(list);faces=collections.defaultdict(list);triangles=collections.defaultdict(list)
 for v in me.vertices:groups[root(v.index)].append(v.index)
 for f in me.polygons:faces[root(f.vertices[0])].append(tuple(f.vertices))
 for t in me.loop_triangles:triangles[root(t.vertices[0])].append(tuple(t.vertices))
 result=[]
 for seed,ids in groups.items():
  if not faces[seed]:continue
  im={v:i for i,v in enumerate(ids)};vs=[tuple(eo.matrix_world@me.vertices[i].co) for i in ids];fs=[tuple(im[i] for i in f) for f in faces[seed]];ts=[tuple(im[i] for i in f) for f in triangles[seed]]
  result.append({'key':obj.name+'::'+str(seed),'object':obj.name,'seed':seed,'ids':ids,'vertices':vs,'faces':fs,'triangles':ts,'bounds':[[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]]})
 eo.to_mesh_clear();return result
def enrich(s):
 if 'closed_oriented' not in s:s.update(shape(s['key'],s['vertices'],s['faces'],s['triangles']))
 return s

def intersection(a,b):
 if not overlap(a['bounds'],b['bounds']):return {'volume':0.0,'closed_result':True,'broadphase_disjoint':True}
 enrich(a);enrich(b)
 if not a['closed_oriented'] or not b['closed_oriented']:return {'volume':None,'reason':'Open or inconsistent operand','operands':[a['key'],b['key']]}
 # Center all temporary operands together to reduce world-coordinate cancellation.
 origin=Vector([(min(a['bounds'][0][k],b['bounds'][0][k])+max(a['bounds'][1][k],b['bounds'][1][k]))/2 for k in range(3)]);created=[]
 try:
  for s in [a,b]:
   me=bpy.data.meshes.new('QA temporary contact');me.from_pydata([Vector(v)-origin for v in s['vertices']],[],s['triangles'] or s['faces']);me.update();obj=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(obj);created.append(obj)
  mod=created[0].modifiers.new('QA exact intersection','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=created[1];deps=bpy.context.evaluated_depsgraph_get();eo=created[0].evaluated_get(deps);me=eo.to_mesh();bm=bmesh.new();bm.from_mesh(me);volume=abs(bm.calc_volume(signed=True));closed=all(e.is_manifold for e in bm.edges);facecount=len(bm.faces);bm.free();eo.to_mesh_clear();return {'volume':volume,'closed_result':closed,'faces':facecount}
 finally:
  for obj in created:me=obj.data;bpy.data.objects.remove(obj,do_unlink=True);bpy.data.meshes.remove(me)

def coplanar_y_contact(a,b,y,tolerance=1e-7):
 """Positive common triangle area on a measured shared Y-plane; not AABB touch."""
 def cross(p,q):return p[0]*q[1]-p[1]*q[0]
 def signed(poly):return sum(cross(poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly)))/2
 def clip(subject,triangle):
  if signed(triangle)<0:triangle=triangle[::-1]
  poly=subject
  for i,u in enumerate(triangle):
   v=triangle[(i+1)%3];edge=(v[0]-u[0],v[1]-u[1]);old=poly;poly=[]
   if not len(old):break
   for j,p in enumerate(old):
    q=old[(j+1)%len(old)];dp=cross(edge,(p[0]-u[0],p[1]-u[1]));dq=cross(edge,(q[0]-u[0],q[1]-u[1]))
    if dp>=0:poly.append(p)
    if (dp>=0)!=(dq>=0):t=dp/(dp-dq);poly.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
  return abs(signed(poly)) if len(poly)>=3 else 0.0
 def triangles(s):return [[(s['vertices'][i][0],s['vertices'][i][2]) for i in t] for t in s['triangles'] if all(abs(s['vertices'][i][1]-y)<=tolerance for i in t)]
 aa=triangles(a);bb=triangles(b);areas=[clip(x,z) for x in aa for z in bb];return {'shared_y':y,'plane_tolerance_m':tolerance,'source_triangle_counts':[len(aa),len(bb)],'maximum_actual_triangle_intersection_area':max(areas,default=0.0),'sum_actual_triangle_intersection_areas':sum(areas),'positive_area_pairs':sum(v>1e-10 for v in areas)}

def triangle_surface_contact(a,b,epsilon=1e-7):
 """Float64 triangle SAT including coplanar axes; epsilon is reported, not geometry expansion."""
 import numpy as np
 def arrays(s):
  if '_triangle_arrays' not in s:
   s['_triangle_arrays']=np.asarray(s['vertices'],float)[np.asarray(s['triangles'],int)];s['_triangle_low']=s['_triangle_arrays'].min(1);s['_triangle_high']=s['_triangle_arrays'].max(1)
  return s['_triangle_arrays']
 aa=arrays(a);bb=arrays(b)
 for i,t in enumerate(aa):
  ids=np.where(np.all(b['_triangle_low']<=t.max(0)+epsilon,axis=1)&np.all(b['_triangle_high']>=t.min(0)-epsilon,axis=1))[0]
  for j in ids:
   u=bb[j];ea=np.roll(t,-1,axis=0)-t;eb=np.roll(u,-1,axis=0)-u;na=np.cross(ea[0],ea[1]);nb=np.cross(eb[0],eb[1]);axes=np.array([na,nb]+[np.cross(x,y) for x in ea for y in eb]+[np.cross(na,e) for e in ea]+[np.cross(nb,e) for e in eb]);length=np.linalg.norm(axes,axis=1);axes=axes[length>1e-12]/length[length>1e-12,None]
   if not len(axes):return {'state':'uncertain_degenerate_triangle','triangles':[i,int(j)]}
   p=t@axes.T;q=u@axes.T;gap=float(np.max(np.maximum(p.min(0)-q.max(0),q.min(0)-p.max(0))))
   if gap<=epsilon:return {'state':'actual_surface_contact' if gap<=1e-9 else 'near_uncertain','triangles':[i,int(j)],'separating_axis_gap':gap,'epsilon':epsilon}
 return {'state':'no_surface_contact','epsilon':epsilon}

def coplanar_triangle_area(a,b,plane_tolerance=6e-6):
 """Actual shared triangle area, general plane. Report max plane deviation explicitly."""
 import numpy as np
 def cross(p,q):return p[0]*q[1]-p[1]*q[0]
 def area(poly):return sum(cross(poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly)))/2
 def clip(subject,triangle):
  if area(triangle)<0:triangle=triangle[::-1]
  poly=subject
  for i,u in enumerate(triangle):
   v=triangle[(i+1)%3];edge=(v[0]-u[0],v[1]-u[1]);old=poly;poly=[]
   if not len(old):break
   for j,p in enumerate(old):
    q=old[(j+1)%len(old)];dp=cross(edge,(p[0]-u[0],p[1]-u[1]));dq=cross(edge,(q[0]-u[0],q[1]-u[1]))
    if dp>=0:poly.append(p)
    if (dp>=0)!=(dq>=0):t=dp/(dp-dq);poly.append(p+t*(q-p))
  return (poly,abs(area(poly))) if len(poly)>=3 else ([],0)
 av=np.asarray(a['vertices'],float);bv=np.asarray(b['vertices'],float);at=av[np.asarray(a['triangles'])];bt=bv[np.asarray(b['triangles'])];pairs=[]
 for i,t in enumerate(at):
  normal=np.cross(t[1]-t[0],t[2]-t[0]);length=np.linalg.norm(normal)
  if length<1e-12:continue
  normal/=length;axis=int(np.argmax(abs(normal)));keep=[k for k in range(3) if k!=axis]
  for j,u in enumerate(bt):
   other=np.cross(u[1]-u[0],u[2]-u[0]);olen=np.linalg.norm(other)
   if olen<1e-12 or abs(normal@(other/olen))<1-1e-7:continue
   polygon,projected_area=clip(t[:,keep],u[:,keep]);amount=projected_area/abs(normal[axis])
   if amount<=1e-12:continue
   # Plane roundoff is assessed only over the actual common projected patch,
   # never distant vertices of a much larger host face.
   other/=olen;plane_a=normal@t[0];plane_b=other@u[0];deviations=[]
   for point in polygon:
    height_a=(plane_a-normal[keep]@point)/normal[axis];height_b=(plane_b-other[keep]@point)/other[axis];deviations.append(abs(height_a-height_b)*abs(normal[axis]))
   deviation=max(deviations)
   if deviation>plane_tolerance:continue
   pairs.append({'triangles':[i,j],'area_m2':float(amount),'max_plane_deviation_m':float(deviation),'normal':normal.tolist()})
 return {'positive_area_pairs':pairs,'sum_area_m2':sum(p['area_m2'] for p in pairs),'max_plane_deviation_m':max((p['max_plane_deviation_m'] for p in pairs),default=0),'plane_tolerance_m':plane_tolerance,'scope':'Shared projected area of actual near-coplanar triangles, with measured plane deviation. 6micrometers bounds float32 interpolated top coordinates; not fictitious positive solid embed.'}
