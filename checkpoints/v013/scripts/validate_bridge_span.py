"""Read-only component-wise point-in-solid checks for sampled walking volumes.

Closed disconnected components are tested separately, avoiding XOR cancellation
of overlapping solids. Three non-axis-aligned ray parities must agree. Open or
nonmanifold candidate components and boundary/ambiguous results fail acceptance.
This is sampled geometric evidence, not a proof of whole-volume accessibility.
"""
import argparse,bpy,json,sys,time,hashlib
from pathlib import Path
from collections import defaultdict,Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser();p.add_argument('--report',required=True);p.add_argument('--allow-collisions',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
start=time.time();floors=[]
def floor(obj,x,y,label):
 o=bpy.data.objects[obj]
 if o.hide_render and obj=='Western citadel_West_Ashlar stone variation':o=bpy.data.objects['V012 | legacy ashlar with buried-route clearance']
 assert not o.hide_render,'Floor must be currently visible'
 o=o.evaluated_get(bpy.context.evaluated_depsgraph_get());inv=o.matrix_world.inverted();h,v,n,i=o.ray_cast(inv@Vector((x,y,80)),inv.to_3x3()@Vector((0,0,-1)));assert h,(obj,x,y)
 z=(o.matrix_world@v).z;floors.append({'zone':label,'x':x,'y':y,'z':z})
for ix in range(85):
 x=-58+ix*.5
 for y in(36.6,38,39.4):
  obj='V007 | continuous stone passage threshold' if x<=-57.6 else ('V008 | eastern stepped approach embedded in rock' if x>=-16 else 'Western citadel_West_Ashlar stone variation')
  floor(obj,x,y,'bridge_span')
points=[(f,delta,Vector((f['x'],f['y'],f['z']+delta))) for f in floors for delta in(.05,1.1,2.0)]
lo=[min(v[k] for _,_,v in points) for k in range(3)];hi=[max(v[k] for _,_,v in points) for k in range(3)]
def contains(bb,q,eps=0):return all(bb[0][k]-eps<=q[k]<=bb[1][k]+eps for k in range(3))
def intersects(bb):return all(bb[1][k]>=lo[k] and bb[0][k]<=hi[k] for k in range(3))
dirs=[Vector(v).normalized() for v in[(.937,.183,.298),(-.297,.911,.287),(.231,-.417,.879)]]
def parity(tree,point,direction,distance):
 cursor=point.copy();n=0;remaining=distance
 while remaining>0 and n<512:
  loc,normal,index,d=tree.ray_cast(cursor,direction,remaining)
  if loc is None:return n%2,n
  advance=d+.0002;cursor+=direction*advance;remaining-=advance;n+=1
 return None,n
# Synthetic regression: classify interior/exterior, and independently retain
# two overlapping closed solids (never parity-XOR the entire joined mesh).
unit_vertices=[(x,y,z) for z in(0,1) for y in(0,1) for x in(0,1)]
unit_faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
unit=BVHTree.FromPolygons(unit_vertices,unit_faces,all_triangles=False)
self_tests={}
for label,point,expected in [('cube_inside',(.4,.5,.6),1),('cube_outside',(1.4,.5,.6),0)]:
 bits=[parity(unit,Vector(point),direction,10)[0] for direction in dirs]
 self_tests[label]=bits==[expected]*3
shifted=BVHTree.FromPolygons([(x+.5,y,z) for x,y,z in unit_vertices],unit_faces,all_triangles=False)
self_tests['overlap_keeps_both_solid_interiors']=all(parity(tree,Vector((.75,.5,.6)),d,10)[0]==1 for tree in(unit,shifted) for d in dirs)
# Regression: an Array modifier expands a unit cube into a second cube at
# x=3..4. Its evaluation must admit a point outside the original mesh AABB.
# Temporary datablocks are always removed, including assertion/error paths.
before_counts=(len(bpy.data.objects),len(bpy.data.meshes))
test_mesh=bpy.data.meshes.new('TEMP occupancy expanding-modifier test')
test_mesh.from_pydata(unit_vertices,[],unit_faces);test_mesh.update()
test_object=bpy.data.objects.new('TEMP occupancy expanding-modifier test',test_mesh)
bpy.context.scene.collection.objects.link(test_object)
try:
 modifier=test_object.modifiers.new('Expand bounding box','ARRAY');modifier.count=2
 modifier.relative_offset_displace=(3,0,0)
 bpy.context.view_layer.update();test_deps=bpy.context.evaluated_depsgraph_get()
 evaluated=test_object.evaluated_get(test_deps)
 ev=[evaluated.matrix_world@Vector(v) for v in evaluated.bound_box]
 eval_bb=([min(v[k] for v in ev) for k in range(3)],[max(v[k] for v in ev) for k in range(3)])
 raw_bb=([min(v[k] for v in unit_vertices) for k in range(3)],[max(v[k] for v in unit_vertices) for k in range(3)])
 target=Vector((3.5,.5,.5))
 self_tests['expanding_modifier_evaluated_aabb']=contains(eval_bb,target) and not contains(raw_bb,target)
finally:
 bpy.data.objects.remove(test_object,do_unlink=True)
 bpy.data.meshes.remove(test_mesh)
 bpy.context.view_layer.update()
self_tests['synthetic_temporary_datablocks_cleaned']=(len(bpy.data.objects),len(bpy.data.meshes))==before_counts
assert all(self_tests.values()),self_tests
surface_tests=[]
known_open_surfaces={'Castle headland | level courtyard and broken coastal escarpment','V010 | headland with local stair-edge clearance','Narrow winding limestone footpath | conformed to meadow'}
collisions=[];uncertain=[];tested_components=[];object_stats=[];deps=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
 if o.type!='MESH' or o.hide_render or o.name.startswith(('Volume cloud','Air perspective')):continue
 modifier_mismatch=[m.name for m in o.modifiers if m.show_viewport!=m.show_render]
 if modifier_mismatch:uncertain.append({'object':o.name,'reason':'viewport_render_modifier_visibility_mismatch','modifiers':modifier_mismatch})
 eo=o.evaluated_get(deps)
 # Cull only evaluated geometry: an expanding modifier can enter the route
 # even when the original mesh bounds are entirely outside it.
 bbox=[eo.matrix_world@Vector(v) for v in eo.bound_box];bb=([min(v[k] for v in bbox) for k in range(3)],[max(v[k] for v in bbox) for k in range(3)])
 if not intersects(bb):continue
 me=eo.to_mesh();world=eo.matrix_world;vs=[world@v.co for v in me.vertices];parent=list(range(len(vs)))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for e in me.edges:
  u,v=e.vertices;u=find(u);v=find(v)
  if u!=v:parent[v]=u
 groups=defaultdict(list)
 for i in range(len(vs)):groups[find(i)].append(i)
 candidate={}
 for seed,ids in groups.items():
  bb=([min(vs[i][k] for i in ids) for k in range(3)],[max(vs[i][k] for i in ids) for k in range(3)])
  if not intersects(bb):continue
  picks=[j for j,(_,_,q) in enumerate(points) if contains(bb,q)]
  if picks:candidate[seed]={'ids':ids,'bb':bb,'picks':picks,'faces':[]}
 for f in me.polygons:
  seed=find(f.vertices[0])
  if seed in candidate:candidate[seed]['faces'].append(tuple(f.vertices))
 for seed,c in candidate.items():
  ids=c['ids'];mapping={old:new for new,old in enumerate(ids)};faces=[tuple(mapping[i] for i in f) for f in c['faces']];coords=[vs[i] for i in ids]
  edge_counts=Counter(tuple(sorted((f[i],f[(i+1)%len(f)]))) for f in faces for i in range(len(f)))
  closed=bool(faces) and all(n==2 for n in edge_counts.values());detail={'object':o.name,'component_seed':min(ids),'vertices':len(ids),'polygons':len(faces),'closed_two_faces_per_edge':closed,'bounds':c['bb']}
  tested_components.append(detail)
  if not closed:
   if o.name in known_open_surfaces:
    # These named pre-existing sheets have no enclosed solid interior. Test them
    # as actual surfaces, not fictitious volumes inferred from their huge AABB.
    # Highest vertical surface must lie below the walking floor; a missing ray
    # means no surface at that XY. Also test the feet-to-head vertical segment
    # and exact sampled-point boundary proximity. Unknown open geometry fails.
    tree=BVHTree.FromPolygons(coords,faces,all_triangles=False,epsilon=0.0)
    floor_indices=sorted({j//3 for j in c['picks']})
    for fi in floor_indices:
     f=floors[fi];xy=(f['x'],f['y']);ceiling=c['bb'][1][2]+1
     top,normal,index,distance=tree.ray_cast(Vector((*xy,ceiling)),Vector((0,0,-1)),ceiling-c['bb'][0][2]+2)
     loc,n,idx,dist=tree.ray_cast(Vector((*xy,f['z']+.05)),Vector((0,0,1)),2.05)
     near_boundary=False
     for delta in(.05,1.1,2.0):
      nl,nn,ni,nd=tree.find_nearest(Vector((*xy,f['z']+delta)))
      if nd is not None and nd<.0005:near_boundary=True
     clear=(top is None or top.z<=f['z']+.001) and loc is None and not near_boundary
     rec={**f,'object':o.name,'component_seed':min(ids),'local_highest_surface_z':None if top is None else top.z,'feet_to_head_intersection':None if loc is None else list(loc),'sample_boundary_proximity':near_boundary,'surface_clear':clear,'scope':'Known open terrain/path sheet: surface collision tested, no enclosed-volume claim.'}
     surface_tests.append(rec)
     if not clear:collisions.append({**rec,'reason':'known_open_surface_blocks_walking_column'})
   else:
    for j in c['picks']:
     f,d,q=points[j];uncertain.append({**f,'height_above_floor':d,'point':list(q),'object':o.name,'component_seed':min(ids),'reason':'open_or_nonmanifold_candidate_component'})
   continue
  tree=BVHTree.FromPolygons(coords,faces,all_triangles=False,epsilon=0.0);distance=(Vector(c['bb'][1])-Vector(c['bb'][0])).length*2+10
  for j in c['picks']:
   f,d,q=points[j];location,normal,index,near=tree.find_nearest(q)
   if near is not None and near<.0005:
    uncertain.append({**f,'height_above_floor':d,'point':list(q),'object':o.name,'component_seed':min(ids),'reason':'within_boundary_tolerance'});continue
   votes=[parity(tree,q,direction,distance) for direction in dirs]
   record={**f,'height_above_floor':d,'point':list(q),'object':o.name,'component_seed':min(ids),'ray_crossings':[n for bit,n in votes]}
   bits=[bit for bit,n in votes]
   if any(bit is None for bit in bits) or len(set(bits))!=1:uncertain.append({**record,'reason':'ray_parity_disagreement_or_limit'})
   elif bits[0]==1:collisions.append(record)
 object_stats.append({'object':o.name,'evaluated_vertices':len(vs),'components':len(groups),'candidate_components':len(candidate),'modifiers_evaluated':[m.type for m in o.modifiers if m.show_viewport]});eo.to_mesh_clear()
r={'model':Path(bpy.data.filepath).name,'model_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'method':'separate evaluated connected components; strict closed-edge test; three agreeing oblique ray parities; evaluated-object AABB broadphase','synthetic_regressions':self_tests,'floor_samples':len(floors),'occupancy_points':len(points),'zones':dict(Counter(f['zone'] for f in floors)),'height_offsets':[.05,1.1,2.0],'collisions':collisions,'uncertain':uncertain,'known_open_surface_tests':surface_tests,'tested_components':tested_components,'objects':object_stats,'sampled_occupancy_clear':not collisions and not uncertain,'seconds':time.time()-start,'limits':'Known named open terrain/path sheets are surface-collision-tested and make no enclosed-volume claim. Unknown open candidates fail. Discrete samples only, not continuous-volume proof. Eastern walking endpoint x=-3.5 stops before intentionally closed doorway.'}
Path(a.report).write_text(json.dumps(r,indent=2));print(json.dumps({k:r[k] for k in('floor_samples','occupancy_points','sampled_occupancy_clear','seconds')}));print('COLLISION OBJECTS',dict(Counter(x['object'] for x in collisions)));print('UNCERTAIN OBJECTS',dict(Counter(x['object'] for x in uncertain)))
if not a.allow_collisions:assert r['sampled_occupancy_clear'],'Occupancy failed: inspect report collisions/uncertain'
