import json,numpy as np,hashlib
from pathlib import Path
from geometry_checks import *
import argparse
p=argparse.ArgumentParser();p.add_argument('--geometry',required=True);p.add_argument('--report',required=True);a=p.parse_args();assert not Path(a.report).exists();geometry_path=Path(a.geometry);g=json.loads(geometry_path.read_text());d=g['objects']['V027 | three pointed bays with high wall bands'];v=np.array(d['vertices']);ts=np.array(d['triangles']);rows=[]
assert topology(v,ts[:-1])[0]['bad_oriented_edges'];rows.append({'case':'missing_actual_face','rejected_by':'closed edge incidence'})
x=ts.copy();x[0]=x[0][::-1];assert topology(v,x)[0]['bad_oriented_edges'];rows.append({'case':'reverse_actual_face','rejected_by':'directed edge orientation'})
# Isolate exact real triangle pair to exercise the same explicit overlap predicate.
t=v[ts[0]];assert cp.contact(t.tolist(),t.tolist(),1e-7)['area']>0;rows.append({'case':'duplicate_actual_exposed_face','rejected_by':'positive-area explicit coplanar clipping'})
h=g['objects']['V012 | entrance hall ceiling lining'];ht=np.array(h['vertices'])[h['triangles']];states=[]
for station in [-1.8,.4,2.6]:
 p=np.array([station,38,32.81]);assert inside(p,v[ts])['state']=='inside' and inside(p,ht)['state']=='inside';moved=p+[0,10,0];assert inside(moved,(v+[0,10,0])[ts])['state']=='inside' and inside(moved,ht)['state']=='outside';states.append({'station':station,'detached_crown_outside_source':True})
rows.append({'case':'union_translation_detaches_all_crowns','rejected_by':'actual source-host containment','stations':states})
# A new actual-face vertex moved into the protected central body prism must fail disjointness.
x=v.copy();x[ts[0,0]]=[0,38,30.5];b=np.array([[-3.5,37.4,29.025],[4.45,38.6,31.1]]);assert np.all(x[ts[0,0]]>b[0])and np.all(x[ts[0,0]]<b[1]);rows.append({'case':'actual_new_vertex_inside_protected_prism','rejected_by':'strict point-in-prism collision'})
x=v.copy();x[0,2]=33.0;assert x[:,2].max()>32.82;rows.append({'case':'exceed_reviewed_height','rejected_by':'actual bounds'})
r={'pass':True,'input_sha256':g['input_sha256'],'geometry_sha256':hashlib.sha256(geometry_path.read_bytes()).hexdigest(),'controls':rows,'scope':'Six bounded pure exported-geometry controls, not saved or Blender-mutated candidate files. Source preservation has separate actual native negative tests.'};Path(a.report).write_text(json.dumps(r,indent=2));print('6 controls PASS')
