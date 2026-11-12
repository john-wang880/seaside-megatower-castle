import bpy,sys,pathlib,json,numpy as np
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parent
import hashlib
assert hashlib.sha256(pathlib.Path(sys.argv[-1]).read_bytes()).hexdigest()=='a6c9715064ae0ea8ee58f369f46ceb3352bfc84fb53687b30bffd35bf38bd9ce'
bpy.ops.wm.open_mainfile(filepath=sys.argv[-1],use_scripts=False);deps=bpy.context.evaluated_depsgraph_get();r=[];lo=np.array([113.5,189.9,5.9]);hi=np.array([118.5,192.6,7.6])
for o in bpy.data.objects:
 if o.type!='MESH' or o.hide_render:continue
 eo=o.evaluated_get(deps);bb=np.array([list(eo.matrix_world@Vector(c))for c in eo.bound_box])
 if np.any(bb.max(axis=0)<lo) or np.any(bb.min(axis=0)>hi):continue
 me=eo.to_mesh();me.calc_loop_triangles();v=np.array([list(eo.matrix_world@q.co)for q in me.vertices]);idx=np.array([list(t.vertices)for t in me.loop_triangles]);t=v[idx];mask=np.all(t.max(axis=1)>=lo,axis=1)&np.all(t.min(axis=1)<=hi,axis=1)
 if np.any(mask):r.append({'name':o.name,'triangles_xyz':t[mask].tolist(),'selected_triangles':int(mask.sum()),'total_triangles':len(t)})
 eo.to_mesh_clear()
(P/'ENVIRONMENT.json').write_text(json.dumps({'scope':'Evaluated render-visible source meshes; every triangle whose AABB intersects the local tested envelope. No source changes.','envelope':[lo.tolist(),hi.tolist()],'objects':r}))
