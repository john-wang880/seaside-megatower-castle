import bpy,json,hashlib
from pathlib import Path
P=Path('work/interior_ceiling_v026');d=json.loads((P/'current_survey.json').read_text());src=Path('work/v018/castle_v018.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();h=sha(src);assert h=='c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd';bpy.ops.wm.open_mainfile(filepath=str(src.resolve()),use_scripts=False);dg=bpy.context.evaluated_depsgraph_get();checks=[]
for r in d['objects']:
 o=bpy.data.objects.get(r['name']);assert o
 c={'object':o.name,'matrix_exact':[list(v)for v in o.matrix_world]==r['matrix'],'visibility_exact':o.hide_render==r['hide_render']and o.hide_viewport==r['hide_viewport']}
 if o.type=='MESH':
  eo=o.evaluated_get(dg);me=eo.to_mesh();g={'vertices':[list(eo.matrix_world@v.co)for v in me.vertices],'faces':[list(f.vertices)for f in me.polygons]};c['evaluated_geometry_exact']=g==d['geometry'][o.name];c['material_assignment_exact']=[{'link':m.link,'material':m.material.name if m.material else None}for m in o.material_slots]==r['material_slots'];eo.to_mesh_clear()
 if o.type=='LIGHT':c['light_data_exact']=o.data.energy==r['energy']and list(o.data.color)==r['color']and o.data.type==r['light_type']
 checks.append(c)
assert sha(src)==h
report={'historical_source_sha256':h,'current_source_sha256':d['source_sha256'],'all_selected_checks_pass':all(all(v for k,v in r.items()if k!='object')for r in checks),'objects':checks,'scope':'Selected actual evaluated vertices/faces, material slot bindings, object transforms/visibility and light energy/color/type only. Not a whole-scene/materialgraph/pixel identity claim. No render/save.'};(P/'historical_identity.json').write_text(json.dumps(report,indent=2));print('PASS',report['all_selected_checks_pass'],len(checks))
