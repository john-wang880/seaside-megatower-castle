"""Verify native derived triangles exactly cover each affected/new saved planar parent.
Exact-zero derived triangles are recorded and excluded only after parent coverage proof.
Remote original polygons have already been preserved as exact oriented coordinate records.
"""
import argparse,json,hashlib
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
from exact_axis_boundary import area,clip_convex,bounds,positive_bbox,validate,cross,fraction3
from planar_triangulation import triangulate
from axis_reference import build

def audit(mesh):
 rows=[];zero=[];nonzero=[]
 for fi,face in enumerate(mesh['faces']):
  ids=[i for i,p in enumerate(mesh['triangle_polygons']) if p==fi]
  if mesh['face_lineage'][fi]['kind']=='remote_original':continue
  expected=triangulate(mesh['vertices'],face);points=[mesh['vertices'][i] for i in face];axis=next(k for k in range(3) if all(p[k]==points[0][k] for p in points));other=[k for k in range(3) if k!=axis]
  def project(t):return [tuple(F(mesh['vertices'][i][k]) for k in other) for i in t]
  ears=[project(t) for t in expected];actual=[]
  for ti in ids:
   t=mesh['triangles'][ti];poly=project(t);a=area(poly)
   if a==0:
    p=[fraction3(mesh['vertices'][i]) for i in t];n=cross(tuple(p[1][k]-p[0][k] for k in range(3)),tuple(p[2][k]-p[0][k] for k in range(3)));assert not any(n)
    zero.append({'triangle':ti,'parent':fi,'coordinates':[mesh['vertices'][i] for i in t]});continue
   assert sum((area(clip_convex(poly,e)) for e in ears),F(0))==a,('native triangle outside parent',fi,ti)
   actual.append((ti,poly));nonzero.append(t)
  for j,(ti,p) in enumerate(actual):
   for tj,q in actual[j+1:]:
    assert not positive_bbox(bounds(p),bounds(q)) or area(clip_convex(p,q))==0,('native multiple coverage',fi,ti,tj)
  assert sum((area(p) for _,p in actual),F(0))==sum((area(e) for e in ears),F(0)),('native parent gap',fi)
  rows.append({'parent':fi,'triangles':len(ids),'positive_area':float(sum((area(e) for e in ears),F(0)))})
 return {'pass':True,'parents_checked':len(rows),'exact_zero_triangles':zero,'uncovered_area':0,'multiply_covered_area':0,'outside_area':0},nonzero
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for k in ('geometry','export','proof','report'):p.add_argument('--'+k,required=True)
 a=p.parse_args();d=json.loads(Path(a.geometry).read_text());results=[]
 for m in d['meshes']:
  r,t=audit(m)
  if m['name']=='V028 | local receiving chamber shell':r['actual_native_boundary']=validate(m['vertices'],t,build(json.loads(Path(a.export).read_text()),json.loads(Path(a.proof).read_text()))[0])
  results.append({'name':m['name'],**r})
 out={'pass':True,'candidate_sha256':d['candidate_sha256'],'geometry_sha256':hashlib.sha256(Path(a.geometry).read_bytes()).hexdigest(),'meshes':results,'limits':'Remote original parent records separately exact; zero derived triangles carry no surface area and are not saved-face removals.'};assert not Path(a.report).exists();Path(a.report).write_text(json.dumps(out,indent=2));print('NATIVE TESSELLATION PASS',sum(len(x['exact_zero_triangles']) for x in results),'exact-zero derived triangles')
