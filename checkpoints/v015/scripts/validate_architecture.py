import bpy,bmesh,argparse,json,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);rows=[]
for o in bpy.data.objects:
 if o.type!='MESH' or not o.name.startswith('V014 |'):continue
 bm=bmesh.new();bm.from_mesh(o.data);rows.append({'object':o.name,'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume':bm.calc_volume(signed=True)});bm.free()
r={'new_meshes':rows,'closed_positive_volumes':all(q['nonmanifold_edges']==0 and q['signed_volume']>0 for q in rows),'scope':'Mesh topology only, not structural engineering certification.'};Path(a.report).write_text(json.dumps(r,indent=2));print(r);assert r['closed_positive_volumes']
