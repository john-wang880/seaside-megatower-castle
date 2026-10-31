"""Read-only upper-scene vertex/edge invariance above the bounded excavation."""
import argparse,bpy,json,sys,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--baseline',required=True);p.add_argument('--checkpoint',required=True);p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(Path(path).resolve()),load_ui=False,use_scripts=False);deps=bpy.context.evaluated_depsgraph_get();vertices=set();edges=set()
 for o in bpy.data.objects:
  if o.type!='MESH' or o.hide_render:continue
  eo=o.evaluated_get(deps);me=eo.to_mesh();world=eo.matrix_world;coords=[world@v.co for v in me.vertices];used={i for p in me.polygons for i in p.vertices};keys={i:tuple(round(c,5) for c in coords[i]) for i in used if coords[i].z>35.3}
  vertices.update(keys.values())
  for e in me.edges:
   x,y=e.vertices
   if x in keys and y in keys:edges.add(tuple(sorted((keys[x],keys[y]))))
  eo.to_mesh_clear()
 return vertices,edges
v0,e0=snapshot(a.baseline);v1,e1=snapshot(a.checkpoint)
r={'threshold_z':35.3,'coordinate_precision':1e-5,'baseline_vertices':len(v0),'candidate_vertices':len(v1),'baseline_edges':len(e0),'candidate_edges':len(e1),'vertices_added':len(v1-v0),'vertices_removed':len(v0-v1),'edges_added':len(e1-e0),'edges_removed':len(e0-e1),'upper_evaluated_vertex_edge_sets_identical':v0==v1 and e0==e1,'examples_added':list(sorted(v1-v0))[:10],'examples_removed':list(sorted(v0-v1))[:10],'scope':'Visible evaluated vertex and edge geometry abovez35.3 only, at1e-5 coordinate precision. Whole scene lighting and original data checked separately; not structural certification.'};Path(a.report).write_text(json.dumps(r,indent=2));print(r);assert r['upper_evaluated_vertex_edge_sets_identical']
