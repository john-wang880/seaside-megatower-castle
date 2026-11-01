import sys,json,traceback,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import inputs,sha
a,source,candidate,report_path,data=inputs();case=a.case;p=Path(__file__).resolve().with_name('critical.py');s=p.read_text()
mutations={'mask':"bpy.data.objects[plan['object']].vertex_groups[0].add([0],1.,'REPLACE')",'hidden_original':"hidden=next(ob for ob in bpy.data.objects if ob.type=='MESH' and ob.hide_render and len(ob.data.vertices)); hidden.data.vertices[0].co.x+=.01",'enlargement':"bpy.data.objects[plan['replacement']].data.vertices[24].co.x-=2",'orientation':"mm=bpy.data.objects[plan['replacement']].data; bb=bmesh.new();bb.from_mesh(mm);bb.faces.ensure_lookup_table();bb.faces[0].normal_flip();bb.to_mesh(mm);bb.free()",'backing_gap':"mm=bpy.data.objects[plan['replacement']].data; [setattr(mm.vertices[i].co,'z',100.) for i in range(20,24)]"}
assert case in mutations
needle="bpy.ops.wm.open_mainfile(filepath=str(candidate),use_scripts=False);"
s=s.replace(needle,needle+'\n'+mutations[case]+'\nbpy.context.view_layer.update();').replace("report_path.write_text", "report_path.with_name(report_path.stem+'_mutation_full.json').write_text")
try:exec(compile(s,str(p)+'[expanded-negative]','exec'),{'__file__':str(p),'__name__':'__main__'})
except AssertionError as e:
 tb=e.__traceback__
 while tb.tb_next:tb=tb.tb_next
 r={'case':case,'rejected':True,'error':str(e),'actual_assertion':s.splitlines()[tb.tb_lineno-1],'mutation':mutations[case],'traceback':traceback.format_exc(),'candidate_sha256':sha(candidate),'source_sha256':sha(source),'expanded_sha256':hashlib.sha256(s.encode()).hexdigest()};report_path.write_text(json.dumps(r,indent=2));print('EXPECTED',case,r['actual_assertion'])
else:raise RuntimeError('Negative accepted')
