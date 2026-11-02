"""Saved fixture/body and finite wall-seating checks, explicit coplanar pairs."""
import json,sys,hashlib
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parent/'principal_hall_qa_v027'))
from check_A_exact import analyze
from continuous_box_cover import box_inside
sys.path.insert(0,str(P));from coplanar_predicate import candidates,contact
n=json.loads((P/'native_geometry.json').read_text());f=json.loads((P/'lit_geometry.json').read_text());r=json.loads((P/'saved_routes.json').read_text());shell=n['meshes'][-1];host={'object':shell['name'],'seed':0,'vertices':shell['vertices'],'local_faces':shell['faces'],'local_triangles':shell['triangles']};htri=np.array(shell['vertices'])[np.array(shell['triangles'])];htri=htri[np.linalg.norm(np.cross(htri[:,1]-htri[:,0],htri[:,2]-htri[:,0]),axis=1)>0]
source=json.loads((P.parent/'principal_hall_v027/A_approach/native.json').read_text());payload=json.loads((P.parent/'v028_receiving_chamber/geometry_builder/geometry_final.json').read_text());targets={(t['object'],t['evaluated_seed']) for t in payload['targets']};neighbors=[c for c in source['components'] if (c['object'],c['seed']) not in targets]+[{'object':q['name'],'seed':0,'vertices':q['vertices'],'local_faces':q['faces'],'local_triangles':q['triangles']} for q in n['meshes'][:-1]]
rows=[];seats=[];contacts=[]
# Numerical plane budget predeclared as two float32 coordinate ULP at local maximum magnitude.
eps=float(2*np.spacing(np.float32(max(abs(x) for m in n['meshes'][-1:] for v in m['vertices'] for x in v))))
for c in f['components']:
 tests=[analyze(c,x['continuous_box']) for x in r['routes_and_camera_proxies']];assert all(t['disjoint'] for t in tests),(c['object'],tests)
 cv=np.asarray(c['vertices']);cb=[cv.min(0).tolist(),cv.max(0).tolist()];nt=[analyze(q,cb) for q in neighbors];assert all(q['disjoint'] for q in nt),(c['object'],[q for q in nt if not q['disjoint']]);rows.append({'object':c['object'],'all_11_continuous_body_near_plane_boxes_disjoint':True,'other_preserved_and_outside_host_components_disjoint':len(nt)})
 if c['object'].endswith('mounting plate'):
  y=34. if 'room 1 ' in c['object'] else 39.;box=[[15.0005,y-.01,30.94],[15.002,y+.01,30.96]];a=box_inside(c,*box);b=box_inside(host,*box);assert a['pass'] and b['pass'];seats.append({'object':c['object'],'plate':a,'saved_local_wall':b})
 tri=np.array(c['vertices'])[np.array(c['local_triangles'])]
 for i,t in enumerate(tri):
  if np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))==0:continue
  for j in candidates(t,htri,eps):
   q=contact(t.tolist(),htri[j].tolist(),eps)
   if q:contacts.append({'fixture':c['object'],'triangle':i,'local_triangle_nonzero_index':j,**q})
assert len(seats)==2
same=[x for x in contacts if x['same_facing']]
out={'pass':not same,'candidate_sha256':f['candidate_sha256'],'architecture_geometry_sha256':hashlib.sha256((P/'native_geometry.json').read_bytes()).hexdigest(),'fixtures':rows,'positive_wall_seats':seats,'coplanar_or_near_coplanar_contacts':contacts,'same_facing_count':len(same),'plane_distance_budget':eps,'budget_basis':'Two float32 ULP at maximum local-shell coordinate, fixed before testing; contact helper separately reports strict1e-7 classification. Positive area cutoff1e-8 from historical controlled clipping predicate.','limits':'Finite positive seat and continuous proxy geometry, not load or global accessibility. Existing fixture self topology/materials copied exactly, not redesigned.'};(P/'saved_fixtures_final.json').write_text(json.dumps(out,indent=2));assert out['pass'],same;print('SAVED FIXTURES PASS',len(contacts),'opposite-facing contacts')
