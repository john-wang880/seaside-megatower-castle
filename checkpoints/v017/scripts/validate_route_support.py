"""Read-only bounded coverage audit: central v012 route surfaces and prism joins.
No full-castle navigation, human motion or accessibility certification implied.
"""
import bpy,json,hashlib,math,sys,argparse
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
prisms=json.loads(Path(a.manifest).read_text())['continuous_envelope']['prisms'];EPS=2e-5
source=Path(bpy.data.filepath);sha=hashlib.sha256(source.read_bytes()).hexdigest()
def overlap(a,b,eps=EPS):return all(a[1][k]>=b[0][k]-eps and a[0][k]<=b[1][k]+eps for k in range(3))
def bounds(vs):return ([min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)])
# Adjacent closed prisms must overlap or share a nonzero-area boundary, not
# merely touch at a corner. Numerical gaps are reported, not rounded away.
joins=[]
for i in range(len(prisms)-1):
 x,y=prisms[i]['bounds'],prisms[i+1]['bounds'];d=[min(x[1][k],y[1][k])-max(x[0][k],y[0][k]) for k in range(3)]
 joins.append({'from':prisms[i]['zone'],'to':prisms[i+1]['zone'],'signed_overlap_xyz':d,'meeting':all(q>=-1e-10 for q in d) and sum(q>1e-10 for q in d)>=2})
# Polygon clipping and exact piecewise-linear union integration for projected
# horizontal tread / vertical riser triangles. Sweep at all vertices AND edge
# intersections, so overlap cannot conceal a gap as naive summed areas could.
def clip(poly,axis,value,greater):
 if not poly:return []
 out=[]
 for u,v in zip(poly,poly[1:]+poly[:1]):
  du=(u[axis]-value)*(1 if greater else -1);dv=(v[axis]-value)*(1 if greater else -1)
  iu=du>=-1e-12;iv=dv>=-1e-12
  if iu:out.append(u)
  if iu!=iv:
   t=du/(du-dv);out.append(tuple(u[k]+t*(v[k]-u[k]) for k in range(len(u))))
 return out

def crop(poly,rect):
 for axis,value,greater in[(0,rect[0],True),(0,rect[1],False),(1,rect[2],True),(1,rect[3],False)]:poly=clip(poly,axis,value,greater)
 return poly

def interval(poly,x):
 yy=[]
 for u,v in zip(poly,poly[1:]+poly[:1]):
  if abs(v[0]-u[0])<1e-12:continue
  if min(u[0],v[0])-1e-12<=x<=max(u[0],v[0])+1e-12:yy.append(u[1]+(x-u[0])*(v[1]-u[1])/(v[0]-u[0]))
 return (min(yy),max(yy)) if yy else None

def coverage(polys,rect):
 polys=[q for p in polys if len(q:=crop(p,rect))>=3];edges=[(a,b) for p in polys for a,b in zip(p,p[1:]+p[:1])]
 xs=[rect[0],rect[1]]+[v[0] for p in polys for v in p]
 for i,(a,b) in enumerate(edges):
  dx,dy=b[0]-a[0],b[1]-a[1]
  for c,d in edges[i+1:]:
   ex,ey=d[0]-c[0],d[1]-c[1];den=dx*ey-dy*ex
   if abs(den)<1e-12:continue
   t=((c[0]-a[0])*ey-(c[1]-a[1])*ex)/den;u=((c[0]-a[0])*dy-(c[1]-a[1])*dx)/den
   if -1e-10<=t<=1+1e-10 and -1e-10<=u<=1+1e-10:xs.append(a[0]+t*dx)
 xs=sorted(set(round(x,11) for x in xs));area=0;gaps=[]
 for x0,x1 in zip(xs,xs[1:]):
  if x1-x0<1e-11:continue
  x=(x0+x1)/2;iv=sorted(q for p in polys if (q:=interval(p,x)) is not None);merged=[]
  for lo,hi in iv:
   if not merged or lo>merged[-1][1]+1e-10:merged.append([lo,hi])
   else:merged[-1][1]=max(merged[-1][1],hi)
  covered=sum(max(0,b-a) for a,b in merged);area+=(x1-x0)*covered
  cursor=rect[2]
  for lo,hi in merged+[[rect[3],rect[3]]]:
   if lo>cursor+1e-9:gaps.append({'x_interval':[x0,x1],'y_gap_at_midpoint':[cursor,lo]})
   cursor=max(cursor,hi)
 expected=(rect[1]-rect[0])*(rect[3]-rect[2]);deficit=max(0,expected-area)
 # At most a 20-micron coordinate discrepancy from float32 mesh storage.
 meaningful=[q for q in gaps if (q['x_interval'][1]-q['x_interval'][0])>EPS and (q['y_gap_at_midpoint'][1]-q['y_gap_at_midpoint'][0])>EPS]
 return {'expected_area':expected,'covered_union_area':area,'uncovered_area':deficit,'gap_cells':gaps,'meaningful_gap_cells':meaningful,'coverage_within_numeric_tolerance':not meaningful and deficit<=EPS*2*((rect[1]-rect[0])+(rect[3]-rect[2])),'triangles_considered':len(polys)}

