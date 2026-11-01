import json,numpy as np
from pathlib import Path
import argparse
p=argparse.ArgumentParser();p.add_argument('--geometry',required=True);p.add_argument('--report',required=True);args=p.parse_args();assert not Path(args.report).exists();geometry_path=Path(args.geometry);g=json.loads(geometry_path.read_text());d=g['objects']['V027 | three pointed bays with high wall bands'];v=np.array(d['vertices']);ts=np.array(d['triangles']);t=v[ts];bad=[];epsilon=1e-7
for i,a in enumerate(t):
 for j in range(i+1,len(t)):
  b=t[j]
  if np.any(a.max(0)<b.min(0)-epsilon)or np.any(b.max(0)<a.min(0)-epsilon):continue
  common=sorted(set(ts[i])&set(ts[j]));hits=[]
  for f,u in [(a,b),(b,a)]:
   e1=u[1]-u[0];e2=u[2]-u[0]
   for k in range(3):
    direction=f[(k+1)%3]-f[k];h=np.cross(direction,e2);det=e1@h
    if abs(det)<1e-14:continue
    x=f[k]-u[0];aa=x@h/det;q=np.cross(x,e1);bb=direction@q/det;tt=e2@q/det
    if min(aa,bb,1-aa-bb,tt,1-tt)>=-1e-10:
     p=f[k]+tt*direction
     if not common:dist=float('inf')
     elif len(common)==1:dist=np.linalg.norm(p-v[common[0]])
     else:
      c=v[common[0]];e=v[common[1]]-c;dist=np.linalg.norm(p-(c+np.clip((p-c)@e/(e@e),0,1)*e))
     if dist>epsilon:hits.append({'point':list(p),'distance_to_shared_simplex':float(dist)})
  if hits:bad.append({'pair':[i,j],'common_vertex_ids':[int(x)for x in common],'contacts':hits})
r={'pass':not bad,'noncoplanar_contacts_outside_shared_simplex':bad,'epsilon':epsilon,'unique_coordinate_count':len({tuple(x)for x in v}),'vertex_count':len(v),'scope':'Inclusive endpoint/edge triangle contacts tested, with shared topological vertex/edge permitted only within1e-7; complements strict crossing and positive-area coplanar proof.'};assert r['unique_coordinate_count']==len(v);Path(args.report).write_text(json.dumps(r,indent=2));print(r['pass'],len(bad));assert r['pass']
