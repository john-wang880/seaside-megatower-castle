"""Pure double-precision convex triangle overlay; no external dependencies."""
def area(poly):return abs(sum(a[0]*b[1]-a[1]*b[0]for a,b in zip(poly,poly[1:]+poly[:1]))*.5)if poly else 0
def ccw(poly):
 return poly if sum(a[0]*b[1]-a[1]*b[0]for a,b in zip(poly,poly[1:]+poly[:1]))>0 else poly[::-1]
def cut(poly,fn):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  fa,fb=fn(a),fn(b)
  if fa>=0:out.append(a)
  if(fa>=0)!=(fb>=0):
   t=fa/(fa-fb);out.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])))
 return out
def clip(poly,tri):
 for a,b in zip(tri,tri[1:]+tri[:1]):
  poly=cut(poly,lambda p:(b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]))
  if not poly:break
 return poly
def plane(vs):
 p,q,r=vs;u=[q[i]-p[i]for i in range(3)];v=[r[i]-p[i]for i in range(3)];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];a,b=-n[0]/n[2],-n[1]/n[2];return a,b,p[2]-a*p[0]-b*p[1]
