import json,numpy as np,pathlib
TOL=1e-6
P=pathlib.Path(__file__).resolve().parent;data=json.loads((P/'actual_geometry.json').read_text());lookup={x['name']:x for x in data}
def hit(t,lo,hi):
 c=(lo+hi)/2;h=(hi-lo)/2;v=t-c;e=np.roll(v,-1,axis=0)-v
 axes=[*np.eye(3),np.cross(e[0],e[1])]+[np.cross(a,b) for a in e for b in np.eye(3)]
 for a in axes:
  norm=np.linalg.norm(a)
  if norm<1e-12:continue
  a=a/norm
  s=v@a;r=h@np.abs(a)
  if s.min()>=r-TOL or s.max()<=-r+TOL:return False
 return True
obstacles=[x for x in data if 'supply bin' not in x['name']];report=[]
for name,obj in lookup.items():
 if 'supply bin' not in name:continue
 v=np.array(obj['vertices']);lo=v.min(axis=0);hi=v.max(axis=0);start=[lo.tolist(),hi.tolist()];north='north' in name
 # Box translated horizontally into the existing aisle; no hinge/rotation assumed.
 if north:lo[1]=37.1
 else:hi[1]=35.4
 collisions=[]
 for obs in obstacles:
  vs=np.array(obs['vertices']);ts=vs[np.array(obs['triangles'])];mask=np.all(ts.max(axis=1)>lo+TOL,axis=1)&np.all(ts.min(axis=1)<hi-TOL,axis=1)
  count=sum(hit(t,lo,hi)for t in ts[mask])
  if count:collisions.append({'object':obs['name'],'triangles':int(count)})
 report.append({'bin':name,'start_bounds':start,'sweep_bounds':[lo.tolist(),hi.tolist()],'boundary_collisions':collisions})
# Reject obvious penetration positive control; accept separated negative control.
t=np.array([[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]])
assert hit(t,np.array([.1,.1,-.1]),np.array([.3,.3,.1]));assert not hit(t,np.array([2.,2.,2.]),np.array([3.,3.,3.]))
for scale in [.001,1,100]:
 assert hit(t*scale,np.array([.1,.1,-.1])*scale,np.array([.3,.3,.1])*scale)
 assert not hit(t*scale,np.array([.1,.1,0])*scale,np.array([.3,.3,.1])*scale)
assert hit(t,np.array([.1,.1,-5e-6]),np.array([.3,.3,.1]))
assert not hit(t,np.array([.1,.1,5e-6]),np.array([.3,.3,.1]))
out={'obstacle_count':len(obstacles),'obstacles':[o['name']for o in obstacles],'scope' :'Conservative box-envelope horizontal extraction against the raw, unevaluated mesh surfaces of the six named racks, braces and room-shell objects. Does not certify human ergonomics, load, box operability, all-scene exclusion or enclosed-volume containment. Touching surfaces excluded at 1e-6 scene-unit tolerance on normalized SAT axes and AABB prefilter.','bins':report,'controls_pass':True,'no_detected_boundary_crossings':all(not x['boundary_collisions'] for x in report)}
(P/'RETRIEVAL_AUDIT.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
