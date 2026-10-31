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
start=time.time();floors=[];floor_checks=[];prisms=[]
visible=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and not o.name.startswith(('Volume cloud','Air perspective'))]
deps=bpy.context.evaluated_depsgraph_get()
def floor(x,y,expected,label):
 hits=[]
 for o in visible:
  eo=o.evaluated_get(deps);inv=eo.matrix_world.inverted();h,v,n,i=eo.ray_cast(inv@Vector((x,y,expected+.08)),(inv.to_3x3()@Vector((0,0,-1))).normalized(),distance=.16)
  if h:hits.append(((eo.matrix_world@v).z,o.name))
 if hits:
  z,name=max(hits);valid=abs(z-expected)<.003
 else:z=expected;name=None;valid=False
 floor_checks.append({'zone':label,'x':x,'y':y,'expected_z':expected,'actual_z':z,'support_object':name,'valid':valid})
 floors.append({'zone':label,'x':x,'y':y,'z':z})
def prism(label,x0,x1,y0,y1,z):prisms.append({'zone':label,'bounds':[[x0,y0,z+.025],[x1,y1,z+2.1]],'floor_z':z})
for i in range(33):
 x=-3.5+i*7.95/32
 for y in(37.4,38,38.6):floor(x,y,29,'entrance_hall')
prism('entrance_hall',-3.5,4.45,37.4,38.6,29)
prism('turning_elbow',3.85,5.05,37.4,38.6,29)
for x in(3.85,4.45,5.05):
 for y in(37.4,38,38.6):floor(x,y,29,'turning_elbow')
for i in range(31):
 y=38+i*7.5/30
 for x in(3.85,4.45,5.05):floor(x,y,29 if y<45.5 else 29+.18125,'north_corridor')
prism('north_corridor',3.85,5.05,38,45.5,29)
for step in range(20):
 z=29+(step+1)*.18125;y0=45.5+step*.6
 for d in(.03,.3,.57):
  for x in(3.85,4.45,5.05):floor(x,y0+d,z,'north_stairs')
 prism('north_stair_'+str(step+1),3.85,5.05,y0,y0+.6,z)
for i in range(81):
 y=57.5+i*.025
 for x in(3.85,4.45,5.05):floor(x,y,32.625,'covered_terrace_landing')
prism('covered_terrace_landing',3.85,5.05,57.5,59.5,32.625)
points=[(f,delta,Vector((f['x'],f['y'],f['z']+delta))) for f in floors for delta in(.05,1.1,2.0)]
lo=[min(p['bounds'][0][k] for p in prisms) for k in range(3)];hi=[max(p['bounds'][1][k] for p in prisms) for k in range(3)]
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
# Full prism/surface intersection using the 13 separating-axis tests for
# every evaluated triangle: 3 box axes, triangle normal, 9 edge cross axes.
# With no boundary surface in the prism interior, 3-ray center containment
# resolves the remaining closed-solid containment case. No sampling substitutes
# for surface intersection in this test. Contact-only triangles are separate.
envelope_collisions=[];envelope_uncertain=[];boundary_contacts=[];envelope_component_checks=0
axes=[Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))]
def bb_overlap(a,b,eps=0):return all(a[1][k]>=b[0][k]-eps and a[0][k]<=b[1][k]+eps for k in range(3))
def triangle_box(tri,bb):
 center=(Vector(bb[0])+Vector(bb[1]))*.5;half=(Vector(bb[1])-Vector(bb[0]))*.5
 v=[q-center for q in tri];edges=[v[1]-v[0],v[2]-v[1],v[0]-v[2]]
 tests=axes+[edges[0].cross(edges[1])]+[e.cross(ax) for e in edges for ax in axes]
 contact=False
 for ax in tests:
  length=ax.length
  if length<1e-10:continue
  ax=ax/length;projection=[q.dot(ax) for q in v];low=min(projection);high=max(projection);r=sum(half[k]*abs(ax[k]) for k in range(3));eps=2e-5
  if low>r+eps or high< -r-eps:return 'none'
  if low>=r-eps or high<= -r+eps:contact=True
 return 'contact' if contact else 'interior'
def clip_contact(poly,axis,value,greater):
 if not poly:return []
 result=[]
 for u,v in zip(poly,poly[1:]+poly[:1]):
  du=(u[axis]-value)*(1 if greater else -1);dv=(v[axis]-value)*(1 if greater else -1)
  iu=du>=-1e-12;iv=dv>=-1e-12
  if iu:result.append(u)
  if iu!=iv:
   fraction=du/(du-dv);result.append(tuple(u[k]+fraction*(v[k]-u[k]) for k in range(3)))
 return result
