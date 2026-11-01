"""Independent convex-solid union boundary construction; no Blender/Boolean dependency.
Clips original convex boundary polygons against every other input solid. Shared
same-facing planes are assigned to one owner. Comparison consumes saved triangles.
"""
import math,itertools,sys
if sys.flags.optimize:raise RuntimeError("Optimized Python unsupported")

def add(a,b):return tuple(x+y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def mul(a,s):return tuple(x*s for x in a)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def norm(a):return math.sqrt(dot(a,a))
def plane(p):
 n=cross(sub(p[1],p[0]),sub(p[2],p[0]));n=mul(n,1/norm(n));return n,dot(n,p[0])
def area(p):
 if len(p)<3:return 0.
 return norm(tuple(sum(cross(p[i],p[(i+1)%len(p)])[k]for i in range(len(p)))for k in range(3)))/2

def clip(p,n,d,inside=True):
 """Closed halfspace clipping, only machine-scale degeneracy cleanup."""
 if not p:return []
 out=[]
 for a,b in zip(p,p[1:]+p[:1]):
  da=dot(n,a)-d;db=dot(n,b)-d
  if not inside:da=-da;db=-db
  if da<=0:out.append(a)
  if (da<0<db)or(db<0<da):out.append(add(a,mul(sub(b,a),da/(da-db))))
 cleaned=[]
 for x in out:
  if not cleaned or norm(sub(x,cleaned[-1]))>1e-11:cleaned.append(x)
 if len(cleaned)>1 and norm(sub(cleaned[0],cleaned[-1]))<1e-11:cleaned.pop()
 return cleaned if len(cleaned)>=3 and area(cleaned)>1e-12 else []

def subtract_convex(p,planes):
 """Disjoint convex pieces of polygon minus convex solid; no union-area sum."""
 inside=p;outside=[]
 for n,d in planes:
  if not inside:break
  # A polygon lying in this plane belongs to the closed interior.
  ds=[dot(n,v)-d for v in inside]
  if max(abs(x)for x in ds)<1e-10:continue
  q=clip(inside,n,d,False)
  if q:outside.append(q)
  inside=clip(inside,n,d,True)
 return outside

def union_boundary(solids):
 planes=[[plane(f)for f in s]for s in solids];out=[]
 for i,s in enumerate(solids):
  for fi,f in enumerate(s):
   n,d=plane(f);pieces=[f]
   for j,ps in enumerate(planes):
    if i==j:continue
    # Equal outward support plane: lower original index owns overlap.
    same=any(dot(n,m)>1-1e-10 and max(abs(dot(m,v)-e)for v in f)<1e-9 for m,e in ps)
    if same and j>i:continue
    pieces=[q for p in pieces for q in subtract_convex(p,ps)]
   out.extend({'solid':i,'face':fi,'polygon':p,'normal':n}for p in pieces)
 return out

def volume(boundary):
 # Translate to local origin to avoid catastrophic cancellation.
 p0=boundary[0]['polygon'][0];total=0.
 for f in boundary:
  p=[sub(v,p0)for v in f['polygon']]
  total+=sum(dot(p[0],cross(p[i],p[i+1]))/6 for i in range(1,len(p)-1))
 return total

def overlap_area(a,b,n):
 p=a
 # b must be consistently oriented along n; clipping works in 3D.
 for x,y in zip(b,b[1:]+b[:1]):
  edge=sub(y,x);outward=cross(edge,n);p=clip(p,outward,dot(outward,x))
  if not p:return 0.
 return area(p)

def box(lo,hi):
 x,y,z=lo;X,Y,Z=hi
 return [[(x,y,z),(x,y,Z),(x,Y,Z),(x,Y,z)],[(X,y,z),(X,Y,z),(X,Y,Z),(X,y,Z)],[(x,y,z),(X,y,z),(X,y,Z),(x,y,Z)],[(x,Y,z),(x,Y,Z),(X,Y,Z),(X,Y,z)],[(x,y,z),(x,Y,z),(X,Y,z),(X,y,z)],[(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)]]

def tests():
 cases=[([box((0,0,0),(2,2,2))],8),([box((0,0,0),(2,2,2)),box((1,0,0),(3,2,2))],12),([box((0,0,0),(3,3,3)),box((1,1,1),(2,2,2))],27),([box((0,0,0),(1,1,1)),box((1,0,0),(2,1,1))],2),([box((0,0,0),(2,2,2)),box((0,0,0),(2,2,2))],8),([box((0,0,0),(1,3,1)),box((0,0,0),(3,1,1))],5)]
 for solids,expected in cases:assert abs(volume(union_boundary(solids))-expected)<1e-9
 return len(cases)
if __name__=='__main__':print('Partition math controls',tests())
