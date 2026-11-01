import sys
if sys.flags.optimize:raise RuntimeError('Optimized Python unsupported')
import json,hashlib,numpy as np,argparse
from pathlib import Path
from coplanar_predicate import candidates,contact
from surface_partition import union_boundary
ap=argparse.ArgumentParser();ap.add_argument('--report',required=True);args=ap.parse_args();out=Path(args.report);assert not out.exists();P=Path(__file__).resolve().parent;eps=.00006103515625;a=[(0.,0.,0.),(2.,0.,0.),(0.,2.,0.)];b=[(.5,.5,0.),(1.5,.5,0.),(.5,1.5,0.)];cases=[]
def check(name,tri,expected_area=None,same=True):
 arr=np.asarray([tri],dtype=float);ix=candidates(a,arr,eps);r=contact(a,arr[ix[0]].tolist(),eps)if ix else None
 if expected_area is None:assert r is None,(name,r)
 else:assert r and abs(r['area']-expected_area)<1e-12 and r['same_facing']==same,(name,r)
 cases.append({'name':name,'pass':True,'broadphase_indices':ix,'contact':r})
check('contained coplanar same-facing',b,.5);check('identical coplanar triangles',a,2.);check('opposite-facing shared interface',list(reversed(b)),.5,False);check('separated parallel plane',[(x,y,z+.01)for x,y,z in b]);check('overlapping AABBs but disjoint coplanar triangles',[(1.5,1.5,0.),(2.,1.5,0.),(1.5,2.,0.)]);check('zero-area edge contact',[(2.,0.,0.),(3.,0.,0.),(2.,1.,0.)]);check('spatially disjoint bounds',[(x+10,y,z)for x,y,z in b]);check('near-plane within declared saved-float budget',[(x,y,z+1e-6)for x,y,z in b],.5)
proof=json.loads((P/'source_proof.json').read_text());ref=union_boundary([x['faces']for x in proof['geometry']['original_convex_solids']]);tris=[[p[0],p[i],p[i+1]]for f in ref for p in [f['polygon']]for i in range(1,len(p)-1)];d=json.loads((P/'source_shaft_geometry.json').read_text());f=d['faces'][13];q=[d['vertices'][i]for i in f['vertices']];other=[[q[0],q[i],q[i+1]]for i in range(1,len(q)-1)];other=np.asarray(other,dtype=float);total=0.
for t in tris:
 for j in candidates(t,other,eps):
  r=contact(t,other[j].tolist(),eps)
  if r:assert r['same_facing'];total+=r['area']
assert total==140.;cases.append({'name':'actual known source polygon13 positive control','pass':True,'area':total});report={'pass':True,'controls':cases,'adjacent_runtime_sha256':hashlib.sha256((P/'adjacent.py').read_bytes()).hexdigest(),'helper_sha256':hashlib.sha256((P/'coplanar_predicate.py').read_bytes()).hexdigest(),'source_proof_sha256':hashlib.sha256((P/'source_proof.json').read_bytes()).hexdigest(),'scope':'Pure tests of the exact shared native-scan predicate, including known actual140-area coplanar source contact; no source/model mutation.'};out.write_text(json.dumps(report,indent=2));print('COPLANAR CONTROLS PASS',len(cases))
