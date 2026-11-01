import json,numpy as np,hashlib
from pathlib import Path
from geometry_checks import *
R=Path(__file__).resolve().parent;g=json.loads((R/'geometry.json').read_text());s=json.loads((R/'solid_contacts.json').read_text());name='V027 | single oblique lower rock buttress';d=g['objects'][name];v=np.array(d['vertices']);t=np.array(d['triangles']);rows=[]
assert topology(v,t[:-1])[0]['bad_oriented_edges'];rows.append({'case':'missing_saved_triangle','rejected_by':'directed edge closedness'})
x=t.copy();x[0]=x[0][::-1];assert topology(v,x)[0]['bad_oriented_edges'];rows.append({'case':'reversed_saved_triangle','rejected_by':'directed edge orientation'})
x=np.vstack([t,t[0]]);assert self_intersections(v,x)['positive_area_coplanar_overlaps'];rows.append({'case':'duplicated_actual_triangle','rejected_by':'explicit positive-area coplanar clipping'})
# Deliberate crossing face through an actual original triangle interior.
a=v[t[0]];c=a.mean(0);normal=np.cross(a[1]-a[0],a[2]-a[0]);normal/=np.linalg.norm(normal);cross=np.array([c-normal,c+normal,(c+a[1])/2+normal]);assert pair_crossings(a,cross);rows.append({'case':'foreign_triangle_through_actual_face','rejected_by':'direct segment/triangle interior intersection'})
cliff=g['objects']['V002 | western headland with solid rock shore'];ct=np.array(cliff['vertices'])[cliff['triangles']];delta=np.array([0,100,0]);states=[]
for w in s['above_water_attachment_witnesses']:
 p=np.array(w['point'])+delta;own=inside(p,(v+delta)[t]);old=inside(p,ct);assert own['state']=='inside' and old['state']=='outside';states.append({'new':own,'source':old})
rows.append({'case':'detached_translation_100Y','rejected_by':'all previously proven positive overlap witnesses outside actual source and envelope','witness_states':states})
plan=json.loads((R.parent/'v027_far_buttress/plan.json').read_text());bad=v.copy();bad[0,0]=plan['bounds'][0][0]-1;assert np.any(bad<np.array(plan['bounds'][0]));rows.append({'case':'out_of_reviewed_envelope','rejected_by':'actual coordinate bounds'})
r={'pass':True,'geometry_sha256':hashlib.sha256((R/'geometry.json').read_bytes()).hexdigest(),'controls':rows,'scope':'Six pure actual-exported-geometry controls; not Blender model mutations. Detached witness rejection is bounded to tested contact evidence, not a global search theorem.'};(R/'actual_geometry_controls.json').write_text(json.dumps(r,indent=2));print('6 actual geometry controls PASS')
