"""Pure double-precision actual triangle predicates; no rendering/model mutation."""
import numpy as np,collections,math
import coplanar_predicate as cp

def topology(vertices,triangles):
 v=np.asarray(vertices,float);ts=np.asarray(triangles,int);t=v[ts];edges=collections.defaultdict(list)
 for i,f in enumerate(ts):
  for a,b in zip(f,np.roll(f,-1)):edges[tuple(sorted((int(a),int(b))))].append((int(a),int(b),i))
 bad=[list(k)for k,x in edges.items()if len(x)!=2 or x[0][:2]!=x[1][:2][::-1]]
 adj=[set()for _ in ts]
 for x in edges.values():
  for a in x:
   for b in x:adj[a[2]].add(b[2])
 seen=set();components=[]
 for i in range(len(ts)):
  if i in seen:continue
  todo=[i];seen.add(i);c=[]
  while todo:
   a=todo.pop();c.append(a)
   for b in adj[a]-seen:seen.add(b);todo.append(b)
  components.append(c)
 origin=v.mean(0);q=t-origin;area=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)/2
 return {'bad_oriented_edges':bad,'components':components,'minimum_triangle_area':float(area.min()),'signed_volume':float(np.einsum('ij,ij->i',q[:,0],np.cross(q[:,1],q[:,2])).sum()/6)},edges

def pair_crossings(a,b,guard=1e-9):
 hits=[]
 for t,u in [(a,b),(b,a)]:
  e1=u[1]-u[0];e2=u[2]-u[0]
  for k in range(3):
   d=t[(k+1)%3]-t[k];h=np.cross(d,e2);det=e1@h
   if abs(det)<1e-14:continue
   v=t[k]-u[0];aa=v@h/det;q=np.cross(v,e1);bb=d@q/det;rr=e2@q/det
   if min(aa,bb,1-aa-bb,rr,1-rr)>guard:hits.append(list(t[k]+rr*d))
 return hits

def self_intersections(vertices,triangles):
 ts=np.array(triangles);t=np.array(vertices)[ts];lo=t.min(1);hi=t.max(1);crossings=[];coplanars=[]
 for i in range(len(t)):
  ids=np.where(np.all(hi>=lo[i]-1e-7,axis=1)&np.all(lo<=hi[i]+1e-7,axis=1))[0]
  for j in ids:
   if j<=i:continue
   hits=pair_crossings(t[i],t[j])
   if hits:crossings.append({'triangles':[i,int(j)],'points':hits})
   c=cp.contact(t[i].tolist(),t[j].tolist(),1e-7)
   if c:coplanars.append({'triangles':[i,int(j)],**c})
 return {'strict_transverse_crossings':crossings,'positive_area_coplanar_overlaps':coplanars,'scope':'All triangle pairs with conservative explicit AABB, including shared-vertex pairs; strict interior segment/barycentric crossing and explicit coplanar polygon clipping, not BVH.overlap exclusion.'}

def nearest_distance(p,t):
 p=np.asarray(p);a=t[:,0];e=t[:,1]-a;f=t[:,2]-a;n=np.cross(e,f);nn=np.einsum('ij,ij->i',n,n);d=np.einsum('ij,ij->i',p-a,n);proj=p-d[:,None]*n/nn[:,None];q=proj-a;ee=np.einsum('ij,ij->i',e,e);ff=np.einsum('ij,ij->i',f,f);ef=np.einsum('ij,ij->i',e,f);qe=np.einsum('ij,ij->i',q,e);qf=np.einsum('ij,ij->i',q,f);den=ee*ff-ef*ef;u=(qe*ff-qf*ef)/den;v=(qf*ee-qe*ef)/den;dist=np.where((u>=0)&(v>=0)&(u+v<=1),d*d/nn,np.inf)
 for k in range(3):
  a=t[:,k];e=t[:,(k+1)%3]-a;tt=np.clip(np.einsum('ij,ij->i',p-a,e)/np.einsum('ij,ij->i',e,e),0,1);delta=p-(a+tt[:,None]*e);dist=np.minimum(dist,np.einsum('ij,ij->i',delta,delta))
 return float(np.sqrt(dist.min()))

def inside(p,t):
 p=np.asarray(p,float);e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];votes=[];counts=[]
 for d in [(1,.371,.613),(.217,1,.489),(.529,.193,1)]:
  d=np.array(d);d=d/np.linalg.norm(d);h=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,h);good=abs(det)>1e-14;inv=np.divide(1,det,out=np.zeros_like(det),where=good);q=p-t[:,0];u=np.einsum('ij,ij->i',q,h)*inv;c=np.cross(q,e1);v=(c@d)*inv;distance=np.einsum('ij,ij->i',e2,c)*inv;x=np.sort(distance[good&(u>=-1e-12)&(v>=-1e-12)&(u+v<=1+1e-12)&(distance>1e-9)]);unique=x[np.r_[True,np.diff(x)>1e-9]] if len(x)else x;counts.append(len(unique));votes.append(len(unique)%2)
 margin=nearest_distance(p,t)
 return {'state':'inside'if votes==[1,1,1]and margin>1e-5 else('outside'if votes==[0,0,0]and margin>1e-5 else'uncertain'),'parity':votes,'crossings':counts,'surface_margin':margin}

def upper_connected(vertices,triangles,level):
 v=np.asarray(vertices);ts=np.asarray(triangles);_,edges=topology(v,ts);active=set(np.where(v[ts][:,:,2].max(1)>level)[0]);adj={i:set()for i in active}
 for edge,records in edges.items():
  if max(v[edge[0],2],v[edge[1],2])<=level:continue
  ids={r[2]for r in records}&active
  for i in ids:adj[i]|=ids
 groups=[]
 while active:
  seed=next(iter(active));active.remove(seed);todo=[seed];group=[]
  while todo:
   i=todo.pop();group.append(i);neighbors=adj[i]&active;active-=neighbors;todo+=list(neighbors)
  groups.append(group)
 return {'level':level,'surface_components':len(groups),'triangle_counts':[len(x)for x in groups]}
