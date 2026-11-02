"""Independent quantized local expected occupancy from actual source triangles and approved plan."""
import json,struct,itertools
from pathlib import Path
import numpy as np
from exact_axis_boundary import facets_from_cells

def f32(x):return struct.unpack('f',struct.pack('f',float(x)))[0]
def boxq(b):return [[f32(x) for x in row] for row in b]
def inside(p,b):return all(b[0][k]<p[k]<b[1][k] for k in range(3))
def winding(c,p):
 t=np.asarray(c['vertices'],float)[np.asarray(c['local_triangles'],int)]-p;a,b,z=t[:,0],t[:,1],t[:,2];la=np.linalg.norm(a,axis=1);lb=np.linalg.norm(b,axis=1);lz=np.linalg.norm(z,axis=1);den=la*lb*lz+np.einsum('ij,ij->i',a,b)*lz+np.einsum('ij,ij->i',b,z)*la+np.einsum('ij,ij->i',z,a)*lb
 return float(np.sum(2*np.arctan2(np.einsum('ij,ij->i',a,np.cross(b,z)),den))/(4*np.pi))
def build(export,proof):
 targets={'V012 | foundation with continuous L-shaped passage':128,'V012 | ashlar with bounded entrance and north stairwell':13132,'V012 | hall east stone lining':0};hosts=[c for c in export['components'] if targets.get(c['object'])==c['seed']];assert len(hosts)==3
 G=[boxq(b) for b in proof['guard_union']];C=boxq([[7,32.5,29],[15,40.5,32.05]]);D=boxq(proof['opening_unchanged']);L=boxq(proof['proposed_sleeve']);retained=[boxq(b) for b in proof['retained_solids']]
 coords=[sorted(set(f32(v) for v in row)) for row in proof['coordinate_planes']];occupied=set();count=0;maxres=0
 for idx in itertools.product(*(range(len(row)-1) for row in coords)):
  mid=np.array([(coords[k][idx[k]]+coords[k][idx[k]+1])/2 for k in range(3)])
  if not any(inside(mid,b) for b in G):continue
  count+=1;votes=[]
  for c in hosts:
   w=winding(c,mid);res=min(abs(w),abs(abs(w)-1));maxres=max(maxres,res);assert res<1e-8;votes.append(abs(w)>.5)
  cut=(inside(mid,C) or inside(mid,D)) and not any(inside(mid,b) for b in retained)
  if (any(votes) or inside(mid,L)) and not cut:occupied.add(idx)
 aliases=[{'nominal':row,'saved_unique':coords[k],'collapsed_intervals':len(row)-len(coords[k]),'max_rounding_displacement':max(abs(f32(v)-v) for v in row)} for k,row in enumerate(proof['coordinate_planes'])]
 return facets_from_cells(coords,occupied),{'quantized_cell_count':count,'occupied_cells':len(occupied),'max_winding_residual':maxres,'plane_quantization':aliases,'scope':'Expected saved float32 grid, not claim of exact nominal decimal geometry.'}
