import os
"""Exported actual local geometry negatives; not native model mutations."""
import json,copy,hashlib
from pathlib import Path
from axis_reference import build
from exact_axis_boundary import validate
from planar_triangulation import triangulate
P=Path(os.environ['V028_QA_OUTPUT']);DATA=Path(os.environ['V028_QA_DATA']);path=DATA/'geometry_final.json';d=json.loads(path.read_text());m=d['meshes'][-1];ref,_=build(json.loads((DATA/'native.json').read_text()),json.loads((DATA/'guard_partition_proof.json').read_text()))
def check(v,faces):return validate(v,[t for f in faces for t in triangulate(v,f)],ref)
assert check(m['vertices'],m['faces'])['pass'];cases=[]
def reject(name,v,faces):
 try:check(v,faces)
 except (ValueError,AssertionError) as e:cases.append({'name':name,'rejected':True,'reason':str(e)[:250]})
 else:raise RuntimeError('Negative accepted: '+name)
reject('missing_actual_wall_polygon',m['vertices'],m['faces'][1:]);reject('duplicate_actual_wall_polygon',m['vertices'],m['faces']+m['faces'][:1]);f=copy.deepcopy(m['faces']);f[0].reverse();reject('reverse_actual_wall_orientation',m['vertices'],f)
v=copy.deepcopy(m['vertices']);
for p in v:
 if p[2]==29.:p[2]=29.125
reject('raise_actual_room_floor',v,m['faces'])
v=copy.deepcopy(m['vertices']);v[0][0]+=.125;reject('displace_actual_guard_seam',v,m['faces'])
# Closed room AABB destroys the real doorway/recess/pier protected surface partition.
v=[[x,y,z] for z in (28.9,32.15) for y in (32.4,40.6) for x in (6.9,15.1)];f=[[0,2,3,1],[4,5,7,6],[0,1,5,4],[1,3,7,5],[3,2,6,7],[2,0,4,6]];reject('bounding_box_fills_actual_room_and_door_void',v,f)
out={'pass':True,'payload_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'controls':cases,'scope':'Six altered copies of exported actual geometry, not six Blender fixture runs.'};(P/'actual_payload_controls.json').write_text(json.dumps(out,indent=2));print('SIX ACTUAL PAYLOAD NEGATIVES PASS')
