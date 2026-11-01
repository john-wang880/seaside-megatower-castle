import hashlib,json,numpy as np,collections
from pathlib import Path
from geometry_checks import inside,topology
import argparse
p=argparse.ArgumentParser();p.add_argument('--geometry',required=True);p.add_argument('--report',required=True);a=p.parse_args();assert not Path(a.report).exists();geometry_path=Path(a.geometry);g=json.loads(geometry_path.read_text());lo=np.array(g['candidate_bounds'][0]);hi=np.array(g['candidate_bounds'][1]);center=(lo+hi)/2;extent=(hi-lo)/2
hosts={'V012 | hall south stone lining','V012 | hall north stone lining','V012 | entrance hall ceiling lining'};name='V027 | three pointed bays with high wall bands'
def sat(tri,lo,hi):
 c=(lo+hi)/2;e=(hi-lo)/2;tr=tri-c;edges=np.roll(tr,-1,axis=0)-tr;axes=list(np.eye(3))+[np.cross(edges[0],edges[1])]+[np.cross(x,y)for x in edges for y in np.eye(3)];best=0
 for axis in axes:
  n=np.linalg.norm(axis)
  if n<1e-14:continue
  axis=axis/n;p=tr@axis;r=np.abs(axis)@e;best=max(best,float(p.min()-r),float(-r-p.max()))
 return best
assert sat(np.array([[2.,0,0],[0,2,0],[2,2,0]]),np.array([0,0,-.1]),np.array([.5,.5,.1]))>0
assert sat(np.array([[-1.,0,0],[1,0,0],[0,1,0]]),np.array([-.1,-.1,-.1]),np.array([.1,.1,.1]))==0
rows=[];fail=[];pt=np.array([-1.8,38,32.81])
for n,o in g['objects'].items():
 if n==name or n in hosts:continue
 v=np.array(o['vertices']);ts=np.array(o['triangles']);t=v[ts];ids=np.where(np.all(t.max(1)>=lo,1)&np.all(t.min(1)<=hi,1))[0];sats=[{'triangle':int(i),'separation_lower_bound':sat(t[i],lo,hi)}for i in ids]
 if any(x['separation_lower_bound']<=1e-7 for x in sats):fail.append('triangle-box not separated '+n)
 # Full connected components, not parity over overlapping disconnected bodies.
 parent=list(range(len(v)))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for f in ts:
  root=find(int(f[0]))
  for x in f[1:]:parent[find(int(x))]=root
 comps=collections.defaultdict(list)
 for i,f in enumerate(ts):comps[find(int(f[0]))].append(i)
 candidates=[]
 for seed,indices in comps.items():
  ct=t[indices];cl=ct.min((0,1));ch=ct.max((0,1))
  if np.any(ch<lo)or np.any(cl>hi):continue
  # No candidate-envelope/source-surface intersection; test one known new interior point.
  state=inside(pt,ct);candidate={'seed':int(seed),'triangle_count':len(indices),'bounds':[cl.tolist(),ch.tolist()],'union_interior_probe':state}
  verts=sorted(set(ts[indices].flat));mapping={x:i for i,x in enumerate(verts)};tt=[[mapping[x]for x in f]for f in ts[indices]];closed,_=topology(v[verts],tt);candidate['closed_edges']=not closed['bad_oriented_edges'];candidate['positive_volume']=closed['signed_volume']>0
  if not candidate['closed_edges']or not candidate['positive_volume']or state['state']!='outside':fail.append('component containment uncertain/collision '+n)
  # A full old component cannot be enclosed by new envelope if its bounds extend outside.
  candidate['not_wholly_enclosed_by_new_box']=bool(np.any(cl<lo)|np.any(ch>hi));assert candidate['not_wholly_enclosed_by_new_box']
  candidates.append(candidate)
 rows.append({'object':n,'triangle_box_false_positives':sats,'full_component_containment_checks':candidates})
r={'pass':not fail,'geometry_sha256':hashlib.sha256(geometry_path.read_bytes()).hexdigest(),'failures':fail,'input_sha256':g['input_sha256'],'actual_triangle_box_separation':rows,'controls':2,'scope':'Explicit triangle-vs-entire-addition-box SAT resolves broadphase candidates. Full connected old components with overlapping bounds checked separately for closedness and outside parity at known new-union interior point; no crossing of entire box plus connected new union excludes unobserved containment. No AABB-only collision waiver.'};Path(a.report).write_text(json.dumps(r,indent=2));print(r['pass'],fail);assert r['pass']
