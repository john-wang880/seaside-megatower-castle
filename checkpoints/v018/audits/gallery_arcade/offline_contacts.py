import json,itertools,math
from pathlib import Path
P=Path(__file__).resolve().parent;data=json.loads((P/'components_extended.json').read_text())
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def norm(a):
 n=math.sqrt(dot(a,a));return tuple(x/n for x in a) if n>1e-10 else None
def verts(c):return list(c['coords'].values())
def planes(v):
 r=[]
 for a,b,c in itertools.combinations(v,3):
  n=norm(cross(sub(b,a),sub(c,a)))
  if n is None:continue
  ds=[dot(n,sub(p,a)) for p in v]
  if max(ds)<1e-7:r.append((n,dot(n,a)))
  elif min(ds)>-1e-7:r.append((tuple(-x for x in n),-dot(n,a)))
 return r
def sat(c,d):
 v,w=verts(c),verts(d);pv,pw=planes(v),planes(w);axes=[n for n,h in pv+pw];ev=[sub(a,b) for a,b in itertools.combinations(v,2)];ew=[sub(a,b) for a,b in itertools.combinations(w,2)];axes += [n for a in ev for b in ew if (n:=norm(cross(a,b))) is not None];minimum=1e9
 for n in axes:
  x=[dot(n,p) for p in v];y=[dot(n,p) for p in w];depth=min(max(x),max(y))-max(min(x),min(y));minimum=min(minimum,depth)
  if depth < -1e-6:return {'intersects':False,'separating_gap':-depth}
 # Grid witness inside exact convex hulls, report separately from projection overlap.
 lo=[max(c['bounds'][0][a],d['bounds'][0][a]) for a in range(3)];hi=[min(c['bounds'][1][a],d['bounds'][1][a]) for a in range(3)];witness=None
 for f in itertools.product((.1,.3,.5,.7,.9),repeat=3):
  q=[lo[a]+f[a]*(hi[a]-lo[a]) for a in range(3)]
  if all(dot(n,q)<h-1e-6 for n,h in pv+pw):witness=q;break
 return {'intersects':True,'minimum_axis_overlap':minimum,'positive_interior_grid_witness':witness}
def parity(c,q,d):
 hits=[]
 for f in c['polygons']:
  pts=[c['coords'][str(i)] for i in f['vertices']]
  for i in range(1,len(pts)-1):
   a,b,z=pts[0],pts[i],pts[i+1];e1=sub(b,a);e2=sub(z,a);h=cross(d,e2);det=dot(e1,h)
   if abs(det)<1e-10:continue
   inv=1/det;v=sub(q,a);u=dot(v,h)*inv
   if u<0 or u>1:continue
   qq=cross(v,e1);vv=dot(d,qq)*inv
   if vv<0 or u+vv>1:continue
   t=dot(e2,qq)*inv
   if t>1e-7 and not any(abs(t-t0)<1e-6 for t0 in hits):hits.append(t)
 return len(hits)%2==1
west={c['seed']:c for c in data[0]['components']};checks=[]
for a,b in [(376,48),(376,56),(376,368),(368,360),(368,304),(392,56),(392,384)]:checks.append({'components':[a,b],'result':sat(west[a],west[b])})
for check in checks:
 a,b=check['components'];q=check['result'].get('positive_interior_grid_witness')
 if q:
  check['result']['actual_face_fan_three_ray_inside_both']=[all(parity(c,q,d) for c in (west[a],west[b])) for d in [(0.827,.391,.404),(.217,.901,.376),(.513,.249,.821)]]
par=data[2]['components'];adj={c['seed']:set() for c in par};links=[]
for a,b in itertools.combinations(par,2):
 if any(a['bounds'][1][i]<b['bounds'][0][i]-1e-6 or b['bounds'][1][i]<a['bounds'][0][i]-1e-6 for i in range(3)):continue
 r=sat(a,b)
 if r['intersects']:adj[a['seed']].add(b['seed']);adj[b['seed']].add(a['seed']);links.append({'components':[a['seed'],b['seed']],'result':r})
islands=[]
while adj:
 q=[next(iter(adj))];g=set()
 while q:
  k=q.pop()
  if k not in adj:continue
  g.add(k);q.extend(adj.pop(k)-g)
 islands.append(sorted(g))
report={'method':'Convex hull SAT of actual component world vertices; all hull-triple normals and all edge-direction crosses; positive grid witness checks. Does not imply structural capacity. Nonplanar original quads replaced only analytically by their vertex convex hull, not model mutation.','west_selected_contacts':checks,'parapet_component_count':len(par),'parapet_islands':islands,'parapet_links':links,'limitations':'Bounded same-object contact audit. External masonry/pinnacle anchoring not certified by this test; no geometry changes.'};(P/'offline_contacts.json').write_text(json.dumps(report,indent=2));print(checks);print('PARAPET',list(map(len,islands)),len(links))
