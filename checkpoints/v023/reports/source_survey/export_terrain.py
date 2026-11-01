import bpy,json,hashlib
from pathlib import Path
P=Path('work/path_arrival_v022');src=Path('work/v022/castle_v022.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();h=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src.resolve()),use_scripts=False);o=bpy.data.objects['V002 | western headland with solid rock shore'];eo=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=eo.to_mesh();m.calc_loop_triangles();rows=[]
for t in m.loop_triangles:
 vs=[o.matrix_world@m.vertices[i].co for i in t.vertices]
 if t.normal.z<=.05 or max(v.x for v in vs)<-114 or min(v.x for v in vs)>-97 or max(v.y for v in vs)<39 or min(v.y for v in vs)>74:continue
 rows.append({'face':t.polygon_index,'triangle':t.index,'coords':[list(v)for v in vs]})
eo.to_mesh_clear();(P/'local_terrain_triangles.json').write_text(json.dumps({'source_sha256':h,'source_unchanged':sha(src)==h,'object':o.name,'triangles':rows},indent=2));print('EXPORTED',len(rows))
