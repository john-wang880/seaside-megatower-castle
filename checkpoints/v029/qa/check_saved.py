import os
"""Saved triangulation, actual fixture seats/body and camera-clearance gate."""
import json,hashlib,sys
from pathlib import Path
import numpy as np
import check_payload as p
import check_guard as q
sys.path.insert(0,str(p.ROOT))
from check_native_tessellation import audit
D=Path(os.environ['V029_QA_OUTPUT']);n=json.loads((Path(os.environ['V029_QA_DATA'])/'native.json').read_text());plan=json.loads((Path(os.environ['V029_QA_DATA'])/'fixture_plan.json').read_text());geo=json.loads((D/'saved_geometry.json').read_text());fixtures=json.loads((D/'saved_fixtures.json').read_text());payload=json.loads((Path(os.environ['V029_QA_DATA'])/'payload.json').read_text());guard=json.loads((Path(os.environ['V029_QA_DATA'])/'guard_plan.json').read_text())
proof=[]
for mesh,spec in zip(geo['meshes'],payload['meshes']):
 q.require(mesh['name']==spec['name'] and mesh['vertices']==spec['vertices'] and mesh['faces']==spec['faces'],'Saved payload mismatch');r,_=audit(mesh);proof.append({'name':mesh['name'],**r})
p.run(n,guard,payload)
new=[{'object':m['name'],'seed':0,'vertices':m['vertices'],'local_faces':m['faces'],'local_triangles':m['triangles']}for m in geo['meshes']];local=new[-1];seats=[];body=[[14.6,35.6,29.025],[23.3,36.8,31.1]]
for record in plan['lamps']:
 plate=next(c for c in fixtures['components']if c['object']=='V029 | stores '+record['id']+' mounting plate');box=record['positive_plate_source_seat_box'];a=q.box_inside(plate,*box);b=q.box_inside(local,*box);q.require(a['pass']and b['pass'],'Saved positive wall seat');seats.append({'id':record['id'],'plate':a,'saved_wall':b})
all_actual=[c for c in n['components']if c['object']not in q.NAMES]+new+fixtures['components'];q.require(all(q.analyze(c,body)['disjoint']for c in all_actual),'Actual axial body obstruction');near=[]
for v in plan['views']:
 M=np.array(v['reference_matrix']);d=v['camera_data']['clip_start'];w=d*36/52;h=w*694/960;corners=np.array([(M@np.array([x,y,-d,1]))[:3]for x in [-w,w]for y in [-h,h]]);box=[corners.min(0),corners.max(0)];q.require(all(q.analyze(c,box)['disjoint']for c in all_actual),'Actual camera near plane collision');near.append({'view':v['key'],'actual_near_plane_clear':True})
r={'pass':True,'candidate_sha256':geo['candidate_sha256'],'parents':proof,'saved_plate_wall_seats':seats,'actual_axial_body_clear':body,'actual_camera_near_planes':near,'input_sha256':{x:hashlib.sha256((D/x).read_bytes()).hexdigest()for x in ['saved_geometry.json','saved_fixtures.json','SAVED_PRESERVATION.json']},'limits':'Full quantized floor/route expected-boundary proof applies through exact saved payload equality; actual native triangulation coverage independently checked. No rendered or global navigation claim.'};(D/'SAVED_GEOMETRY_PROOF.json').write_text(json.dumps(r,indent=2)+'\n');print('SAVED GEOMETRY PASS')
