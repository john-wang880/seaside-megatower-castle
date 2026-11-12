import bpy,sys,json,pathlib,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=pathlib.Path(__file__).resolve().parent;src=pathlib.Path(sys.argv[-1]);assert hashlib.sha256(src.read_bytes()).hexdigest()=='a6c9715064ae0ea8ee58f369f46ceb3352bfc84fb53687b30bffd35bf38bd9ce'
bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False);dg=bpy.context.evaluated_depsgraph_get();low=(6.8,27.6,28.8);high=(14.2,32.7,32.25);out=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render:continue
 e=o.evaluated_get(dg);m=e.to_mesh();v=[e.matrix_world@x.co for x in m.vertices]
 if not v or any(max(x[i]for x in v)<low[i] or min(x[i]for x in v)>high[i] for i in range(3)):e.to_mesh_clear();continue
 m.calc_loop_triangles();ts=[]
 for t in m.loop_triangles:
  pts=[v[k] for k in t.vertices]
  if all(max(x[i]for x in pts)>=low[i] and min(x[i]for x in pts)<=high[i]for i in range(3)):ts.append([list(x)for x in pts])
 if ts:out.append({'name':o.name,'triangles':ts,'modifiers':[x.type for x in o.modifiers]})
 e.to_mesh_clear()
(P/'LOCAL.json').write_text(json.dumps({'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'proposed_room':[ [7,27.8,29],[14,32.4,32.05]],'review_bounds':[low,high],'surface_overlap':out},indent=2));print([(x['name'],len(x['triangles']))for x in out])
