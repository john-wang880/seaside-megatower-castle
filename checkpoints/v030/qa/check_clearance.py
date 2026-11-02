"""Actual saved fittings versus source, protected volumes, explicit planes and fixed rays."""
import json,sys,itertools,collections,hashlib
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import audit_geometry as a
R=a.R;D=Path(__import__('os').environ['FITTINGS_QA_OUTPUT']);e=a.e;need=a.need
p=json.loads((R/'PLAN.json').read_text());g=json.loads((D/'geometry.json').read_text());_,parts=a.audit(g,p);oldgeo=json.loads((R/'saved_geometry.json').read_text());fixtures=json.loads((R/'saved_fixtures.json').read_text());source=json.loads((R/'native.json').read_text());oldtargets={'V028 | foundation outside chamber guard','V028 | ashlar outside chamber guard','V028 | local receiving chamber shell'};scene=[c for c in source['components']if c['object']not in oldtargets]+fixtures['components']+[{'object':m['name'],'seed':0,'vertices':m['vertices'],'local_faces':m['faces'],'local_triangles':m['triangles']}for m in oldgeo['meshes']]
body=[[14.6,35.6,29.025],[23.3,36.8,31.1]];floor_contacts=[]
for part in parts:
 vv=np.array(part['vertices']);box=[vv.min(0),vv.max(0)];need(a.analyze(part,body)['disjoint'],'Actual protected body hit')
 for comp in scene:
  hit=a.analyze(comp,box)
  if hit['disjoint']:continue
  need(part['kind']=='post'and hit['actual_boundary_triangles'],'Possible source collision '+part['id'])
  for ti in hit['actual_boundary_triangles']:need(all(comp['vertices'][i][2]==29 for i in comp['local_triangles'][ti]),'Nonfloor source contact')
  if hit['closed_oriented']:need(abs(a.solid_winding(comp['vertices'],comp['local_triangles'],(box[0]+box[1])/2))<1e-8,'Post box inside source')
  floor_contacts.append({'part':part['id'],'source':comp['object'],'floor_triangles':hit['actual_boundary_triangles']})
# Exact canonical supporting planes, not a BVH coplanar exclusion.
groups=collections.defaultdict(list)
for part in parts:
 for fi,face in enumerate(part['local_faces']):
  poly=[e.fraction3(part['vertices'][i])for i in face];n=a.signed_normal(poly);axis=next(k for k in range(3)if n[k]);scale=n[axis];normal=tuple(x/scale for x in n);offset=sum(normal[k]*poly[0][k]for k in range(3));projection=max(range(3),key=lambda k:abs(normal[k]));other=[k for k in range(3)if k!=projection];projected=[tuple(v[k]for k in other)for v in poly];groups[(normal,offset)].append((part['id'],fi,scale>0,projected))
opposite=[]
for key,faces in groups.items():
 for x,y in itertools.combinations(faces,2):
  if x[0]==y[0]or not e.positive_bbox(e.bounds(x[3]),e.bounds(y[3])):continue
  ar=e.area(e.clip_convex(x[3],y[3]))
  if not ar:continue
  need(x[2]!=y[2],'Exact same-facing exposed/coplanar patch '+x[0]+' / '+y[0]);opposite.append({'a':x[0],'b':y[0],'projected_area':float(ar)})
# Exact-rational segment clipping against actual convex prism halfspaces.
def ray_prism(start,end,part):
 start=list(map(F,start));delta=[F(end[k])-start[k]for k in range(3)];lo=F(0);hi=F(1);constraints=[(start[2]-part['lo'],delta[2]),(part['hi']-start[2],-delta[2])]
 for u,v in zip(part['poly'],part['poly'][1:]+part['poly'][:1]):
  dx=v[0]-u[0];dy=v[1]-u[1];constraints.append((dx*(start[1]-u[1])-dy*(start[0]-u[0]),dx*delta[1]-dy*delta[0]))
 for constant,slope in constraints:
  if slope==0:
   if constant<0:return None
  elif slope>0:lo=max(lo,-constant/slope)
  else:hi=min(hi,-constant/slope)
 return [float(lo),float(hi)]if lo<=hi and hi>0 and lo<1 else None
actual_rays=json.loads((R/'PLAN_PROOF.json').read_text())['finite_sightlines'];rays=[]
for ray in actual_rays:
 hits=[{'part':part['id'],'interval':ray_prism(ray['actual_from'],ray['actual_to'],part)}for part in parts];hits=[x for x in hits if x['interval']is not None];need(not hits,'Actual fittings obstruct fixed ray');rays.append({'view':ray['view'],'target':ray['target'],'clear':True})
near=[]
for name,receipt in p['accepted_view_receipts'].items():
 M=np.array(receipt['camera']['matrix_world']);cam=receipt['camera']['data'];z=cam['clip_start'];w=z*36/(2*26);h=w*694/960;points=np.array([(M@np.array([x,y,-z,1]))[:3]for x in [-w,w]for y in [-h,h]]);box=[points.min(0),points.max(0)];need(all(a.analyze(part,box)['disjoint']for part in parts),'Actual near plane hit');near.append({'view':name,'clear':True})
out={'pass':True,'candidate_sha256':g['candidate_sha256'],'current_scene_components':len(scene),'body_clear':body,'source_contacts_only_proven_floor':floor_contacts,'exact_same_facing_coplanar_patches':0,'opposite_bearing_patches':opposite,'finite_actual_rays':rays,'near_planes':near,'limits':'Actual saved convex fittings. Exact positive-area coincident planes, not BVH exclusion; contacts and internal post/rail embeddings intentional. Finite13rays do not certify full emitters/shadows/pixel area; fixed actual art views pending.'};(D/'CLEARANCE.json').write_text(json.dumps(out,indent=2)+'\n');print('ACTUAL FITTINGS CLEARANCE PASS')
