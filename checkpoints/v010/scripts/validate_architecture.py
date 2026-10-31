import bpy,bmesh,argparse,json,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);rows=[]
for o in bpy.data.objects:
 if not o.name.startswith('V010 |') or o.type!='MESH' or any(w in o.name for w in ('woodland','headland')):continue
 bm=bmesh.new();bm.from_mesh(o.data);row={'object':o.name,'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume':bm.calc_volume(signed=True)};bm.free();rows.append(row)
r={'new_architecture':rows,'closed_positive_volume':all(q['nonmanifold_edges']==0 and q['signed_volume']>0 for q in rows),'door_deliberately_closed':True,'interior_courtyard_route_complete':False};Path(a.report).write_text(json.dumps(r,indent=2));print(r);assert r['closed_positive_volume']
