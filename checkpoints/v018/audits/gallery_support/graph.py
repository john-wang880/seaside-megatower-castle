"""Independent double-precision actual-polyhedron connectivity, read-only JSON input."""
import json,math,collections,time,itertools
from pathlib import Path
import numpy as np
P=Path('work/gallery_support_graph_v018');start=time.time();raw=json.load(open(P/'geometry.json'));C=raw['components'];EPS=1e-7;NEAR=2e-5

def axes_unique(axes):
 out=[]
 for n in axes:
  length=np.linalg.norm(n)
  if length<1e-12:continue
  n=n/length
  if next((x for x in n if abs(x)>1e-8),1)<0:n=-n
  if not any(np.max(abs(n-q))<1e-8 for q in out):out.append(n)
 return np.array(out)
def prep(c):
 v=np.array(c['vertices'],float);t=np.array(c['triangles'],int);tri=v[t];ed=np.concatenate([tri[:,1]-tri[:,0],tri[:,2]-tri[:,1],tri[:,0]-tri[:,2]]);norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);convex=c['closed']
 for face,n in zip(tri,norm):
  length=np.linalg.norm(n)
  if length<1e-12:convex=False;continue
  ds=(v-face[0])@(n/length)
  if ds.min() < -EPS and ds.max()>EPS:convex=False;break
 normals=axes_unique(norm) if convex else np.empty((0,3));edges=axes_unique(ed) if convex else np.empty((0,3))
 return {'v':v,'t':t,'tri':tri,'normals':normals,'edges':edges,'convex':convex,'lo':v.min(axis=0),'hi':v.max(axis=0),'closed':c['closed']}
cache={}
def get(i):
 if i not in cache:cache[i]=prep(C[i])
 return cache[i]
def project_gap(a,b,axes):
 if len(axes)==0:return float('inf')
 x=a@axes.T;y=b@axes.T
 return float(np.max(np.maximum(x.min(axis=0)-y.max(axis=0),y.min(axis=0)-x.max(axis=0))))
def tri_gap(a,b):
 ea=np.roll(a,-1,axis=0)-a;eb=np.roll(b,-1,axis=0)-b;na=np.cross(ea[0],ea[1]);nb=np.cross(eb[0],eb[1]);axes=[na,nb]+[np.cross(x,y) for x in ea for y in eb]+[np.cross(na,e) for e in ea]+[np.cross(nb,e) for e in eb]
 return project_gap(a,b,axes_unique(axes))
def inside(q,s):
 if not s['closed']:return None
 votes=[];tri=s['tri'];e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0]
 for d in [(1,.371,.613),(.217,1,.489),(.529,.193,1)]:
  d=np.array(d);d/=np.linalg.norm(d);h=np.cross(d,e2);det=np.sum(e1*h,axis=1);good=abs(det)>1e-12;inv=np.zeros_like(det);inv[good]=1/det[good];v=q-tri[:,0];u=np.sum(v*h,axis=1)*inv;cross=np.cross(v,e1);w=(cross@d)*inv;dist=np.sum(e2*cross,axis=1)*inv;hits=sorted(dist[good&(u>=-1e-10)&(w>=-1e-10)&(u+w<=1+1e-10)&(dist>EPS)]);unique=[]
  for h0 in hits:
   if not unique or abs(h0-unique[-1])>EPS:unique.append(h0)
  votes.append(len(unique)%2)
 return bool(votes[0]) if len(set(votes))==1 else None
def contact(a,b):
 gap=max(np.max(a['lo']-b['hi']),np.max(b['lo']-a['hi']))
 if gap>NEAR:return 'separated',gap
 if a['convex'] and b['convex']:
  axes=np.concatenate([a['normals'],b['normals'],axes_unique(np.cross(a['edges'][:,None,:],b['edges'][None,:,:]).reshape(-1,3))]);gap=project_gap(a['v'],b['v'],axes)
  if gap>NEAR:return 'separated',gap
  if gap>EPS:return 'near_uncertain',gap
  return 'convex_solid_overlap_or_touch',gap
 if not a['closed'] or not b['closed']:return 'open_uncertain',None
 # Interior vertex witness gives actual solid contact without surface crossings.
 uncertain_parity=False
 for source,dest in [(a,b),(b,a)]:
  for q in [source['v'][0],source['v'].mean(axis=0)]:
   if np.any(q<dest['lo']) or np.any(q>dest['hi']):continue
   own=inside(q,source);other=inside(q,dest)
   if own is True and other is True:return 'contained_interior_witness',q.tolist()
   if own is None or other is None:uncertain_parity=True
 # Actual triangle SAT, including coplanar in-plane separating axes.
 near=None
 for ta in a['tri']:
  ids=np.where(np.all(b['tri'].min(axis=1)<=ta.max(axis=0)+NEAR,axis=1)&np.all(b['tri'].max(axis=1)>=ta.min(axis=0)-NEAR,axis=1))[0]
  for j in ids:
   g=tri_gap(ta,b['tri'][j])
   if g<=EPS:return 'actual_triangle_contact',g
   if g<=NEAR:near=g
 # Full containment has no surface crossing; test actual closed-solid parity.
 for source,dest in [(a,b),(b,a)]:
  for q in [source['v'][0],source['v'].mean(axis=0)]:
   if inside(q,source) is True and inside(q,dest) is True:return 'contained_interior_witness',q.tolist()
  q=source['v'][0]
  if inside(q,dest) is True:return 'contained_boundary_vertex_witness',q.tolist()
 if near is not None:return 'near_uncertain',near
 if uncertain_parity:return 'parity_uncertain',None
 return 'separated',None
