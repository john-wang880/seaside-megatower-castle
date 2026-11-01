"""Double precision planar clipping and affine height functions; no I/O/dependencies."""
import math
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def sub(a,b):return(a[0]-b[0],a[1]-b[1])
def area(p):return abs(sum(cross(sub(p[i],p[0]),sub(p[i+1],p[0]))for i in range(1,len(p)-1)))/2 if len(p)>=3 else 0.
def signed(p):return sum(cross(sub(p[i],p[0]),sub(p[i+1],p[0]))for i in range(1,len(p)-1))/2

def halfplane(poly,fn):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  fa,fb=fn(a),fn(b)
  if fa>=0:out.append(a)
  if (fa>=0)!=(fb>=0):
   t=fa/(fa-fb);out.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])))
 return out

def clip(poly,window):
 if signed(window)<0:window=window[::-1]
 for a,b in zip(window,window[1:]+window[:1]):
  d=sub(b,a);poly=halfplane(poly,lambda p:cross(d,sub(p,a)))
  if len(poly)<3:return[]
 return poly

def plane(t):
 a,b,c=t;u=sub(b,a);v=sub(c,a);det=cross(u,v);assert abs(det)>1e-12
 gx=((b[2]-a[2])*v[1]-(c[2]-a[2])*u[1])/det;gy=(u[0]*(c[2]-a[2])-v[0]*(b[2]-a[2]))/det
 return lambda p:a[2]+gx*(p[0]-a[0])+gy*(p[1]-a[1])

def bounds(t):return [min(v[0]for v in t),min(v[1]for v in t),max(v[0]for v in t),max(v[1]for v in t)]

def triangle_overlay(path_triangle,terrain_triangles):
 p=[tuple(v[:2])for v in path_triangle];pz=plane(path_triangle);pb=bounds(path_triangle);pieces=[]
 for index,t in enumerate(terrain_triangles):
  tb=bounds(t)
  if pb[0]>tb[2]or tb[0]>pb[2]or pb[1]>tb[3]or tb[1]>pb[3]:continue
  poly=clip(p,[tuple(v[:2])for v in t]);aa=area(poly)
  if aa<=1e-13:continue
  tz=plane(t);values=[pz(q)-tz(q)for q in poly];pieces.append({'terrain_index':index,'polygon':poly,'area':aa,'minimum':min(values),'maximum':max(values)})
 return pieces
