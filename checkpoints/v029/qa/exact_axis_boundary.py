"""Exact-rational saved-float boundary comparison for independently expected axis-cell solids.
Float32 vertices are dyadic rationals; all clipping and area accounting below is exact.
This does NOT assert nominal decimal plans equal quantized saved geometry.
"""
from fractions import Fraction as F
from collections import defaultdict
import itertools

def area(poly):return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))/2) if len(poly)>2 else F(0)
def signed_area(poly):return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))/2
def clip_rect(poly,lo,hi):
 out=poly
 for axis,bound,sign in [(0,lo[0],1),(0,hi[0],-1),(1,lo[1],1),(1,hi[1],-1)]:
  new=[]
  for i,a in enumerate(out):
   b=out[(i+1)%len(out)];da=sign*(a[axis]-bound);db=sign*(b[axis]-bound)
   if da>=0:new.append(a)
   if (da>=0)!=(db>=0):new.append(tuple(a[k]+(b[k]-a[k])*da/(da-db) for k in range(2)))
  out=new
  if not out:break
 return out

def clip_convex(a,b):
 out=a;sign=1 if signed_area(b)>0 else -1
 for i,p in enumerate(b):
  q=b[(i+1)%len(b)];new=[]
  for j,u in enumerate(out):
   v=out[(j+1)%len(out)];du=sign*((q[0]-p[0])*(u[1]-p[1])-(q[1]-p[1])*(u[0]-p[0]));dv=sign*((q[0]-p[0])*(v[1]-p[1])-(q[1]-p[1])*(v[0]-p[0]))
   if du>=0:new.append(u)
   if (du>=0)!=(dv>=0):new.append(tuple(u[k]+(v[k]-u[k])*du/(du-dv) for k in range(2)))
  out=new
  if not out:break
 return out

def bounds(poly):return (tuple(min(p[k] for p in poly) for k in range(2)),tuple(max(p[k] for p in poly) for k in range(2)))
def positive_bbox(a,b):return all(min(a[1][k],b[1][k])>max(a[0][k],b[0][k]) for k in range(2))
def fraction3(p):return tuple(F(float(v)) for v in p)
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def facets_from_cells(coords,occupied):
 refs=defaultdict(list);volume=F(0);coords=[[F(float(v)) for v in row] for row in coords]
 for idx in occupied:
  lo=[coords[k][idx[k]] for k in range(3)];hi=[coords[k][idx[k]+1] for k in range(3)];volume+=(hi[0]-lo[0])*(hi[1]-lo[1])*(hi[2]-lo[2])
  for axis in range(3):
   for sign in [-1,1]:
    neighbor=list(idx);neighbor[axis]+=sign
    if tuple(neighbor) in occupied:continue
    other=[k for k in range(3) if k!=axis];key=(axis,lo[axis] if sign<0 else hi[axis],sign);refs[key].append((tuple(lo[k] for k in other),tuple(hi[k] for k in other)))
 return dict(refs),volume

def validate(vertices,triangles,reference):
 refs,expected_volume=reference;v=[fraction3(p) for p in vertices];groups=defaultdict(list);signed_volume=F(0);origin=v[0];zero=[]
 for ti,ids in enumerate(triangles):
  p=[v[i] for i in ids];e=tuple(p[1][k]-p[0][k] for k in range(3));f=tuple(p[2][k]-p[0][k] for k in range(3));n=cross(e,f)
  if not any(n):zero.append(ti);continue
  axes=[k for k in range(3) if all(q[k]==p[0][k] for q in p)]
  if len(axes)!=1:raise ValueError(('Non-axis local boundary triangle',ti))
  axis=axes[0];key=(axis,p[0][axis],1 if n[axis]>0 else -1)
  if key not in refs:raise ValueError(('Unexpected boundary plane/orientation',ti,key))
  poly=[tuple(q[k] for k in range(3) if k!=axis) for q in p];bbox=bounds(poly);a=area(poly)
  covered=sum((area(clip_rect(poly,lo,hi)) for lo,hi in refs[key] if positive_bbox(bbox,(lo,hi))),F(0))
  if covered!=a:raise ValueError(('Triangle outside expected boundary',ti,str(a-covered)))
  groups[key].append((ti,poly,bbox,a))
  rel=[tuple(q[k]-origin[k] for k in range(3)) for q in p];c=cross(rel[1],rel[2]);signed_volume+=sum(rel[0][k]*c[k] for k in range(3))/6
 # Zero triangles are not silently accepted: caller must provide parent polygon proof first.
 if zero:raise ValueError(('Exact-zero derived triangles require separate parent proof',zero))
 for key,rects in refs.items():
  rows=groups.get(key,[])
  for i,(ti,a,ab,aa) in enumerate(rows):
   for tj,b,bb,ba in rows[i+1:]:
    if positive_bbox(ab,bb) and area(clip_convex(a,b))>0:raise ValueError(('Multiply covered actual boundary',ti,tj))
  expected=sum(((hi[0]-lo[0])*(hi[1]-lo[1]) for lo,hi in rects),F(0));actual=sum((row[3] for row in rows),F(0))
  if actual!=expected:raise ValueError(('Uncovered expected boundary',key,str(expected-actual)))
 if expected_volume is not None and signed_volume!=expected_volume:raise ValueError(('Exact rational volume mismatch',str(signed_volume),str(expected_volume)))
 result={'pass':True,'triangles':len(triangles),'axis_oriented_planes':len(refs),'uncovered_area':0,'outside_area':0,'multiply_covered_area':0,'saved_float_volume_exact_fraction':str(signed_volume),'saved_float_volume':float(signed_volume),'method':'Exact Fraction clipping/areas on saved-float coordinates, independently quantized expected cells; no geometry-area tolerance.'}
 if expected_volume is None:
  result['partial_surface_signed_tetrahedral_sum_exact_fraction']=result.pop('saved_float_volume_exact_fraction');result['partial_surface_signed_tetrahedral_sum']=result.pop('saved_float_volume');result['volume_note']='Partial-domain flux contribution only; not a closed solid volume.'
 return result