# Negative controls: overlap of bounding boxes alone is never contact.
a=np.array([[0,0,0],[2,0,0],[0,2,0]],float);b=np.array([[2,2,0],[2,.9,0],[.9,2,0]],float);assert tri_gap(a,b)>0
assert tri_gap(a,a)==0
# Tetrahedron fixtures, including complete containment without surface crossing.
faces=[[0,2,1],[0,1,3],[0,3,2],[1,2,3]]
def tet(v):return prep({'vertices':v,'triangles':faces,'closed':True})
t=tet([[0,0,0],[3,0,0],[0,3,0],[0,0,3]]);small=tet([[.2,.2,.2],[.3,.2,.2],[.2,.3,.2],[.2,.2,.3]]);assert inside(np.array([.23,.23,.23]),t) and inside(np.array([.23,.23,.23]),small);assert contact(t,small)[0]!='separated'
shift=tet([[4,4,4],[4.1,4,4],[4,4.1,4],[4,4,4.1]]);assert contact(t,shift)[0]=='separated'
def reachable(edges,root):
 adj=collections.defaultdict(set)
 for a,b in edges:adj[a].add(b);adj[b].add(a)
 seen={root};q=[root]
 while q:
  for n in adj[q.pop()]-seen:seen.add(n);q.append(n)
 return seen
assert 2 in reachable([(0,1),(1,2)],0) and 2 not in reachable([(0,1)],0)
# Root choices are explicit primary visible bodies, not all pieces in a merged object.
ROOTS=[('V005 | main tower calibrated stone surface',8),('V008 | gallery with genuine eastern approach portal',8),('V012 | ashlar with bounded entrance and north stairwell',576)]
roots=[i for i,c in enumerate(C) if (c['object'],c['seed']) in ROOTS];assert len(roots)==3
lo=np.array([c['bounds'][0] for c in C]);hi=np.array([c['bounds'][1] for c in C]);targets={i for i,c in enumerate(C) if c['target']};parents={i:None for i in roots};queue=collections.deque(roots);tested=set();edges=[];uncertain=[];n=0
while queue and not targets.issubset(parents):
 i=queue.popleft();candidates=np.where(np.all(lo<=hi[i]+NEAR,axis=1)&np.all(hi>=lo[i]-NEAR,axis=1))[0]
 for j in candidates:
  j=int(j)
  if j in parents or j==i:continue
  key=tuple(sorted((i,j)))
  if key in tested:continue
  tested.add(key);kind,detail=contact(get(i),get(j))
  if kind.endswith('uncertain'):uncertain.append({'a':i,'b':j,'type':kind,'detail':detail})
  elif kind!='separated':parents[j]=i;queue.append(j);edges.append({'a':i,'b':j,'type':kind,'detail':detail})
 n+=1
 if n<5 or n%100==0:print('GRAPH',n,'connected',len(targets&parents.keys()),'/',430,'tested',len(tested),flush=True)
def name(i):return {'object':C[i]['object'],'seed':C[i]['seed'],'bounds':C[i]['bounds']}
chains=[]
for i in sorted(targets&parents.keys()):
 chain=[i]
 while parents[chain[-1]] is not None:chain.append(parents[chain[-1]])
 chains.append({'target':i,'chain_to_root':chain})
unresolved=sorted(targets-parents.keys());r={'source_sha256':raw['source_sha256'],'source_unchanged_at_export':raw['source_unchanged'],'target_count':430,'connected_target_count':len(chains),'examined_component_count':len(C),'tested_pair_count':len(tested),'roots':[name(i) for i in roots],'nodes':{str(i):name(i) for i in set(parents)|targets},'contact_edges':edges,'root_chains':chains,'unresolved_target_ids':unresolved,'uncertain_edges':uncertain,'tolerances':{'contact_epsilon_numerical_not_exact_zero_certificate':EPS,'near_uncertain_gap':NEAR},'negative_controls':{'overlapping_AABB_disjoint_coplanar_triangles_rejected':True,'same_triangle_touch_accepted':True,'contained_closed_tetrahedron_no_surface_crossing_accepted':True,'translated_tetrahedron_rejected':True,'broken_bridge_root_chain_rejected':True},'scope':'Geometric attachment to three explicitly nominated primary visible bodies, not gravity/load/engineering or ground continuity. Full target components; unresolved means not connected in examined neighborhood, never floating certification.','seconds':time.time()-start};(P/'support_graph.json').write_text(json.dumps(r,indent=2));print('FINAL',len(chains),len(unresolved),len(tested),'seconds',r['seconds'],flush=True)
