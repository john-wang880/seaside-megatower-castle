"""CPU actual-payload and mathematical controls; no Blender fixtures."""
import copy,json,hashlib
from pathlib import Path
import check_payload as p
R=p.ROOT;D=Path(__file__).parent;n=json.loads((R/'work/v029_interior_program/native.json').read_text());plan=json.loads((R/'work/v029_interior_program/guard_plan/PLAN.json').read_text());a=json.loads((R/'work/v029_stores/geometry_builder/geometry_diagnostic.json').read_text());rows=[]
def bad(label,change):
 b=copy.deepcopy(a);change(b)
 try:p.run(n,plan,b)
 except (ValueError,RuntimeError) as e:rows.append({'case':label,'rejected':True,'reason':str(e)})
 else:raise RuntimeError('Accepted negative '+label)
bad('local shell vertex shifted into intended doorway',lambda b:b['meshes'][-1]['vertices'][0].__setitem__(0,b['meshes'][-1]['vertices'][0][0]+.01))
bad('missing local boundary face',lambda b:b['meshes'][-1]['faces'].pop())
bad('duplicated local boundary face',lambda b:b['meshes'][-1]['faces'].append(b['meshes'][-1]['faces'][0]))
bad('reversed local boundary orientation',lambda b:b['meshes'][-1]['faces'][0].reverse())
bad('nearest-rounded collapsed partition replaces directed partition',lambda b:[v.__setitem__(2,p.f32(28.9))for m in b['meshes']for v in m['vertices']if v[2]==p.UP])
bad('remote source vertex altered',lambda b:b['meshes'][0]['vertices'][0].__setitem__(0,b['meshes'][0]['vertices'][0][0]+.001))
bad('wrong effective material index',lambda b:b['meshes'][-1].__setitem__('material_index',1))
# Equal-area missing+duplicate regions must not cancel in signed total.
v=[[0,0,0],[1,0,0],[1,1,0],[0,1,0]];ref={(2,p.F(0),1):[[(p.F(0),p.F(0)),(p.F(1),p.F(0)),(p.F(1),p.F(1)),(p.F(0),p.F(1))]]}
try:p.general_validate(v,[(0,1,2),(0,1,2)],ref)
except RuntimeError as e:rows.append({'case':'equal-area missing plus duplicate mathematical cancellation','rejected':True,'reason':str(e)})
else:raise RuntimeError('Cancellation control accepted')
(D/'PAYLOAD_CONTROLS.json').write_text(json.dumps({'pass':True,'count':len(rows),'controls':rows,'scope':'Seven CPU actual exported-payload mutations plus one mathematical area control, not native fixtures.','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n');print('PAYLOAD CONTROLS PASS',len(rows))
