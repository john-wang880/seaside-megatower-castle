"""Independent actual-surface sampling: no builder profiles, no model saves.
Bounded sample evidence only, not an all-surface embedding or structural claim.
"""
import bpy,argparse,sys,json,hashlib
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser();p.add_argument('--report',required=True);p.add_argument('--baseline',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(bpy.data.filepath);canonical=Path(a.baseline);sha=hashlib.sha256(source.read_bytes()).hexdigest();canon=hashlib.sha256(canonical.read_bytes()).hexdigest();assert canon=='578ff47936800fe2a651237b609d95090cd97fefa686a208f8215d57628ac389'
dg=bpy.context.evaluated_depsgraph_get();before=(len(bpy.data.objects),len(bpy.data.meshes))
def geometry(name):
 o=bpy.data.objects[name];assert not o.hide_render and not o.hide_get();eo=o.evaluated_get(dg);me=eo.to_mesh();vs=[eo.matrix_world@v.co for v in me.vertices];fs=[list(f.vertices) for f in me.polygons]
 edges=Counter(tuple(sorted((f[i],f[(i+1)%len(f)]))) for f in fs for i in range(len(f)));assert all(n==2 for n in edges.values()),name+' not closed'
 me.calc_loop_triangles();tris=[tuple(t.vertices) for t in me.loop_triangles];tree=BVHTree.FromPolygons(vs,tris,all_triangles=True);bounds=[[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]];eo.to_mesh_clear();return tree,bounds,len(vs),len(fs)
core,bb,cv,cf=geometry('V016 | offshore terrain-following stair core');rock,rb,rv,rf=geometry('Western citadel_West_Sea stack basalt')
dirs=[Vector((1,.317,.173)).normalized(),Vector((.229,1,.419)).normalized(),Vector((.391,.271,1)).normalized()]
duplicate_events=[]
def count_crossing(index,hit,last_index,last_hit):
 # A straight ray intersects one planar triangle at most once. Only an
 # immediate repeat of the SAME triangle within 1mm is a numerical self-hit;
 # distinct triangles are never merged, however close their intersections.
 if index==last_index:
  return False if (hit-last_hit).length<.001 else None
 return True
def parity(point,direction):
 q=point.copy();n=0;last_index=None;last_hit=None
 for _ in range(128):
  hit,normal,index,distance=rock.ray_cast(q,direction,1000)
  if hit is None:return n%2,n
  decision=count_crossing(index,hit,last_index,last_hit)
  if decision is None:return None,n
  if decision:n+=1
  else:duplicate_events.append({'triangle':index,'repeat_hit_distance':distance,'same_triangle_hit_separation':(hit-last_hit).length})
  last_index=index;last_hit=hit.copy();q=hit+direction*.0001
 return None,n
controls={'same_triangle_near_restart_not_double_counted':count_crossing(66,Vector((.0001,0,0)),66,Vector((0,0,0))) is False,'distinct_nearby_triangle_still_counted':count_crossing(67,Vector((.0001,0,0)),66,Vector((0,0,0))) is True,'distant_same_triangle_repeat_uncertain':count_crossing(66,Vector((1,0,0)),66,Vector((0,0,0))) is None}
def synthetic_crossing_count(indices):
 count=0;last=None;last_hit=None
 for i,index in enumerate(indices):
  hit=Vector((i*.0001,0,0));decision=count_crossing(index,hit,last,last_hit)
  assert decision is not None
  count+=int(decision);last=index;last_hit=hit
 return count
controls['repeated_same_triangle_sequence_counts_one']=synthetic_crossing_count([66,66])==1
controls['distinct_near_triangle_sequence_counts_two']=synthetic_crossing_count([66,67])==2
controls['observed_duplicate_then_two_real_crossings_counts_three']=synthetic_crossing_count([66,66,68,70])==3
assert all(controls.values())
samples=[];fail=[];negative=[];missing=[];nx,ny=41,147;boundary_margin=.001
# Slightly inset endpoints avoid degenerate side/bottom edges; actual lowest
# upward ray hit is used, not a builder height formula or vertical rock interval.
for i in range(nx):
 x=bb[0][0]+.001+(bb[1][0]-bb[0][0]-.002)*i/(nx-1)
 for j in range(ny):
  y=bb[0][1]+.001+(bb[1][1]-bb[0][1]-.002)*j/(ny-1)
  q,normal,index,distance=core.ray_cast(Vector((x,y,bb[0][2]-10)),Vector((0,0,1)),bb[1][2]-bb[0][2]+20)
  if q is None:missing.append([x,y]);continue
  nearest,nn,ni,dist=rock.find_nearest(q);results=[parity(q,d) for d in dirs];bits=[b for b,n in results]
  row={'point':list(q),'core_face':index,'rock_parities':bits,'rock_crossing_counts':[n for b,n in results],'nearest_rock_surface_distance':dist,'pass':bits==[1,1,1] and dist is not None and dist>boundary_margin}
  samples.append(row)
  if not row['pass']:fail.append(row)
  # Synthetic vertically lifted underside points; actual model untouched.
  if i%4==0 and j%7==0:
   lifted=q+Vector((0,0,.5));neg=[parity(lifted,d)[0] for d in dirs];negative.append({'point':list(lifted),'parities':neg,'rejected':neg!=[1,1,1]})
r={'source_sha256':sha,'canonical_v015_sha256':canon,'candidate_unchanged':sha==hashlib.sha256(source.read_bytes()).hexdigest(),'canonical_unchanged':canon==hashlib.sha256(canonical.read_bytes()).hexdigest(),'temporary_datablocks_cleaned':before==(len(bpy.data.objects),len(bpy.data.meshes)),'parity_restart_controls':controls,'numerical_same_triangle_duplicate_events':duplicate_events,'grid':[nx,ny],'sample_count':len(samples),'endpoint_inset':.001,'required_nearest_boundary_margin':boundary_margin,'minimum_nearest_rock_surface_distance':min(s['nearest_rock_surface_distance'] for s in samples),'rock_closed_edge_incidence_verified':True,'core_closed_edge_incidence_verified':True,'core_vertices_faces':[cv,cf],'rock_vertices_faces':[rv,rf],'missing_core_surface_hits':missing,'failures':fail,'samples':samples,'lifted_underside_negative_control':{'translation_z':.5,'sample_count':len(negative),'rejected_count':sum(s['rejected'] for s in negative),'examples':[s for s in negative if s['rejected']][:10]},'scope':'Actual evaluated core underside BVH hits sampled on 41x147 slightly inset grid; each checked against actual closed evaluated basalt by three non-axis ray parities plus Euclidean nearest-surface margin. No source bounding-box/vertical-interval occupancy inference, no builder profile reused. Bounded sampling, not proof for every surface point or structural capacity.'}
r['pass']=len(samples)==nx*ny and not missing and not fail and r['lifted_underside_negative_control']['rejected_count']>0 and r['candidate_unchanged'] and r['canonical_unchanged'] and r['temporary_datablocks_cleaned']
Path(a.report).write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ('samples','failures')},indent=2));assert r['pass'],'Inspect grounding failures'
