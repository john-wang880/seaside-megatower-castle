import os
"""Exact rational oriented-volume conservation of each whole outside-host replacement."""
import json,itertools,hashlib
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from axis_reference import boxq,f32,inside,winding
from exact_axis_boundary import cross,fraction3
P=Path(os.environ['V028_QA_OUTPUT']);DATA=Path(os.environ['V028_QA_DATA']);n=json.loads((P/'native_geometry.json').read_text());d=json.loads((DATA/'native.json').read_text());plan=json.loads((DATA/'geometry_final.json').read_text());proof=json.loads((DATA/'guard_partition_proof.json').read_text());G=[boxq(b) for b in proof['guard_union']];coords=[sorted(set(f32(x) for x in row)) for row in proof['coordinate_planes']]
def volume(v,tris):
 v=[fraction3(p) for p in v];origin=v[0];result=F(0)
 for t in tris:
  p=[tuple(v[i][k]-origin[k] for k in range(3)) for i in t];normal=cross(p[1],p[2]);result+=sum(p[0][k]*normal[k] for k in range(3))/6
 return result
rows=[]
for m,t in zip(n['meshes'][:3],plan['targets']):
 c=next(c for c in d['components'] if c['object']==t['object'] and c['seed']==t['evaluated_seed']);old=volume(c['vertices'],c['local_triangles']);new=volume(m['vertices'],m['triangles']);inside_v=F(0)
 for idx in itertools.product(*(range(len(row)-1) for row in coords)):
  mid=np.array([(coords[k][idx[k]]+coords[k][idx[k]+1])/2 for k in range(3)])
  if any(inside(mid,g) for g in G) and abs(winding(c,mid))>.5:inside_v+=np.prod([F(coords[k][idx[k]+1])-F(coords[k][idx[k]]) for k in range(3)])
 assert new==old-inside_v and new>0,(m['name'],str(new-old+inside_v));rows.append({'name':m['name'],'source_volume':float(old),'removed_source_inside_quantized_guard':float(inside_v),'saved_outside_volume':float(new),'exact_rational_difference':str(new-old+inside_v)})
(P/'outside_volumes.json').write_text(json.dumps({'pass':True,'candidate_sha256':n['candidate_sha256'],'rows':rows,'limits':'Oriented volume per original host separately, not sum as union volume where original hosts overlap.'},indent=2));print('EXACT OUTSIDE VOLUME PASS')
