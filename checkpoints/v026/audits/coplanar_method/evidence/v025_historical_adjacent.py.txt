import bpy,sys,json,hashlib,argparse,collections
from pathlib import Path
import sys
if sys.flags.optimize:raise RuntimeError('Optimized Python unsupported')
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent));from surface_partition import *
p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--candidate-sha',required=True);p.add_argument('--report',required=True);p.add_argument('--union',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);src=Path(a.candidate);sha=lambda:hashlib.sha256(src.read_bytes()).hexdigest();assert sha()==a.candidate_sha and not Path(a.report).exists();bpy.ops.wm.open_mainfile(filepath=str(src.resolve()),use_scripts=False);dg=bpy.context.evaluated_depsgraph_get();u=bpy.data.objects[a.union];m=u.data;m.calc_loop_triangles();uv=[u.matrix_world@v.co for v in m.vertices];ut=[tuple(t.vertices)for t in m.loop_triangles if not exact_zero_triangle([tuple(uv[i])for i in t.vertices])];uf=[[tuple(uv[i])for i in t]for t in ut];up=[plane(f)for f in uf];ub=BVHTree.FromPolygons(uv,ut,all_triangles=True,epsilon=0.000030517578125);lo=[min(v[k]for v in uv)for k in range(3)];hi=[max(v[k]for v in uv)for k in range(3)]
rows=[];scanned=[];eps=0.000030517578125
for o in bpy.context.scene.objects:
 if o==u or o.type!='MESH' or o.hide_render:continue
 # Render-visible architecture must not disappear just because viewport hidden.
 eo=o.evaluated_get(dg);bb=[eo.matrix_world@Vector(v)for v in eo.bound_box]
 if any(max(v[k]for v in bb)<lo[k]-eps or min(v[k]for v in bb)>hi[k]+eps for k in range(3)):continue
 # Volume-only atmospheric objects are not opaque architectural skins.
 surface=any(mat and (not mat.use_nodes or any(n.type=='OUTPUT_MATERIAL'and n.is_active_output and n.inputs['Surface'].is_linked for n in mat.node_tree.nodes))for mat in o.data.materials)
 if not surface:continue
 me=eo.to_mesh();me.calc_loop_triangles();vs=[eo.matrix_world@v.co for v in me.vertices];ts=[tuple(t.vertices)for t in me.loop_triangles];bv=BVHTree.FromPolygons(vs,ts,all_triangles=True,epsilon=eps);pairs=ub.overlap(bv);scanned.append({'object':o.name,'triangles':len(ts),'aabb_triangle_candidates':len(pairs),'hide_viewport':o.hide_viewport,'hide_get':o.hide_get()})
 for i,j in pairs:
  q=[tuple(vs[k])for k in ts[j]]
  if area(q)<1e-12:continue
  n,d=up[i];qn,qd=plane(q);alignment=dot(n,qn);dist=max(abs(dot(n,v)-d)for v in q)
  if abs(alignment)<.99999 or dist>eps:continue
  projected=[sub(v,mul(n,dot(n,v)-d))for v in q]
  if alignment<0:projected.reverse()
  ar=overlap_area(uf[i],projected,n)
  if ar<=1e-9:continue
  rows.append({'object':o.name,'union_triangle':i,'neighbor_triangle':j,'neighbor_polygon':me.loop_triangles[j].polygon_index,'same_facing':alignment>0,'area':ar,'maximum_plane_distance':dist,'strict_coplanar_at_1e_7':dist<1e-7})
 eo.to_mesh_clear()
summary=collections.defaultdict(lambda:{'same_facing_area':0.,'opposite_facing_area':0.,'pairs':0})
for r in rows:
 s=summary[r['object']];s['same_facing_area'if r['same_facing']else'opposite_facing_area']+=r['area'];s['pairs']+=1
assert sha()==a.candidate_sha
Path(a.report).write_text(json.dumps({'candidate_sha256':a.candidate_sha,'source_unchanged':True,'evaluated_broadphase':True,'scanned_objects':scanned,'contacts':rows,'by_object':dict(summary),'scope':'All render-visible surface-mesh objects with evaluated bounds intersecting entire selected union bounds. Triangle BVH broadphase plus actual oriented coplanar polygon overlap. Areas pairwise may include multiway overlap; exposure/burial not inferred from overlap alone.'},indent=2));print('ADJACENT',dict(summary))