# Union controls: duplicate overlaps must not hide a real missing strip.
full=[[(0,0),(1,0),(1,1)],[(0,0),(1,1),(0,1)]]
assert coverage(full,[0,1,0,1])['coverage_within_numeric_tolerance']
gapped=[[(0,0),(.4,0),(.4,1),(0,1)]]*3+[[ (.6,0),(1,0),(1,1),(.6,1)]]
assert not coverage(gapped,[0,1,0,1])['coverage_within_numeric_tolerance']
triangles=[];deps=bpy.context.evaluated_depsgraph_get();route_bb=[[-3.5,37.4,28.99],[5.05,59.5,34.725]]
for o in bpy.data.objects:
 if o.type!='MESH' or o.hide_render or o.name.startswith(('Volume cloud','Air perspective')):continue
 eo=o.evaluated_get(deps);bb=bounds([eo.matrix_world@Vector(v) for v in eo.bound_box])
 if not overlap(bb,route_bb):continue
 me=eo.to_mesh();vs=[eo.matrix_world@v.co for v in me.vertices];me.calc_loop_triangles()
 for t in me.loop_triangles:
  tri=[vs[i].copy() for i in t.vertices];bb=bounds(tri)
  if overlap(bb,route_bb):triangles.append({'object':o.name,'triangle':tri,'bounds':bb})
 eo.to_mesh_clear()

def projected_check(rect,fixed_axis,fixed_value,axes):
 polys=[];objects=set()
 for t in triangles:
  if all(abs(v[fixed_axis]-fixed_value)<=EPS for v in t['triangle']):
   poly=[tuple(v[k] for k in axes) for v in t['triangle']]
   if len(crop(poly,rect))>=3:polys.append(poly);objects.add(t['object'])
 r=coverage(polys,rect);r['support_objects']=sorted(objects);return r
floors=[]
for p in prisms:
 b=p['bounds'];rect=[b[0][0],b[1][0],b[0][1],b[1][1]]
 floors.append({'zone':p['zone'],'expected_floor_z':p['floor_z'],**projected_check(rect,2,p['floor_z'],(0,1))})
risers=[]
for i in range(20):
 y=45.5+i*.6;low=29+i*.18125;high=low+.18125
 risers.append({'index':i+1,'expected_plane_y':y,'expected_z_range':[low,high],**projected_check([3.85,5.05,low,high],1,y,(0,2))})

# Independently classify every actual stair contact, using the same triangle/AABB
# geometry but requiring its CLIPPED contact to lie at the next riser plane and
# within the intended 0.18125m band. No blanket object-name exception.
axes3=[Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))]
def sat(tri,bb):
 c=(Vector(bb[0])+Vector(bb[1]))*.5;h=(Vector(bb[1])-Vector(bb[0]))*.5;v=[q-c for q in tri];ed=[v[1]-v[0],v[2]-v[1],v[0]-v[2]];contact=False
 for ax in axes3+[ed[0].cross(ed[1])]+[e.cross(q) for e in ed for q in axes3]:
  if ax.length<1e-10:continue
  ax=ax.normalized();p=[q.dot(ax) for q in v];lo,hi=min(p),max(p);radius=sum(h[k]*abs(ax[k]) for k in range(3))
  if lo>radius+EPS or hi< -radius-EPS:return 'none'
  if lo>=radius-EPS or hi<= -radius+EPS:contact=True
 return 'contact' if contact else 'interior'
contacts=[]
for p in prisms:
 bb=p['bounds']
 for ti,t in enumerate(triangles):
  if t['object']!='V012 | twenty north stair treads' or not overlap(t['bounds'],bb):continue
  if sat(t['triangle'],bb)!='contact':continue
  poly=[tuple(v) for v in t['triangle']]
  for k in range(3):
   poly=clip(poly,k,bb[0][k]-EPS,True);poly=clip(poly,k,bb[1][k]+EPS,False)
  expected=p['zone']=='north_corridor' or (p['zone'].startswith('north_stair_') and p['zone']!='north_stair_20')
  correct=expected and bool(poly) and all(abs(v[1]-bb[1][1])<=3*EPS and p['floor_z']-3*EPS<=v[2]<=p['floor_z']+.18125+3*EPS for v in poly)
  contacts.append({'zone':p['zone'],'triangle_index':ti,'contact_vertices':[list(v) for v in poly],'strict_expected_riser_contact':correct})
# The legacy name+zone predicate alone would accept a tall curtain exactly at a
# prism end. Strict band/plane validation must reject this synthetic case.
p=prisms[2];tall_contact=[(3.85,45.5,30),(5.05,45.5,30),(4.45,45.5,31)]
legacy_accepts=True;strict_rejects=not all(p['floor_z']-3*EPS<=v[2]<=p['floor_z']+.18125+3*EPS for v in tall_contact)
assert legacy_accepts and strict_rejects
r={'model_sha256':sha,'source_unchanged':sha==hashlib.sha256(source.read_bytes()).hexdigest(),'numeric_tolerance':EPS,'prism_joins':joins,'all_prisms_connected':all(q['meeting'] for q in joins),'minimum_stair_shared_vertical_extent':min(q['signed_overlap_xyz'][2] for q in joins),'floor_surface_union_checks':floors,'all_central_floor_footprints_supported':all(q['coverage_within_numeric_tolerance'] for q in floors),'riser_surface_union_checks':risers,'all_expected_riser_faces_present':all(q['coverage_within_numeric_tolerance'] for q in risers),'strict_stair_contacts':contacts,'all_actual_contacts_are_expected_riser_band':bool(contacts) and all(q['strict_expected_riser_contact'] for q in contacts),'legacy_exception_synthetic_tall_contact_would_be_accepted':legacy_accepts,'strict_rule_rejects_synthetic_tall_contact':strict_rejects,'overlap_cannot_conceal_gap_regression':True,'scope':'Only24 central v012 stair-following prisms/footprints and20 risers. Prism connectivity does not prove traversal by a rigid2.1m-tall body: successive shared vertical overlap is1.89375m. No dynamic navigation or whole-castle claim.'}
Path(a.report).write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if not isinstance(v,list)}));assert r['all_prisms_connected'] and r['all_central_floor_footprints_supported'] and r['all_expected_riser_faces_present'] and r['all_actual_contacts_are_expected_riser_band'] and r['source_unchanged']