successors={prisms[i]['zone']:prisms[i+1] for i in range(len(prisms)-1)}
def expected_step_contact(tri,pr,object_name):
 # The old object-name+zone exception could accept an arbitrary tall curtain
 # on a shared prism face. Accept ONLY clipped contact at the next known riser
 # plane, within its actual intended floor-to-floor height band.
 eps=2e-5;next_pr=successors.get(pr['zone']);reason=None
 if object_name!='V012 | twenty north stair treads':reason='not_stair_body'
 elif not (pr['zone']=='north_corridor' or pr['zone'].startswith('north_stair_')):reason='not_before_expected_riser'
 elif next_pr is None or abs(next_pr['floor_z']-pr['floor_z']-.18125)>eps:reason='no_expected_next_rise'
 elif abs(pr['bounds'][1][1]-next_pr['bounds'][0][1])>eps:reason='next_prism_plane_mismatch'
 poly=[tuple(v) for v in tri]
 for k in range(3):
  poly=clip_contact(poly,k,pr['bounds'][0][k]-eps,True)
  poly=clip_contact(poly,k,pr['bounds'][1][k]+eps,False)
 if not poly and reason is None:reason='no_geometric_contact'
 if reason is None:
  if not all(abs(v[1]-pr['bounds'][1][1])<=3*eps for v in poly):reason='contact_not_on_next_riser_plane'
  elif not all(pr['floor_z']-3*eps<=v[2]<=next_pr['floor_z']+3*eps for v in poly):reason='contact_outside_expected_riser_height_band'
 return {'accepted':reason is None,'reason':reason,'clipped_contact_vertices':[list(v) for v in poly],'expected_plane_y':pr['bounds'][1][1],'expected_height_band':[pr['floor_z'],next_pr['floor_z']] if next_pr else None}

