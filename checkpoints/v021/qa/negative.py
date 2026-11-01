import sys,json,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import inputs,sha
a,source,candidate,report_path,plan=inputs();case=a.case
p=Path(__file__).resolve().with_name('validate.py');s=p.read_text()
mutations={'bounds':"bpy.data.objects[plan['pairs'][0]['union_object']].data.vertices[0].co.x-=.01",'orientation':"m=bpy.data.objects[plan['pairs'][0]['union_object']].data; bm=bmesh.new();bm.from_mesh(m);bm.faces.ensure_lookup_table();bm.faces[0].normal_flip();bm.to_mesh(m);bm.free()",'material':"bpy.data.objects[plan['pairs'][0]['union_object']].data.materials[0]=bpy.data.materials[plan['pairs'][1]['material']]",'mask':"bpy.data.objects[plan['pairs'][0]['target']].vertex_groups[0].add([0],1.,'REPLACE')",'unrelated_source':"bpy.data.objects['V010 | woodland boughs with gate exit clearance'].data.vertices[0].co.x+=.01"}
assert case in mutations
s=s.replace("checks={};rows=[];dg=",mutations[case]+"\nbpy.context.view_layer.update()\nchecks={};rows=[];dg=")
try:exec(compile(s,str(p)+'[negative-expanded]','exec'),{'__file__':str(p),'__name__':'__main__'})
except AssertionError as e:
 trace=traceback.format_exc();tb=e.__traceback__
 while tb.tb_next:tb=tb.tb_next
 report={'case':case,'rejected':True,'error':str(e),'traceback':trace,'actual_executed_assertion':s.splitlines()[tb.tb_lineno-1],'executed_mutation':mutations[case],'candidate_sha256':sha(candidate),'source_sha256':sha(source)}
 if report_path.exists():raise RuntimeError('Unexpected report collision')
 report_path.write_text(json.dumps(report,indent=2));print('EXPECTED REJECTION',case,str(e))
else:raise RuntimeError('Negative was not rejected')
