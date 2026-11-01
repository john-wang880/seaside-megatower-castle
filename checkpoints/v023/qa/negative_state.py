import sys,json,traceback,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import inputs,sha
a,source,candidate,report_path,geometry_path,plan=inputs();case=a.case;p=Path(__file__).resolve().with_name('export_and_preserve.py');s=p.read_text();mutation={'extra_mask':"bpy.data.objects[plan['path_object']].vertex_groups[0].add([0],1.,'REPLACE')",'unrelated_source':"hidden=next(ob for ob in bpy.data.objects if ob.type=='MESH' and ob.hide_render and len(ob.data.vertices)); hidden.data.vertices[0].co.x+=.01"}[case];needle="bpy.ops.wm.open_mainfile(filepath=str(candidate),use_scripts=False);";s=s.replace(needle,needle+'\n'+mutation+'\nbpy.context.view_layer.update();').replace("report_path.write_text", "report_path.with_name(report_path.stem+'_failed_preservation.json').write_text")
try:exec(compile(s,str(p)+'[expanded-negative]','exec'),{'__file__':str(p),'__name__':'__main__'})
except AssertionError as e:
 tb=e.__traceback__
 while tb.tb_next:tb=tb.tb_next
 r={'case':case,'rejected':True,'mutation':mutation,'actual_assertion':s.splitlines()[tb.tb_lineno-1],'error':str(e),'source_sha256':sha(source),'candidate_sha256':sha(candidate),'traceback':traceback.format_exc()};report_path.write_text(json.dumps(r,indent=2));print('EXPECTED',case)
else:raise RuntimeError('Negative accepted')
