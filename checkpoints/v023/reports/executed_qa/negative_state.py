import sys,json,traceback,hashlib
from pathlib import Path
case=sys.argv[sys.argv.index('--')+1];p=Path(__file__).resolve().with_name('export_and_preserve.py');s=p.read_text();mutation={'extra_mask':"bpy.data.objects[plan['path_object']].vertex_groups[0].add([0],1.,'REPLACE')",'unrelated_source':"hidden=next(ob for ob in bpy.data.objects if ob.type=='MESH' and ob.hide_render and len(ob.data.vertices)); hidden.data.vertices[0].co.x+=.01"}[case];needle="bpy.ops.wm.open_mainfile(filepath=str(candidate),use_scripts=False);";s=s.replace(needle,needle+'\n'+mutation+'\nbpy.context.view_layer.update();').replace("(P/'actual_geometry.json')","(P/'negative_%s_geometry.json')"%case).replace("(P/'preservation.json')","(P/'negative_%s_preservation.json')"%case)
try:exec(compile(s,str(p)+'[expanded-negative]','exec'),{'__file__':str(p),'__name__':'__main__'})
except AssertionError as e:
 tb=e.__traceback__
 while tb.tb_next:tb=tb.tb_next
 r={'case':case,'rejected':True,'mutation':mutation,'actual_assertion':s.splitlines()[tb.tb_lineno-1],'error':str(e),'traceback':traceback.format_exc()};Path(__file__).with_name('negative_'+case+'.json').write_text(json.dumps(r,indent=2));print('EXPECTED',case)
else:raise RuntimeError('Negative accepted')
