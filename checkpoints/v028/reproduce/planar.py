"""Planar fragment boundary recovery and deterministic hole triangulation."""
import math,collections

def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def signed(p):return sum(a[0]*b[1]-a[1]*b[0]for a,b in zip(p,p[1:]+p[:1]))/2

def inside(p,poly):
 yes=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>p[1])!=(b[1]>p[1])and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:yes=not yes
 return yes

def proper(a,b,c,d):return cross(a,b,c)*cross(a,b,d)<-1e-20 and cross(c,d,a)*cross(c,d,b)<-1e-20

def recover(polys,original,axis):
 uv=[a for a in range(3)if a!=axis];reg={}
 def key(p):
  k=tuple(round(p[a],10)for a in uv)
  reg.setdefault(k,p);return k
 originals=set(key(p)for p in original)
 rings=[[key(p)for p in poly]for poly in polys];points=list(reg);edges=collections.Counter()
 for poly in rings:
  for a,b in zip(poly,poly[1:]+poly[:1]):
   dx,dy=b[0]-a[0],b[1]-a[1];den=dx*dx+dy*dy
   if den<1e-24:continue
   line=[(0,a),(1,b)]
   for q in points:
    t=((q[0]-a[0])*dx+(q[1]-a[1])*dy)/den
    if 1e-12<t<1-1e-12 and abs(cross(a,b,q))<1e-8*math.sqrt(den):line.append((t,q))
   line.sort()
   for (_,v),(_,w)in zip(line,line[1:]):
    if v!=w:edges[(v,w)]+=1
 boundary=[]
 for (a,b),n in edges.items():
  count=n-edges[(b,a)]
  if count>0:
   if count!=1:raise RuntimeError('multiply covered planar fragments')
   boundary.append((a,b))
 nxt=collections.defaultdict(list)
 for a,b in boundary:nxt[a].append(b)
 if any(len(v)!=1 for v in nxt.values()):raise RuntimeError('branched planar boundary '+str([(k,v)for k,v in nxt.items()if len(v)!=1][:3]))
 todo=set(boundary);loops=[]
 while todo:
  a,b=min(todo);loop=[a];cur=a
  while True:
   nn=nxt[cur][0]
   if(cur,nn)not in todo:raise RuntimeError('broken boundary loop')
   todo.remove((cur,nn));cur=nn
   if cur==a:break
   loop.append(cur)
  changed=True
  while changed:
   changed=False
   for i,q in enumerate(loop):
    if q in originals:continue
    a,b=loop[i-1],loop[(i+1)%len(loop)]
    if abs(cross(a,q,b))<1e-8*max(1.,math.dist(a,b)):
     loop.pop(i);changed=True;break
  loops.append(loop)
 return loops,reg,uv

def earclip(poly):
 p=list(poly);out=[];guard=0
 while len(p)>3:
  guard+=1
  if guard>10000:raise RuntimeError('earclip bound')
  found=False
  for i,b in enumerate(p):
   a=p[i-1];c=p[(i+1)%len(p)]
   if cross(a,b,c)<=1e-12:continue
   bad=False
   for q in p:
    if q in (a,b,c):continue
    if cross(a,b,q)>=-1e-11 and cross(b,c,q)>=-1e-11 and cross(c,a,q)>=-1e-11:bad=True;break
   if bad:continue
   out.append([a,b,c]);p.pop(i);found=True;break
  if not found:
   # Only exact collinear redundant knots may be dropped, never a reflex corner.
   for i,b in enumerate(p):
    if abs(cross(p[i-1],b,p[(i+1)%len(p)]))<1e-12 and b not in (p[i-1],p[(i+1)%len(p)]):p.pop(i);found=True;break
  if not found:raise RuntimeError('no valid planar ear '+str(p))
 if len(p)==3 and cross(*p)>1e-12:out.append(p)
 return out

def triangulate(polys,original,axis):
 loops,reg,uv=recover(polys,original,axis)
 orig2=[tuple(round(p[a],10)for a in uv)for p in original];sgn=1 if signed(orig2)>0 else-1
 if sgn<0:loops=[p[::-1]for p in loops]
 outers=[p for p in loops if signed(p)>0];holes=[p for p in loops if signed(p)<0];out=[]
 for outer in outers:
  hs=[h for h in holes if inside(h[0],outer)];poly=outer[:]
  for hole in sorted(hs,key=lambda h:min(h)):
   choices=[]
   for i,a in enumerate(poly):
    for j,b in enumerate(hole):
     if a==b:continue
     if any(proper(a,b,c,d)for ring in loops for c,d in zip(ring,ring[1:]+ring[:1])):continue
     mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
     if not inside(mid,outer)or any(inside(mid,h)for h in hs):continue
     choices.append((math.dist(a,b),a,b,i,j))
   if not choices:raise RuntimeError('no visible hole bridge')
   _,a,b,i,j=min(choices);walk=hole[j:]+hole[:j]+[hole[j]];poly=poly[:i+1]+walk+[a]+poly[i+1:]
  tris=earclip(poly)
  expected=signed(outer)+sum(signed(h)for h in hs)
  if abs(sum(signed(t)for t in tris)-expected)>1e-7:raise RuntimeError('planar triangulated area mismatch')
  out.extend([[reg[q]for q in (t if sgn>0 else t[::-1])]for t in tris])
 return out
