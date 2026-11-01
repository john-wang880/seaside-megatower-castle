"""Actual triangle projected occlusion along west-to-east +X, not perspective render."""
from pathlib import Path
exec(compile(Path(__file__).resolve().with_name('validate_technical.py').read_text().split('rows=[];')[0],'geometry_initialization','exec'))
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def area(poly):return sum(cross(poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly)))/2
def intersection_area(subject,clip):
 if area(clip)<0:clip=clip[::-1]
 poly=subject
 for i,u in enumerate(clip):
  v=clip[(i+1)%3];edge=(v[0]-u[0],v[1]-u[1]);old=poly;poly=[]
  if not old:break
  for j,p in enumerate(old):
   q=old[(j+1)%len(old)];dp=cross(edge,(p[0]-u[0],p[1]-u[1]));dq=cross(edge,(q[0]-u[0],q[1]-u[1]))
   if dp>=0:poly.append(p)
   if (dp>=0)!=(dq>=0):t=dp/(dp-dq);poly.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
 return abs(area(poly)) if len(poly)>=3 else 0
def front_triangles(s):
 x=s['bounds'][0][0];return [[(s['vertices'][i][1],s['vertices'][i][2]) for i in t] for t in s['triangles'] if all(abs(s['vertices'][i][0]-x)<1e-6 for i in t)]
ct=front_triangles(cornice);assert len(ct)==2;rows=[]
for s in components('V020 candidate | west portal radial stones'):
 tri=front_triangles(s);total=sum(abs(area(t)) for t in tri);covered=sum(intersection_area(t,c) for t in tri for c in ct) if cornice['bounds'][0][0]<s['bounds'][0][0] else 0.0;assert total>0 and -1e-9<=covered<=total+1e-9;rows.append({'piece':s['key'],'front_face_area_m2':total,'covered_by_actual_cornice_front_m2':covered,'west_orthographic_covered_fraction':covered/total})
coplanar=[]
arch=components('V020 candidate | west portal radial stones')
front_records=[(piece['key'],tri) for piece in arch for tri in front_triangles(piece)]
for i,(name,tri) in enumerate(front_records):
 for other,triangle in front_records[i+1:]:
  amount=intersection_area(tri,triangle)
  if amount>1e-10:coplanar.append({'pieces':[name,other],'duplicate_front_triangle_area_m2':amount})
r={'remaining_duplicate_front_triangle_patches':coplanar,'candidate_sha256':before,'source_cornice':cornice['key'],'cornice_front_x':cornice['bounds'][0][0],'pieces':rows,'scope':'Actual front triangle projected union against nearer measured cornice face along +X. Exact planar clipping up to floating arithmetic; not practical-camera or full perspective visibility proof.','candidate_unchanged':sha(a.candidate)==before};Path(a.report).write_text(json.dumps(r,indent=2));assert not coplanar and all(p['covered_by_actual_cornice_front_m2']==0 for p in rows); print(json.dumps(rows,indent=2))
