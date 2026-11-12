import bpy,json,pathlib,sys,hashlib
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parent
assert hashlib.sha256(pathlib.Path(sys.argv[-1]).read_bytes()).hexdigest()=='a6c9715064ae0ea8ee58f369f46ceb3352bfc84fb53687b30bffd35bf38bd9ce'
bpy.ops.wm.open_mainfile(filepath=sys.argv[-1],use_scripts=False)
r=[]
for o in bpy.data.objects:
 if o.type=='MESH':
  b=[o.matrix_world@Vector(v) for v in o.bound_box]
  r.append({'name':o.name,'min':[min(v[i] for v in b) for i in range(3)],'max':[max(v[i] for v in b) for i in range(3)]})
(P/'bounds.json').write_text(json.dumps(r,indent=2))
for o in bpy.data.objects:
 if o.type=='CAMERA':print('CAMERA',o.name,list(o.location),list(o.rotation_euler))
