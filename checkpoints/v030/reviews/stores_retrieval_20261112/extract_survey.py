import bpy,pathlib,json,sys,hashlib
P=pathlib.Path(__file__).resolve().parent
src=pathlib.Path(sys.argv[-1]).resolve()
assert hashlib.sha256(src.read_bytes()).hexdigest()=="740efdecdc3a7b081b44c244d8113b678a03aeb7cc377764195354588c00bbd6"
bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False)
names=[o.name for o in bpy.data.objects if 'supply bin' in o.name or 'three-bay rack' in o.name or o.name.startswith('S27') or o.name=='V029 | local stores shell']
d=[]
for n in names:
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();d.append({'name':n,'vertices':[list(o.matrix_world@v.co) for v in me.vertices],'triangles':[list(t.vertices) for t in me.loop_triangles]})
(P/'actual_geometry.json').write_text(json.dumps(d))
