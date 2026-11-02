import os
"""Actual saved, camera-facing pier surface footprints; no camera search."""
import json,itertools
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from exact_axis_boundary import clip_rect,area
from axis_reference import f32
P=Path(os.environ['V028_QA_OUTPUT']);DATA=Path(os.environ['V028_QA_DATA']);r=json.loads((P/'reverse_correction.json').read_text());n=json.loads((P/'native_geometry.json').read_text());m=n['meshes'][-1];E=np.array(r['eye_float32']);A=np.array(r['aim_float32']);fw=(A-E)/np.linalg.norm(A-E);rt=np.cross(fw,[0,0,1]);rt/=np.linalg.norm(rt);up=np.cross(rt,fw);scale=960*26/36
v=np.array(m['vertices']);tris=v[np.array(m['triangles'])];rows=[]
def project(p):
 q=np.array(p)-E;d=q@fw;return (F(float(480+q@rt/d*scale)),F(float(347-q@up/d*scale)))
for name,yrange in [('south',[34.6,35.4]),('north',[38.2,39.])]:
 low=[f32(10.6),f32(yrange[0]),29.];high=[f32(11.4),f32(yrange[1]),f32(31.8)];pieces=[]
 for ti,t in enumerate(tris):
  norm=np.cross(t[1]-t[0],t[2]-t[0])
  if np.linalg.norm(norm)==0 or np.dot(norm,E-t.mean(0))<=0:continue
  axes=[k for k in (0,1) if np.all(t[:,k]==t[0,k]) and t[0,k] in (low[k],high[k])]
  if not axes:continue
  axis=axes[0];other=[k for k in range(3) if k!=axis];poly=clip_rect([tuple(F(float(q[k])) for k in other) for q in t],tuple(F(low[k]) for k in other),tuple(F(high[k]) for k in other))
  if not area(poly):continue
  points=[]
  for q in poly:
   p=[0.,0.,0.];p[axis]=t[0,axis]
   for k,value in zip(other,q):p[k]=float(value)
   points.append(project(p))
  clipped=clip_rect(points,(F(0),F(0)),(F(960),F(694)))
  if area(clipped):pieces.append({'native_triangle':ti,'axis':axis,'plane':float(t[0,axis]),'screen_polygon':[[float(x),float(y)] for x,y in clipped],'pixel_area':float(area(clipped))})
 assert pieces;arr=np.array([p for row in pieces for p in row['screen_polygon']]);rows.append({'pier':name,'actual_camera_facing_surface_patches':pieces,'clipped_screen_bounds':[arr.min(0).tolist(),arr.max(0).tolist()],'sum_projected_patch_area_pixels':sum(q['pixel_area'] for q in pieces),'image_area_fraction':sum(q['pixel_area'] for q in pieces)/(960*694)})
out={'candidate_sha256':r['candidate_sha256'],'camera':{'eye':r['eye_float32'],'aim':r['aim_float32']},'actual_saved_pier_surface_footprints':rows,'limits':'Projected clipped actual facing triangles of each retained pier below roof band, not AABB projection. Patch-area sum is a projected framing metric before other-object occlusion, not pixel segmentation or artistic acceptance; doorway continuous visibility separately proved.'};(P/'reverse_pier_footprints.json').write_text(json.dumps(out,indent=2));print([(x['pier'],x['clipped_screen_bounds'],x['image_area_fraction']) for x in rows])
