"""Pure-Python independent affine triangle-overlay proof, no Blender/model writes."""
import json,math,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;D=P.parent/'path_arrival_v022';survey=json.loads((D/'survey.json').read_text());terrain=json.loads((D/'local_terrain_triangles.json').read_text());coverage=json.loads((D/'coverage.json').read_text());source=survey['source_sha256'];assert terrain['source_sha256']==coverage['source_sha256']==source

def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def sub(a,b):return(a[0]-b[0],a[1]-b[1])
def area(p):return abs(sum(cross(sub(p[i],p[0]),sub(p[i+1],p[0]))for i in range(1,len(p)-1)))/2 if len(p)>=3 else 0.
def signed(p):return sum(cross(sub(p[i],p[0]),sub(p[i+1],p[0]))for i in range(1,len(p)-1))/2

def halfplane(poly,fn):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  fa,fb=fn(a),fn(b)
  if fa>=0:out.append(a)
  if (fa>=0)!=(fb>=0):
   t=fa/(fa-fb);out.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])))
 return out

def clip(poly,window):
 if signed(window)<0:window=window[::-1]
 for a,b in zip(window,window[1:]+window[:1]):
  d=sub(b,a);poly=halfplane(poly,lambda p:cross(d,sub(p,a)))
  if len(poly)<3:return[]
 return poly

def plane(t):
 a,b,c=t;u=sub(b,a);v=sub(c,a);det=cross(u,v);assert abs(det)>1e-12
 gx=((b[2]-a[2])*v[1]-(c[2]-a[2])*u[1])/det;gy=(u[0]*(c[2]-a[2])-v[0]*(b[2]-a[2]))/det
 return lambda p:a[2]+gx*(p[0]-a[0])+gy*(p[1]-a[1])

def bounds(t):return [min(v[0]for v in t),min(v[1]for v in t),max(v[0]for v in t),max(v[1]for v in t)]
T=[]
for row in terrain['triangles']:
 t=row['coords'];T.append((row['triangle'],[(v[0],v[1])for v in t],bounds(t),plane(t)))
faces={f['id']:f for f in survey['path']['faces']};verts=survey['path']['vertices'];rows=[];total=buried=0.;low=float('inf');high=-float('inf');max_coverage_error=0.;max_overlap=0.
for previous in coverage['faces']:
 f=faces[previous['face']];assert len(f['vertices'])==3;t=[verts[i]for i in f['vertices']];p=[tuple(v[:2])for v in t];pb=bounds(t);pz=plane(t);pieces=[];covered=bur=0.;gaps=[]
 for tid,xy,tb,tz in T:
  if pb[0]>tb[2]or tb[0]>pb[2]or pb[1]>tb[3]or tb[1]>pb[3]:continue
  poly=clip(p,xy);aa=area(poly)
  if aa<=1e-13:continue
  gap=lambda q:pz(q)-tz(q);values=[gap(q)for q in poly];negative=halfplane(poly,lambda q:-gap(q));ba=area(negative);pieces.append({'terrain_triangle':tid,'polygon':poly,'area':aa,'min_gap':min(values),'max_gap':max(values),'buried_area':ba});covered+=aa;bur+=ba;gaps.extend(values)
 ar=area(p);error=abs(covered-ar);assert error<1e-7,(f['id'],error);max_coverage_error=max(max_coverage_error,error)
 for i,a in enumerate(pieces):
  for b in pieces[i+1:]:
   overlap=area(clip(a['polygon'],b['polygon']));max_overlap=max(max_overlap,overlap);assert overlap<1e-9,(f['id'],overlap)
 assert abs(bur-previous['terrain_covered_area'])<1e-7,(f['id'],bur,previous['terrain_covered_area'])
 row={'face':f['id'],'material_index':f['material_index'],'plan_area':ar,'buried_area':bur,'min_full_face_gap':min(gaps),'max_full_face_gap':max(gaps),'terrain_piece_count':len(pieces)};rows.append(row);total+=ar;buried+=bur;low=min(low,min(gaps));high=max(high,max(gaps))
result={'pass':True,'source_sha256':source,'method':'Independent double-precision convex polygon clipping; affine pathZ−terrainZ extrema at every overlay polygon vertex. Buried region is exact affine halfplane clip, not vertex/centroid sampling. Actual source pathfaces are triangles. Per-face full coverage plus pairwise no-positive-area overlap checked. Planimetric area only, not camera pixels.','faces':rows,'summary':{'face_count':len(rows),'plan_area':total,'buried_area':buried,'buried_fraction':buried/total,'minimum_full_face_gap':low,'maximum_full_face_gap':high,'maximum_partition_area_error':max_coverage_error,'maximum_overlay_piece_overlap_area':max_overlap},'input_hashes':{n:hashlib.sha256((D/n).read_bytes()).hexdigest()for n in ['survey.json','coverage.json','local_terrain_triangles.json']},'limits':'Exported bounded single terrain heightfield only; actual candidate/clean boundary and additional visible geometry still need separate scene validation.'};(P/'source_overlay.json').write_text(json.dumps(result,indent=2));print(json.dumps(result['summary'],indent=2))
