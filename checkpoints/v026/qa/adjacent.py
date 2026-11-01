"""Read-only correction of the historical BVH-only coplanar broadphase."""
import sys
sys.dont_write_bytecode=True
if sys.flags.optimize:raise RuntimeError('Optimized Python unsupported')
import bpy,argparse,json,hashlib,collections,numpy as np
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from surface_partition import exact_zero_triangle
from coplanar_predicate import candidates,contact
p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--sha256',required=True);p.add_argument('--union',action='append',required=True);p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
src=Path(a.model).resolve();out=Path(a.report).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if out.exists() or out==src:raise RuntimeError('New external report required')
if sha(src)!=a.sha256:raise RuntimeError('Source SHA mismatch')
bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False);dg=bpy.context.evaluated_depsgraph_get();eps=0.00006103515625
results=[]
for name in a.union:
 u=bpy.data.objects[name];eu=u.evaluated_get(dg);um=eu.to_mesh();um.calc_loop_triangles();uv=[tuple(eu.matrix_world@v.co)for v in um.vertices]
 ut=[(t.index,t.polygon_index,[uv[k]for k in t.vertices])for t in um.loop_triangles if not exact_zero_triangle([uv[k]for k in t.vertices])]
 lo=[min(v[k]for v in uv)for k in range(3)];hi=[max(v[k]for v in uv)for k in range(3)];rows=[];scanned=[]
 for o in bpy.context.scene.objects:
  if o==u or o.type!='MESH' or o.hide_render:continue
  eo=o.evaluated_get(dg);bb=[eo.matrix_world@Vector(v)for v in eo.bound_box]
  if any(max(v[k]for v in bb)<lo[k]-eps or min(v[k]for v in bb)>hi[k]+eps for k in range(3)):continue
  if not any(s.material and(not s.material.use_nodes or any(n.type=='OUTPUT_MATERIAL'and n.is_active_output and n.inputs['Surface'].is_linked for n in s.material.node_tree.nodes))for s in o.material_slots):continue
  me=eo.to_mesh();me.calc_loop_triangles();vs=[tuple(eo.matrix_world@v.co)for v in me.vertices];ts=[(t.index,t.polygon_index,[vs[k]for k in t.vertices])for t in me.loop_triangles];arr=np.asarray([r[2]for r in ts],dtype=float);count=0
  for ti,pi,tri in ut:
   for j in candidates(tri,arr,eps):
    count+=1;hit=contact(tri,arr[j].tolist(),eps)
    if hit:rows.append({'object':o.name,'union_triangle':ti,'union_polygon':pi,'neighbor_triangle':ts[j][0],'neighbor_polygon':ts[j][1],**hit})
  scanned.append({'object':o.name,'triangles':len(ts),'bounds_plane_candidates':count});eo.to_mesh_clear()
 eu.to_mesh_clear();summary=collections.defaultdict(lambda:{'same_facing_area':0.,'opposite_facing_area':0.,'pairs':0})
 for r in rows:
  s=summary[r['object']];s['same_facing_area'if r['same_facing']else'opposite_facing_area']+=r['area'];s['pairs']+=1
 results.append({'union':name,'scanned_objects':scanned,'contacts':rows,'by_object':dict(summary)})
if sha(src)!=a.sha256:raise RuntimeError('Source changed')
root=Path(__file__).resolve().parent
out.write_text(json.dumps({'model_sha256':a.sha256,'source_unchanged':True,'plane_tolerance':eps,'minimum_reported_pair_area':1e-8,'helper_sha256':sha(root/'coplanar_predicate.py'),'results':results,'scope':'Explicit triangle bounds/plane filter and oriented polygon overlap. All render-visible neighboring surface meshes evaluated before bounds cull. Exact-zero derived triangles omitted only from normal operations. Pair areas can double-count multiway contacts; contacts alone do not establish exposure or geometric regression. Historical reports remain unchanged.'},indent=2));print('RECHECK',[(r['union'],r['by_object'])for r in results])
