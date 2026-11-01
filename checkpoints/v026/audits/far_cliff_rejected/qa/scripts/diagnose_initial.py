import json,numpy as np,hashlib
from pathlib import Path
p=Path('work/v027_far_buttress/selfcrossing_diagnostic.json');r=json.loads(p.read_text());v=np.array(r['coords']);ts=r['triangles'];rows=[]
for i,j in sorted(set(tuple(x)for x in r['strict_pairs'])):
 hits=[]
 for ti,tj in [(ts[i],ts[j]),(ts[j],ts[i])]:
  b=v[tj];e1=b[1]-b[0];e2=b[2]-b[0]
  for k in range(3):
   start=v[ti[k]];delta=v[ti[(k+1)%3]]-start;h=np.cross(delta,e2);det=e1@h
   if abs(det)<1e-14:continue
   d=start-b[0];u=d@h/det;q=np.cross(d,e1);w=delta@q/det;t=e2@q/det
   if min(u,w,1-u-w,t,1-t)>1e-9:hits.append({'point':list(start+t*delta),'segment_fraction':t,'triangle_barycentric':[1-u-w,u,w]})
 if hits:rows.append({'pair':[i,j],'hits':hits})
out={'diagnostic_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'confirmed_pairs':rows,'count':len(rows),'method':'Float64 direct segment/triangle interior test on actual saved-precision native export; no BVH predicate. Interior barycentric guard1e-9.','diagnosis':'Straight backwall bottom-to-top chord crosses bent outer section at thin buried end sections; construct profile-following internal backwall preserving outer coordinates, not tolerance relaxation.'};Path('work/v027_far_buttress_qa/initial_crossing_proof.json').write_text(json.dumps(out,indent=2));print(len(rows),'confirmed crossing pairs')