# Positive controls for a triangle crossing, touching, and missing an AABB.
box_test=[[0,0,0],[1,1,1]]
self_tests['triangle_box_crossing']=triangle_box([Vector(q) for q in[(-1,.5,.5),(2,.5,.5),(.5,2,.5)]],box_test)=='interior'
self_tests['triangle_box_contact']=triangle_box([Vector(q) for q in[(0,0,1),(1,0,1),(0,1,1)]],box_test)=='contact'
self_tests['triangle_box_separated']=triangle_box([Vector(q) for q in[(0,0,2),(1,0,2),(0,1,2)]],box_test)=='none'
tiny=[Vector((.7+.1*x,.2+.1*y,.2+.1*z)) for x,y,z in unit_vertices]
tiny_tree=BVHTree.FromPolygons(tiny,unit_faces,all_triangles=False)
self_tests['off_center_obstacle_not_missed_by_center_sampling']=all(parity(tiny_tree,Vector((.5,.5,.5)),d,10)[0]==0 for d in dirs) and any(triangle_box([tiny[f[0]],tiny[f[1]],tiny[f[2]]],box_test)=='interior' for f in unit_faces)
large=[Vector((-1+3*x,-1+3*y,-1+3*z)) for x,y,z in unit_vertices]
large_tree=BVHTree.FromPolygons(large,unit_faces,all_triangles=False)
self_tests['fully_enclosed_prism_detected_by_containment']=all(triangle_box([large[f[0]],large[f[1]],large[f[2]]],box_test)=='none' for f in unit_faces) and all(parity(large_tree,Vector((.5,.5,.5)),d,10)[0]==1 for d in dirs)
# Positive controls specifically for the formerly broad step exception.
control=prisms[2];name='V012 | twenty north stair treads'
expected=[Vector(q) for q in[(3.85,45.5,29.05),(5.05,45.5,29.05),(4.45,45.5,29.18125)]]
tall=[Vector(q) for q in[(3.85,45.5,30),(5.05,45.5,30),(4.45,45.5,31)]]
intruding=[Vector((v.x,v.y-.01,v.z)) for v in tall]
wrong_side=[Vector(q) for q in[(3.85,44.5,29.05),(3.85,45,29.05),(3.85,44.75,29.15)]]
self_tests['expected_riser_contact_accepted']=triangle_box(expected,control['bounds'])=='contact' and expected_step_contact(expected,control,name)['accepted']
self_tests['tall_named_stair_boundary_curtain_rejected']=triangle_box(tall,control['bounds'])=='contact' and not expected_step_contact(tall,control,name)['accepted']
self_tests['named_stair_body_intrusion_is_interior_collision']=triangle_box(intruding,control['bounds'])=='interior'
self_tests['wrong_side_stair_contact_rejected']=triangle_box(wrong_side,control['bounds'])=='contact' and not expected_step_contact(wrong_side,control,name)['accepted']
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
  boxes=[j for j,p in enumerate(prisms) if bb_overlap(bb,p['bounds'])]
  if picks or boxes:candidate[seed]={'ids':ids,'bb':bb,'picks':picks,'faces':[],'prisms':boxes,'triangles':[]}
 for f in me.polygons:
  seed=find(f.vertices[0])
  if seed in candidate:candidate[seed]['faces'].append(tuple(f.vertices))
 me.calc_loop_triangles()
 for tri in me.loop_triangles:
  seed=find(tri.vertices[0])
  if seed in candidate:candidate[seed]['triangles'].append(tuple(tri.vertices))
 for seed,c in candidate.items():
  ids=c['ids'];mapping={old:new for new,old in enumerate(ids)};faces=[tuple(mapping[i] for i in f) for f in c['faces']];coords=[vs[i] for i in ids]
  edge_counts=Counter(tuple(sorted((f[i],f[(i+1)%len(f)]))) for f in faces for i in range(len(f)))
  closed=bool(faces) and all(n==2 for n in edge_counts.values());detail={'object':o.name,'component_seed':min(ids),'vertices':len(ids),'polygons':len(faces),'closed_two_faces_per_edge':closed,'bounds':c['bb']}
  tested_components.append(detail)
  triangle_data=[]
  for ids_tri in c['triangles']:
   tri=[vs[i] for i in ids_tri];bounds=([min(v[k] for v in tri) for k in range(3)],[max(v[k] for v in tri) for k in range(3)])
   triangle_data.append((tri,bounds))
  envelope_tree=None
  for pj in c['prisms']:
   pr=prisms[pj];pb=pr['bounds'];envelope_component_checks+=1;crossing=[];touching=[]
   for ti,(tri,tbb) in enumerate(triangle_data):
    if not bb_overlap(tbb,pb,2e-5):continue
    status=triangle_box(tri,pb)
    if status=='interior':crossing.append(ti)
    elif status=='contact':touching.append(ti)
   rec={'prism':pj,'zone':pr['zone'],'object':o.name,'component_seed':min(ids),'bounds':pb,'triangle_interior_intersections':len(crossing),'triangle_boundary_contacts':len(touching)}
   if not closed and o.name not in known_open_surfaces:
    envelope_uncertain.append({**rec,'reason':'unknown_open_component'});continue
   if crossing:
    envelope_collisions.append({**rec,'reason':'surface_intersects_prism_interior','first_triangle_world':[list(v) for v in triangle_data[crossing[0]][0]]});continue
   if touching:
    contact_geometry=[expected_step_contact(triangle_data[ti][0],pr,o.name) for ti in touching]
    intentional=all(q['accepted'] for q in contact_geometry)
    boundary_contacts.append({**rec,'intentional_step_boundary':intentional,'geometric_contact_classification':contact_geometry})
    if not intentional:envelope_uncertain.append({**rec,'reason':'boundary_contact_not_expected_riser_geometry','geometric_contact_classification':contact_geometry})
   if closed:
    if envelope_tree is None:envelope_tree=BVHTree.FromPolygons(coords,faces,all_triangles=False,epsilon=0.0)
    center=(Vector(pb[0])+Vector(pb[1]))*.5;distance=(Vector(c['bb'][1])-Vector(c['bb'][0])).length*2+10
    votes=[parity(envelope_tree,center,d,distance)[0] for d in dirs]
    if any(q is None for q in votes) or len(set(votes))!=1:envelope_uncertain.append({**rec,'reason':'prism_center_parity_ambiguous','votes':votes})
    elif votes[0]:envelope_collisions.append({**rec,'reason':'prism_inside_closed_component','votes':votes})
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
r={'model':Path(bpy.data.filepath).name,'model_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'method':'separate evaluated connected components; strict closed-edge test; three agreeing oblique ray parities; evaluated-object AABB broadphase','synthetic_regressions':self_tests,'continuous_envelope':{'step_contact_rule':'Expected next-riser plane AND intended floor-to-next-floor band; object name alone is insufficient.','triangle_sat_tolerance':.00002,'width':1.2,'vertical_offsets':[.025,2.1],'prisms':prisms,'component_prism_checks':envelope_component_checks,'collisions':envelope_collisions,'uncertain':envelope_uncertain,'boundary_contacts':boundary_contacts,'clear':not envelope_collisions and not envelope_uncertain,'scope':'Central stair-following axis-aligned clearance prisms including explicit turn square; evaluated triangulated surfaces and component containment. Not dynamic-human or full navigation certification.'},'floor_contact_checks':floor_checks,'floor_contact_pass':all(q['valid'] for q in floor_checks),'floor_samples':len(floors),'occupancy_points':len(points),'zones':dict(Counter(f['zone'] for f in floors)),'height_offsets':[.05,1.1,2.0],'collisions':collisions,'uncertain':uncertain,'known_open_surface_tests':surface_tests,'tested_components':tested_components,'objects':object_stats,'sampled_occupancy_clear':not collisions and not uncertain and all(q['valid'] for q in floor_checks),'seconds':time.time()-start,'limits':'Known named open terrain/path sheets are surface-collision-tested and make no enclosed-volume claim. Unknown open candidates fail. Discrete samples only, not continuous-volume proof. v012 L-route to existing covered terrace; not an open-sky courtyard or dynamic navigation certification.'}
r['route_acceptance_pass']=r['sampled_occupancy_clear'] and r['continuous_envelope']['clear'] and r['floor_contact_pass']
Path(a.report).write_text(json.dumps(r,indent=2));print(json.dumps({k:r[k] for k in('floor_samples','occupancy_points','sampled_occupancy_clear','route_acceptance_pass','seconds')}));print('COLLISION OBJECTS',dict(Counter(x['object'] for x in collisions)));print('UNCERTAIN OBJECTS',dict(Counter(x['object'] for x in uncertain)))
if not a.allow_collisions:assert r['sampled_occupancy_clear'] and r['continuous_envelope']['clear'],'Occupancy failed: inspect report collisions/uncertain'
