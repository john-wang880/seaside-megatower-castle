import os
"""Finite saved-geometry destination/aperture rays, not pixel-area certification."""
import json,hashlib
from pathlib import Path
import numpy as np
import check_payload as p
import check_guard as q
D=Path(os.environ['V029_QA_OUTPUT']);n=json.loads((Path(os.environ['V029_QA_DATA'])/'native.json').read_text());plan=json.loads((Path(os.environ['V029_QA_DATA'])/'fixture_plan.json').read_text());guard=json.loads((Path(os.environ['V029_QA_DATA'])/'guard_plan.json').read_text());geo=json.loads((D/'saved_geometry.json').read_text());fix=json.loads((D/'saved_fixtures.json').read_text());C=list(map(p.box,guard['cavities']));components=[c for c in n['components']if c['object']not in q.NAMES]+fix['components']+[{'vertices':m['vertices'],'local_triangles':m['triangles']}for m in geo['meshes']];tris=np.concatenate([np.asarray(c['vertices'])[c['local_triangles']]for c in components]);lo=tris.min(1);hi=tris.max(1);rows=[]
for v in plan['views']:
 eye=np.array(v['eye']);target=C[0]if v['key']=='stores_entry'else C[1];x=target[1][0]if v['key']=='stores_entry'else target[0][0]
 for y in np.linspace(target[0][1]+.01,target[1][1]-.01,5):
  for z in np.linspace(target[0][2]+.01,target[1][2]-.01,5):
   end=np.array([x,y,z]);d=end-eye;tt=tris[np.all(hi>=np.minimum(eye,end),axis=1)&np.all(lo<=np.maximum(eye,end),axis=1)];e1=tt[:,1]-tt[:,0];e2=tt[:,2]-tt[:,0];h=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.einsum('ij,ij->i',e1,h);valid=np.abs(det)>1e-12;tt=tt[valid];e1=e1[valid];e2=e2[valid];h=h[valid];det=det[valid];s=eye-tt[:,0];u=np.einsum('ij,ij->i',s,h)/det;c=np.cross(s,e1);vv=c@d/det;t=np.einsum('ij,ij->i',e2,c)/det;hit=(u>=0)&(vv>=0)&(u+vv<=1)&(t>1e-9)&(t<1-1e-9);q.require(not hit.any(),'Saved aperture/destination blocked');rows.append({'view':v['key'],'end':end.tolist(),'clear_open_segment':True})
r={'pass':True,'candidate_sha256':geo['candidate_sha256'],'rays':rows,'count':len(rows),'scope':'Fifty actual saved-geometry rays to interior aperture/destination grid; endpoints on wall/aperture plane excluded, no whole projected-region/pixel coverage claim. Prospective continuous air and full aperture projection separately proven.'};(D/'SAVED_VISIBILITY.json').write_text(json.dumps(r,indent=2)+'\n');print('SAVED VISIBILITY PASS',len(rows))
