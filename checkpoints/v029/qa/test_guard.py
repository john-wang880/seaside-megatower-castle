import os
"""Seven bounded negative controls on actual exported inputs/reference predicates. No Blender."""
import json,copy,hashlib
from pathlib import Path
import check_guard as q
P=Path(os.environ['V029_QA_OUTPUT']);R=Path(__file__).resolve().parent;n=json.loads((Path(os.environ['V029_QA_DATA'])/'native.json').read_text());plan=json.loads((Path(os.environ['V029_QA_DATA'])/'guard_plan.json').read_text());r=q.run(n,plan['guard'],plan['cavities']);q.validate_targets(n,plan,r['domains']);results=[]
def reject(name,fn):
 try:fn()
 except RuntimeError as e:results.append({'case':name,'rejected':True,'message':str(e)})
 else:raise RuntimeError('Negative accepted '+name)
g=copy.deepcopy(plan['guard']);g[0][1][0]=23.4;reject('guard ends on cavity instead of enclosing it',lambda:q.margins(g,plan['cavities']))
p=copy.deepcopy(plan);p['targets'][0]['raw_vertex_ids']=p['targets'][0]['raw_vertex_ids'][:-1];reject('omitted target raw vertex',lambda:q.validate_targets(n,p))
coords=copy.deepcopy(r['coordinate_planes']);k,v=next((k,v)for k,v in r['_required_planes']if v==31.440000534057617);coords[k].remove(v);reject('missing actual foundation top plane',lambda:q.require_planes(coords,r['_required_planes']))
cut=copy.deepcopy(plan['cavities']);cut[0][0][2]=28.94;rows=[dict(x,after=x['source'] and not any(q.inside(x['mid'],c)for c in cut))for x in r['_floor_cells']];reject('actual cavity cut extended below intended floor',lambda:q.require_floor(rows))
rows=copy.deepcopy(r['_body_cells']);next(x for x in rows if x['source'])['after']=True;reject('retained solid filling doorway lane',lambda:q.require_air(rows))
reject('duplicate expected oriented boundary rectangle',lambda:q.require_unique(r['_boundaries']+[r['_boundaries'][0]]))
fixture=next(c for c in n['components']if c['object']=='V028 | room 1 rain hood');bad=[[14.7,33.89,31.12],[14.93,34.12,31.22]];reject('actual lamp geometry intruded by changed opening',lambda:q.require(q.non_target_free(fixture,bad),'Existing lamp intersects changed volume'))
(P/'NEGATIVE_CONTROLS.json').write_text(json.dumps({'pass':True,'controls':results,'count':len(results),'limits':'CPU pre-cut plan/actual exported geometry controls, not saved-candidate or native tests.','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n');print('GUARD CONTROLS PASS',len(results))
