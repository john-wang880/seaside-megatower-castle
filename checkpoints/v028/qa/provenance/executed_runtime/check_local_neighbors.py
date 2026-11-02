"""Exact coplanar patch scan against every preserved component in bounded source export."""
import json,hashlib
from pathlib import Path
from collections import defaultdict
from fractions import Fraction as F
from exact_axis_boundary import fraction3,cross,area,clip_convex,bounds,positive_bbox
P=Path(__file__).resolve().parent
n=json.loads((P/'native_geometry.json').read_text());src=P.parent/'principal_hall_v027/A_approach/native.json';s=json.loads(src.read_text());payload=json.loads((P.parent/'v028_receiving_chamber/geometry_builder/geometry_final.json').read_text());targets={(t['object'],t['evaluated_seed']) for t in payload['targets']};m=n['meshes'][-1]
def triangles(vertices,tris):
 out=[]
 for i,ids in enumerate(tris):
  p=[fraction3(vertices[j]) for j in ids];normal=cross(tuple(p[1][k]-p[0][k] for k in range(3)),tuple(p[2][k]-p[0][k] for k in range(3)))
  if not any(normal):continue
  axes=[k for k in range(3) if all(q[k]==p[0][k] for q in p)]
  if len(axes)!=1:continue
  axis=axes[0];poly=[tuple(q[k] for k in range(3) if k!=axis) for q in p];out.append((i,axis,p[0][axis],1 if normal[axis]>0 else -1,poly,bounds(poly)))
 return out
local=triangles(m['vertices'],m['triangles']);contacts=[]
neighbors=list(s['components'])+[{'object':q['name'],'seed':0,'vertices':q['vertices'],'local_triangles':q['triangles']} for q in n['meshes'][:-1]]
for c in neighbors:
 if (c['object'],c['seed']) in targets:continue
 sums=defaultdict(F);pairs=0
 source_triangles=triangles(c['vertices'],c['local_triangles'])
 for i,axis,plane,sign,p,pb in local:
  for j,ax,pl,sg,q,qb in source_triangles:
   if axis==ax and plane==pl and positive_bbox(pb,qb):
    ar=area(clip_convex(p,q))
    if ar:sums[(axis,str(plane),sign==sg)]+=ar;pairs+=1
 if sums:contacts.append({'object':c['object'],'seed':c['seed'],'pairs':pairs,'planes':[{'axis':k[0],'plane':k[1],'same_facing':k[2],'pairwise_area':float(v)} for k,v in sums.items()]})
out={'candidate_sha256':n['candidate_sha256'],'source_export_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'contacts':contacts,'scope':'Local shell versus all preserved components in complete bounded export; exact axis-plane polygon clipping, not BVH. Pairwise contact sums are not unique exposed area. Outside remote inherited surfaces are separately exact.'};(P/'local_neighbors_with_interfaces.json').write_text(json.dumps(out,indent=2));print(json.dumps(contacts,indent=2))
