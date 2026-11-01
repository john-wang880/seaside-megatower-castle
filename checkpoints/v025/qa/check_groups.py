import argparse,json,subprocess,sys,hashlib,itertools
from pathlib import Path
import sys
if sys.flags.optimize:raise RuntimeError('Optimized Python unsupported')
from surface_partition import *
p=argparse.ArgumentParser();p.add_argument('--geometry',required=True);p.add_argument('--baseline-cross',required=True);p.add_argument('--output-dir',required=True);a=p.parse_args();root=Path(a.output_dir);root.mkdir(exist_ok=False);data=json.loads(Path(a.geometry).read_text());base=json.loads(Path(a.baseline_cross).read_text());assert data['source_sha256']==base['source_sha256'];groups=data['groups'];checks=[]
for g in groups:
 d={'source_sha256':data['source_sha256'],'candidate_sha256':data['candidate_sha256'],**g};inp=root/f"group_{g['ordinal']:02d}.json";out=root/f"group_{g['ordinal']:02d}_boundary.json";inp.write_text(json.dumps(d));r=subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('check_boundary.py')),'--geometry',str(inp),'--report',str(out)],capture_output=True,text=True);(root/f"group_{g['ordinal']:02d}.log").write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr;report=json.loads(out.read_text());assert report['pass'];checks.append(report)
planes=[[[plane(f)for f in s['faces']]for s in g['original_convex_solids']]for g in groups]
def inside_union(p,solids):
 remaining=[p];ret=[]
 for ps in solids:
  new=[]
  for q in remaining:
   inside=q
   for n,d in ps:
    inside=clip(inside,n,d,True)
    if not inside:break
   if inside:ret.append(inside)
   new+=subtract_convex(q,ps)
  remaining=new
 return ret
pairs=[]
for i,j in itertools.combinations(range(4),2):
 boundary=[]
 for ia,ib in [(i,j),(j,i)]:
  for f in nonzero_triangles(groups[ia]['union_triangles'])[0]:boundary +=[{'polygon':p}for p in inside_union(f,planes[ib])]
 vi=volume(boundary)if boundary else 0.;ref=next(x['actual_intersection_volume']for x in base['cross_group_pairs']if x['planes']==[groups[i]['plane_y'],groups[j]['plane_y']]);budget=checks[i]['volume_budget']+checks[j]['volume_budget'];assert abs(vi-ref)<=budget,('Crossgroup occupied intersection changed',i,j,vi,ref)
 contacts=[]
 for f in nonzero_triangles(groups[i]['union_triangles'])[0]:
  n,d=plane(f)
  for q in nonzero_triangles(groups[j]['union_triangles'])[0]:
   m,e=plane(q);alignment=dot(n,m)
   if abs(alignment)<1-1e-9 or max(abs(dot(n,v)-d)for v in q)>1e-8:continue
   ar=overlap_area(f,q if alignment>0 else list(reversed(q)),n)
   if ar>1e-8:contacts.append({'same_facing':alignment>0,'area':ar})
 assert not contacts,('New inter-frame coplanar skin',i,j,contacts[:3]);pairs.append({'planes':[groups[i]['plane_y'],groups[j]['plane_y']],'baseline_intersection_volume':ref,'saved_boundary_intersection_volume':vi,'difference':vi-ref,'numerical_volume_budget':budget,'coplanar_exterior_contacts':contacts})
(root/'SUMMARY.json').write_text(json.dumps({'pass':True,'source_sha256':data['source_sha256'],'candidate_sha256':data['candidate_sha256'],'geometry_export_sha256':hashlib.sha256(Path(a.geometry).read_bytes()).hexdigest(),'group_boundary_passes':4,'cross_group_pairs':pairs,'scope':'Each saved union boundary independently matches its five-source convex union. Intersections computed from saved boundary triangles clipped to opposite original convex decomposition; legitimate existing cross-frame overlaps retained, no global disjointness claim.'},indent=2));print('FOUR BOUNDARIES AND CROSSGROUP INTERFACES PASS')
