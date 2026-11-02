"""Independent remote-polygon and exact saved-coordinate clipped-domain/cap audit."""
import argparse,json,hashlib,itertools
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction as F
import numpy as np
from axis_reference import f32,boxq,inside,winding
from exact_axis_boundary import validate,signed_area
from planar_triangulation import triangulate

def point_polygon(p,poly):
 inside_=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:inside_=not inside_
 return inside_
def poly_ref(vertices,face,G):
 p=[vertices[i] for i in face];axis=next(k for k in range(3) if all(x[k]==p[0][k] for x in p));other=[k for k in range(3) if k!=axis];uv=[tuple(F(x[k]) for k in other) for x in p];sgn=(1 if signed_area(uv)>0 else -1)*(-1 if axis==1 else 1)
 coords=[sorted(set([x[k] for x in p]+[b[e][k] for b in G for e in (0,1) if min(x[k] for x in p)<b[e][k]<max(x[k] for x in p)])) for k in other];refs=[]
 for i,j in itertools.product(range(len(coords[0])-1),range(len(coords[1])-1)):
  lo=(F(coords[0][i]),F(coords[1][j]));hi=(F(coords[0][i+1]),F(coords[1][j+1]));mid=[(lo[k]+hi[k])/2 for k in range(2)];q=[F(0)]*3;q[axis]=F(p[0][axis]);q[other[0]],q[other[1]]=mid
  if point_polygon(mid,uv) and not any(inside(q,b) for b in G):refs.append((lo,hi))
 return {(axis,F(p[0][axis]),sgn):refs}
def domain(mesh,ids,refs):
 tris=[t for i in ids for t in triangulate(mesh['vertices'],mesh['faces'][i])]
 return validate(mesh['vertices'],tris,(refs,None))
def cap_ref(host,G,coords):
 cells=set();ing=set()
 for idx in itertools.product(*(range(len(r)-1) for r in coords)):
  mid=np.array([(coords[k][idx[k]]+coords[k][idx[k]+1])/2 for k in range(3)])
  if not any(inside(mid,b) for b in G):continue
  ing.add(idx);w=winding(host,mid);assert min(abs(w),abs(abs(w)-1))<1e-8
  if abs(w)>.5:cells.add(idx)
 refs=defaultdict(list)
 for idx in cells:
  for axis in range(3):
   for s in (-1,1):
    adj=list(idx);adj[axis]+=s
    if tuple(adj) in ing:continue
    other=[k for k in range(3) if k!=axis];plane=F(coords[axis][idx[axis]+(s>0)]);lo=tuple(F(coords[k][idx[k]]) for k in other);hi=tuple(F(coords[k][idx[k]+1]) for k in other);refs[(axis,plane,-s)].append((lo,hi))
 return dict(refs)
def run(payload,export,proof,faces):
 G=[boxq(b) for b in proof['guard_union']];coords=[sorted(set(f32(v) for v in row)) for row in proof['coordinate_planes']];rows=[];remote_total=0
 for m,target in zip(payload['meshes'][:3],payload['targets']):
  name=target['object'];seed=target['evaluated_seed'];h=next(c for c in export['components'] if c['object']==name and c['seed']==seed);spec=next(t for t in faces['targets'] if t['object']==name);affected={a['source_face']:a['local_face'] for a in spec['affected']};original={f['id']:i for i,f in enumerate(h['faces'])};seen=[];remote=[]
  for i,l in enumerate(m['face_lineage']):
   if l['kind']=='remote_original':
    fid=l['source_face'];assert l['source_object']==name and fid not in affected and fid not in seen;seen.append(fid)
    actual=[m['vertices'][j] for j in m['faces'][i]];expected=[h['vertices'][j] for j in h['local_faces'][original[fid]]];assert actual==expected,('remote changed',name,fid);remote.append(fid)
  assert set(remote)==set(original)-set(affected);remote_total+=len(remote)
  domains=[]
  for fid,local in affected.items():
   ids=[i for i,l in enumerate(m['face_lineage']) if l['kind']=='clipped_source_domain' and l['source_face']==fid and l['source_object']==name];assert ids
   result=domain(m,ids,poly_ref(h['vertices'],h['local_faces'][local],G));domains.append({'source_face':fid,**result})
  ids=[i for i,l in enumerate(m['face_lineage']) if l['kind']=='buried_guard_cap'];caps=domain(m,ids,cap_ref(h,G,coords))
  assert len(remote)+sum(l['kind']=='clipped_source_domain' for l in m['face_lineage'])+len(ids)==len(m['faces'])
  edges=Counter((a,b) for f in m['faces'] for a,b in zip(f,f[1:]+f[:1]));assert all(n==1 and edges[(b,a)]==1 for (a,b),n in edges.items()),('edge incidence',name)
  rows.append({'object':name,'remote_polygons_exact':len(remote),'affected_domains':domains,'guard_caps':caps,'closed_oriented_edges':True})
 assert remote_total==112
 return {'pass':True,'remote_polygons_exact':remote_total,'hosts':rows,'scope':'Exact saved-float boundary-domain equality and oriented closure. Native evaluated attributes and source rollback remain separate pending gates.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--payload',required=True);p.add_argument('--export',required=True);p.add_argument('--proof',required=True);p.add_argument('--faces',required=True);p.add_argument('--report',required=True);a=p.parse_args();paths=[a.payload,a.export,a.proof,a.faces];r=run(*(json.load(open(x)) for x in paths));r['inputs']={x:hashlib.sha256(Path(x).read_bytes()).hexdigest() for x in paths};out=Path(a.report);assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n');print('OUTSIDE DOMAIN PASS',r['remote_polygons_exact'])
