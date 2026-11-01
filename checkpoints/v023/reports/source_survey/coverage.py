"""Read-only exact piecewise-planar XY overlap; no Blender or model writes."""
import json,math
from pathlib import Path
P=Path('work/path_arrival_v022');data=json.load(open(P/'survey.json'));path=data['path'];ground=json.load(open(P/'local_terrain_triangles.json'));V=path['vertices']
def area(poly):return abs(sum(a[0]*b[1]-a[1]*b[0]for a,b in zip(poly,poly[1:]+poly[:1]))*.5)if poly else 0
def ccw(poly):
 return poly if sum(a[0]*b[1]-a[1]*b[0]for a,b in zip(poly,poly[1:]+poly[:1]))>0 else poly[::-1]
def cut(poly,fn):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  fa,fb=fn(a),fn(b)
  if fa>=0:out.append(a)
  if(fa>=0)!=(fb>=0):
   t=fa/(fa-fb);out.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])))
 return out
def clip(poly,tri):
 for a,b in zip(tri,tri[1:]+tri[:1]):
  poly=cut(poly,lambda p:(b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]))
  if not poly:break
 return poly
def plane(vs):
 p,q,r=vs;u=[q[i]-p[i]for i in range(3)];v=[r[i]-p[i]for i in range(3)];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];a,b=-n[0]/n[2],-n[1]/n[2];return a,b,p[2]-a*p[0]-b*p[1]
G=[]
for g in ground['triangles']:
 vs=g['coords'];G.append((g,ccw([(v[0],v[1])for v in vs]),plane(vs),[min(v[k]for v in vs)for k in range(2)],[max(v[k]for v in vs)for k in range(2)]))
rows=[]
for f in path['faces']:
 row=min(f['vertices'])//7
 if not 95<=row<=109:continue
 vs=[V[i]for i in f['vertices']];poly=ccw([(v[0],v[1])for v in vs]);pa=plane(vs);lo=[min(v[k]for v in vs)for k in range(2)];hi=[max(v[k]for v in vs)for k in range(2)];total=buried=0;parts=[]
 for g,tri,pb,gl,gh in G:
  if any(hi[k]<gl[k]or lo[k]>gh[k]for k in range(2)):continue
  inter=clip(poly,tri);a=area(inter)
  if a<1e-10:continue
  diff=[pb[i]-pa[i]for i in range(3)];above=lambda p:diff[0]*p[0]+diff[1]*p[1]+diff[2];bad=cut(inter,above);ba=area(bad);total+=a;buried+=ba
  if ba>1e-9:parts.append({'terrain_face':g['face'],'area':ba,'polygon_xy':bad,'max_terrain_above_path':max(above(p)for p in bad)})
 original=area(poly);assert abs(total-original)<1e-7,(f['id'],original,total)
 rows.append({'face':f['id'],'row':row,'cross_cell':(f['id']%12)//2,'material':path['materials'][f['material_index']],'plan_area':original,'terrain_covered_area':buried,'terrain_covered_fraction':buried/original,'buried_parts':parts})
summary={}
for name,rs in [('all_selected_faces',rows),('inner_four_cells',[r for r in rows if r['cross_cell']in[1,2,3,4]]),('outer_two_cells',[r for r in rows if r['cross_cell']in[0,5]])]:
 a=sum(r['plan_area']for r in rs);b=sum(r['terrain_covered_area']for r in rs);summary[name]={'faces':len(rs),'plan_area':a,'terrain_covered_area':b,'terrain_covered_fraction':b/a,'faces_with_positive_buried_area':sum(r['terrain_covered_area']>1e-8 for r in rs)}
(P/'coverage.json').write_text(json.dumps({'method':'Exact evaluated triangle XY clipping and affine terrainZ−pathZ halfplane clipping, Python doubleprecision; summed triangle coverage equals each originalpathtriangle area within1e−7. Planimetric coverage, notcamera projectedpixelarea. Topterrain singleheightfield inthis boundedwindow; nootherobjects included.','source_sha256':data['source_sha256'],'summary':summary,'faces':rows},indent=2));print(json.dumps(summary,indent=2))
