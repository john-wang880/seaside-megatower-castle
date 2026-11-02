"""Actual exported-geometry and contact predicate negatives; no native mutation claims."""
import copy,json
from pathlib import Path
import audit_geometry as a
D=Path(__import__('os').environ['FITTINGS_QA_OUTPUT']);data=json.loads((D/'geometry.json').read_text());plan=json.loads((a.R/'PLAN.json').read_text());rows=[]
def reject(label,mutate):
 d=copy.deepcopy(data);mutate(d)
 try:a.audit(d,plan)
 except (RuntimeError,ValueError)as e:rows.append({'case':label,'rejected':True,'reason':str(e)})
 else:raise RuntimeError('Control accepted '+label)
reject('raised foot retains closed form but loses actual floor contact',lambda d:[v.__setitem__(2,v[2]+.01)for v in d['meshes'][0]['vertices'][:16]])
reject('chamfer loss moved corner to original box corner',lambda d:d['meshes'][0]['vertices'][0].__setitem__(0,plan['primitive_parts'][0]['min'][0]))
reject('missing actual parent face',lambda d:d['meshes'][0]['faces'].pop())
reject('reversed actual parent orientation',lambda d:d['meshes'][0]['faces'][0].reverse())
reject('duplicated component ownership',lambda d:d['meshes'][0]['components'].append(d['meshes'][0]['components'][0]))
bin_index=next(i for i,m in enumerate(data['meshes'])if 'supply bin' in m['name']);reject('floating lid shifted from body seat',lambda d:[v.__setitem__(2,v[2]+.01)for v in d['meshes'][bin_index]['vertices'][16:32]])
poly=[(a.F(0),a.F(0)),(a.F(1),a.F(0)),(a.F(1),a.F(1)),(a.F(0),a.F(1))];half=poly[:3]
try:a.coverage(poly,[half,half])
except RuntimeError as e:rows.append({'case':'equal-area bearing hole plus duplicate cannot cancel','rejected':True,'reason':str(e)})
else:raise RuntimeError('Compensating bearing defect accepted')
(D/'GEOMETRY_CONTROLS.json').write_text(json.dumps({'pass':True,'controls':rows,'count':len(rows),'scope':'Six actual saved-export mutations plus one mathematical bearing-coverage control, not native candidate edits.'},indent=2)+'\n');print('SEVEN GEOMETRY CONTROLS PASS')
