import os
"""Continuous saved-geometry route boxes and proposed view near-plane/body proxies."""
import json,sys,hashlib,math
from pathlib import Path
P=Path(os.environ['V028_QA_OUTPUT']);DATA=Path(os.environ['V028_QA_DATA']);sys.path.insert(0,str(Path(__file__).resolve().parent))
from body_support import analyze
n=json.loads((P/'native_geometry.json').read_text());s=json.loads((DATA/'native.json').read_text());p=json.loads((DATA/'geometry_final.json').read_text());targets={(t['object'],t['evaluated_seed']) for t in p['targets']};comps=[c for c in s['components'] if (c['object'],c['seed']) not in targets]
for m in n['meshes']:comps.append({'object':m['name'],'seed':0,'vertices':m['vertices'],'local_faces':m['faces'],'local_triangles':m['triangles']})
route=json.loads((P/'route_fixture_plan.json').read_text());boxes={r['name']:r['swept_body_box'] for r in route['route_boxes']};boxes.update(entry_shift=[[3.85,36.9,29.025],[5.05,38.6,31.1]],entry_east=[[3.85,36.9,29.025],[8.2,38.1,31.1]])
views={'primary':{'eye':[5.9,37.5,30.65],'aim':[13,36.7,30.65]},'secondary':{'eye':[13.7,39.5,30.65],'aim':[8,35.8,30.45]}}
radius=math.sqrt(.05**2+(.05*36/26/2)**2+(.05*36/26/2*694/960)**2)
for name,v in views.items():
 e=v['eye'];boxes[name+'_near_sphere_AABB']=[[x-radius for x in e],[x+radius for x in e]];boxes[name+'_body']=[[e[0]-.6,e[1]-.6,29.025],[e[0]+.6,e[1]+.6,31.1]]
results=[]
for name,b in boxes.items():
 rows=[analyze(c,b) for c in comps];bad=[r for r in rows if not r['disjoint']];assert not bad,(name,bad);results.append({'name':name,'continuous_box':b,'components_checked':len(rows),'actual_triangle_and_closed_containment_disjoint':True})
out={'pass':True,'candidate_sha256':n['candidate_sha256'],'routes_and_camera_proxies':results,'view_design':views,'near_plane_enclosing_radius':radius,'camera_settings':{'lens':26,'sensor_width':36,'resolution':[960,694],'clip_start':.05},'limits':'Continuous axis-aligned body/near-plane proxies only. No full-floor accessibility, human gait, whole frustum visibility, or rendered camera metadata claim. Unchanged old components covered by exact source proof and bounded complete export; new meshes use saved native loop triangles.'};(P/'saved_routes.json').write_text(json.dumps(out,indent=2));print('SAVED ROUTES AND CAMERA PROXIES PASS',len(results))
