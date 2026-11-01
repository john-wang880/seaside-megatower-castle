import sys
if sys.flags.optimize:raise RuntimeError('Optimized Python unsupported')
import json,sys,argparse,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from surface_partition import *
p=argparse.ArgumentParser();p.add_argument('--contacts',required=True);p.add_argument('--geometry',required=True);p.add_argument('--preservation',required=True);p.add_argument('--report',required=True);a=p.parse_args();out=Path(a.report);assert not out.exists();cd=json.loads(Path(a.contacts).read_text());gd=json.loads(Path(a.geometry).read_text());pd=json.loads(Path(a.preservation).read_text());assert pd['pass'];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();groups=gd.get('groups',[gd]);records=[]
assert cd['model_sha256']==gd['candidate_sha256']
for result,g in zip(cd['results'],groups):
 ref=union_boundary([s['faces']for s in g['original_convex_solids']]);rows=[]
 for i in sorted(set(r['union_triangle']for r in result['contacts'])):
  t=g['union_triangles'][i];n,d=plane(t);covers=[]
  for j,r in enumerate(ref):
   q=r['polygon'];m,e=plane(q)
   if dot(n,m)<.99999 or max(abs(dot(m,v)-e)for v in t)>3.0517578125e-5:continue
   ar=overlap_area(t,q,n)
   if ar>1e-9:covers.append({'reference_boundary_piece':j,'area':ar,'original_operand':r.get('source',r.get('solid_index'))})
  ar=area(t);covered=sum(x['area']for x in covers);assert abs(ar-covered)<1e-5,(i,ar,covered)
  rows.append({'saved_triangle_index':i,'triangle_area':ar,'original_union_boundary_coverage':covered,'reference_pieces':covers,'normal':n,'plane_offset':d})
 records.append({'union':result['union'],'contact_triangles':rows})
checks=pd.get('normalized_source_checks',pd.get('normalized_full_scene_checks',{}));assert checks and all(checks.values())
out.write_text(json.dumps({'pass':True,'model_sha256':cd['model_sha256'],'original_source_sha256':gd['source_sha256'],'inputs':{p:sha(p)for p in [a.contacts,a.geometry,a.preservation]},'all_contact_triangles_on_original_occupied_union_boundary':True,'unchanged_neighbor_geometry_basis':checks,'records':records,'scope':'Every newly detected contact triangle is linked to the independently clipped original operands boundary. Neighbor geometry preservation is separately bound to the full-scene normalized proof. Therefore contacts are inherited occupied-boundary relationships, not evidence of union enlargement. No universal visibility/burial claim.'},indent=2));print('ORIGINAL BOUNDARY LINK PASS')
