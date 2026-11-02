"""Independent exact 2D ear clipping of simple axis-planar saved polygons.
Derived CPU triangulation for planar surface-set proof only; native loop triangles
remain authoritative for saved-engine topology receipts.
"""
from fractions import Fraction as F
from exact_axis_boundary import signed_area

def orient(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def point_in_tri(p,a,b,c,sgn):return all(sgn*orient(x,y,p)>=0 for x,y in [(a,b),(b,c),(c,a)])
def triangulate(vertices,face):
 p3=[vertices[i] for i in face];axes=[k for k in range(3) if all(p[k]==p3[0][k] for p in p3)]
 if len(axes)!=1:raise ValueError('Non-axis parent polygon')
 axis=axes[0];uv={i:tuple(F(float(vertices[i][k])) for k in range(3) if k!=axis) for i in face};ids=list(face)
 if len(set(ids))!=len(ids):raise ValueError('Repeated parent vertex')
 changed=True
 while changed and len(ids)>3:
  changed=False
  for j,i in enumerate(ids):
   a,b,c=uv[ids[j-1]],uv[i],uv[ids[(j+1)%len(ids)]]
   if orient(a,b,c)==0:
    if not all(min(a[k],c[k])<=b[k]<=max(a[k],c[k]) for k in range(2)):raise ValueError('Collinear backtracking polygon')
    ids.pop(j);changed=True;break
 area=signed_area([uv[i] for i in ids]);sgn=1 if area>0 else -1
 if area==0:raise ValueError('Zero parent polygon')
 # A simple polygon cannot have non-neighbor proper crossings or endpoint-on-edge.
 for i,aidx in enumerate(ids):
  bidx=ids[(i+1)%len(ids)]
  for j in range(i+1,len(ids)):
   cidx=ids[j];didx=ids[(j+1)%len(ids)]
   if {aidx,bidx}&{cidx,didx}:continue
   a,b,c,d=uv[aidx],uv[bidx],uv[cidx],uv[didx]
   o=[orient(a,b,c),orient(a,b,d),orient(c,d,a),orient(c,d,b)]
   if o[0]*o[1]<0 and o[2]*o[3]<0:raise ValueError('Self-crossing parent polygon')
   for point,x,y in [(c,a,b),(d,a,b),(a,c,d),(b,c,d)]:
    if orient(x,y,point)==0 and all(min(x[k],y[k])<=point[k]<=max(x[k],y[k]) for k in range(2)):raise ValueError('Non-neighbor polygon contact')
 triangles=[]
 while len(ids)>3:
  for j,i in enumerate(ids):
   a,b,c=ids[j-1],i,ids[(j+1)%len(ids)]
   if sgn*orient(uv[a],uv[b],uv[c])<=0:continue
   if any(point_in_tri(uv[k],uv[a],uv[b],uv[c],sgn) for k in ids if k not in (a,b,c)):continue
   triangles.append([a,b,c]);ids.pop(j);break
  else:raise ValueError('No valid exact ear')
 triangles.append(ids)
 actual=sum(signed_area([uv[i] for i in t]) for t in triangles)
 if actual!=area:raise ValueError('Tessellation area differs')
 return triangles
