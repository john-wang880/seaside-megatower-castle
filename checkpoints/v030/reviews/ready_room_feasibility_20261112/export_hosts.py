import bpy,sys,json,pathlib,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=pathlib.Path(__file__).resolve().parent;src=pathlib.Path(sys.argv[-1]);assert hashlib.sha256(src.read_bytes()).hexdigest()=='a6c9715064ae0ea8ee58f369f46ceb3352bfc84fb53687b30bffd35bf38bd9ce'
bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False);dg=bpy.context.evaluated_depsgraph_get();low=(6.8,27.6,28.8);high=(14.2,32.7,32.25);out=[]
for name in ['V029 | foundation outside stores guard','V029 | ashlar outside stores guard','V029 | receiving shell outside stores guard']:
 o=bpy.data.objects[name];e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles()
 out.append({'name':name,'vertices':[list(e.matrix_world@v.co)for v in m.vertices],'triangles':[list(t.vertices)for t in m.loop_triangles],'faces':[list(p.vertices)for p in m.polygons],'modifiers':[x.type for x in o.modifiers],'vertex_groups':[x.name for x in o.vertex_groups],'users':o.data.users,'materials':[x.name if x else None for x in m.materials]});e.to_mesh_clear()
(P/'HOSTS.json').write_text(json.dumps(out))
