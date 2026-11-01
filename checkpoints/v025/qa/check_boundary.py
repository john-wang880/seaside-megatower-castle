"""Compare actual saved union against independent convex boundary partition."""
import argparse,json,math,struct,hashlib
from pathlib import Path
import sys
if sys.flags.optimize:raise RuntimeError('Assertions required; optimized Python unsupported')
from surface_partition import *
p=argparse.ArgumentParser();p.add_argument('--geometry',required=True);p.add_argument('--report',required=True);a=p.parse_args();out=Path(a.report);assert not out.exists();data=json.loads(Path(a.geometry).read_text());solids=[s['faces']for s in data['original_convex_solids']];candidate,zero_measure_triangles=nonzero_triangles(data['union_triangles'])
# Float32 spacing determined before residual measurements; four ULP allowance
# covers one saved Boolean intersection coordinate plus normal-plane projection.
def ulp32(x):
 x=abs(x)
 if x==0:return 2**-149
 return 2**(math.floor(math.log2(x))-23)
coords=[c for s in solids for f in s for v in f for c in v];maxulp=max(map(ulp32,coords));distance_budget=4*maxulp
for s in solids:
 vs=[v for f in s for v in f]
 for f in s:
  n,d=plane(f);assert max(dot(n,v)-d for v in vs)<1e-7,'Input not convex'
reference=union_boundary(solids);ref=[r['polygon']for r in reference]
assert tests()==6

def perimeter(p):return sum(norm(sub(x,y))for x,y in zip(p,p[1:]+p[:1]))
def bounds(p):return [[min(v[k]for v in p)for k in range(3)],[max(v[k]for v in p)for k in range(3)]]
def broad(a,b):return all(a[1][k]+distance_budget>=b[0][k] and b[1][k]+distance_budget>=a[0][k]for k in range(3))
refs=[(f,*plane(f),bounds(f))for f in ref];cans=[(f,*plane(f),bounds(f))for f in candidate];cr=[0.]*len(cans);rr=[0.]*len(refs);maxdisp=0.;matches=0;reference_cover_polygons=[[]for _ in refs]
for i,(c,cn,cd,cb)in enumerate(cans):
 assert area(c)>1e-12,'Degenerate candidate triangle'
 for j,(r,rn,rd,rb)in enumerate(refs):
  if not broad(cb,rb)or dot(cn,rn)<=0:continue
  ds=[dot(rn,v)-rd for v in c]
  if max(map(abs,ds))>distance_budget:continue
  projected=[sub(v,mul(rn,d))for v,d in zip(c,ds)]
  intersection=projected
  for x,y in zip(r,r[1:]+r[:1]):
   outward=cross(sub(y,x),rn);intersection=clip(intersection,outward,dot(outward,x))
   if not intersection:break
  ar=area(intersection)
  if ar>1e-12:cr[i]+=ar;rr[j]+=ar;matches+=1;maxdisp=max(maxdisp,max(map(abs,ds)));reference_cover_polygons[j].append(intersection)
rows=[];fail=[]
for label,faces,coverage in [('saved',candidate,cr),('reference',ref,rr)]:
 total=sum(map(area,faces));residual=sum(abs(area(f)-cov)for f,cov in zip(faces,coverage));budget=sum(4*perimeter(f)*distance_budget+16*distance_budget**2 for f in faces)
 for i,(f,cov)in enumerate(zip(faces,coverage)):
  limit=4*perimeter(f)*distance_budget+16*distance_budget**2
  if abs(area(f)-cov)>limit:fail.append({'side':label,'index':i,'area':area(f),'coverage':cov,'residual':area(f)-cov,'budget':limit})
 rows.append({'side':label,'area':total,'absolute_coverage_residual':residual,'residual_fraction':residual/total,'sum_rounding_area_budget':budget})
# Separate actual holes and double-covered regions: signed area sums alone can cancel.
coverage_set_rows=[]
for j,(r,rn,rd,rb)in enumerate(refs):
 remaining=[r]
 for q in reference_cover_polygons[j]:
  ps=[(cross(sub(y,x),rn),dot(cross(sub(y,x),rn),x))for x,y in zip(q,q[1:]+q[:1])]
  remaining=[piece for current in remaining for piece in subtract_convex(current,ps)]
 uncovered=sum(area(piece)for piece in remaining);duplicated=rr[j]-(area(r)-uncovered);limit=4*perimeter(r)*distance_budget+16*distance_budget**2
 coverage_set_rows.append({'reference_piece':j,'uncovered_area':uncovered,'duplicate_coverage_area':duplicated,'budget':limit})
 if uncovered>limit or duplicated>limit:fail.append({'reference_piece':j,'uncovered_area':uncovered,'duplicate_coverage_area':duplicated,'budget':limit})
vref=volume(reference);vcan=volume([{'polygon':p}for p in candidate]);vbudget=rows[0]['area']*distance_budget*2
if abs(vref-vcan)>vbudget:fail.append({'volume_difference':vcan-vref,'budget':vbudget})
report={'pass':not fail,'source_sha256':data['source_sha256'],'candidate_sha256':data['candidate_sha256'],'geometry_export_sha256':hashlib.sha256(Path(a.geometry).read_bytes()).hexdigest(),'original_solids':len(solids),'independent_union_boundary_pieces':len(ref),'saved_triangles':len(candidate),'original_saved_loop_triangle_count':len(data['union_triangles']),'exact_zero_measure_loop_triangles':zero_measure_triangles,'coverage':rows,'set_coverage_uncovered_area':sum(x['uncovered_area']for x in coverage_set_rows),'set_coverage_duplicate_area':sum(max(0,x['duplicate_coverage_area'])for x in coverage_set_rows),'set_coverage_rows':coverage_set_rows,'matched_surface_pairs':matches,'maximum_matched_plane_displacement':maxdisp,'predeclared_max_coordinate_ulp':maxulp,'distance_budget_4ulp':distance_budget,'reference_union_volume':vref,'saved_union_volume':vcan,'volume_difference':vcan-vref,'volume_budget':vbudget,'failures':fail,'math_controls':6,'scope':'Both-direction oriented surface coverage from independently clipped convex input boundary; saved float32 numerical bounds, not exact rational or global model certification.'};out.write_text(json.dumps(report,indent=2));assert report['pass'],fail[:5];print('BOUNDARY PASS',rows,'volume',vcan-vref)
