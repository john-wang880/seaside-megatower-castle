"""Fresh-process in-memory negative fixture. No source script/model is edited."""
import argparse,bpy,hashlib,json,sys,traceback
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--asset',required=True);p.add_argument('--source-components',required=True);p.add_argument('--baseline',required=True);p.add_argument('--checkpoint',required=True);p.add_argument('--validator',required=True);p.add_argument('--report',required=True);p.add_argument('--control',choices=['wrong_mask_vertex','unselected_geometry','hidden_original'],required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();source=Path(a.baseline).resolve();candidate=Path(a.checkpoint).resolve();shas=(sha(source),sha(candidate));report=Path(a.report).resolve();assert not report.exists();detail=report.with_suffix('.validator.json');assert not detail.exists();validator=Path(a.validator).resolve();code=validator.read_text();marker='check = snap()';assert code.count(marker)==1
mutation={}
def mutate():
 target='Dense western woodland | irregular three-dimensional needle boughs' if a.control=='hidden_original' else 'V010 | woodland boughs with gate exit clearance';o=bpy.data.objects[target];selected=set(range(90395,90693));index=next(i for f in o.data.polygons for i in f.vertices if i not in selected)
 mutation.update({'object':target,'mesh':o.data.name,'vertex':index})
 if a.control=='wrong_mask_vertex':
  o.vertex_groups['V019 candidate | reversible left tree foliage'].add([index],1.0,'REPLACE');mutation['operation']='add weight1 on unselected faced vertex'
 else:
  mutation['before']=list(o.data.vertices[index].co);o.data.vertices[index].co.x+=.01;mutation['after']=list(o.data.vertices[index].co);mutation['operation']='shift source vertex x by0.01'
 o.data.update();bpy.context.view_layer.update()
code=code.replace(marker,'_qa_negative_mutation();'+marker)
sys.argv=[str(validator),'--','--baseline',str(source),'--checkpoint',str(candidate),'--report',str(detail),'--source-components',a.source_components,'--asset',a.asset]
rejected=False;failure=None
try:exec(compile(code,str(validator),'exec'),{'__name__':'__main__','__file__':str(validator),'_qa_negative_mutation':mutate})
except AssertionError as exc:
 failure={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
 if a.control=='wrong_mask_vertex':rejected='Unexpected owned group/weight set' in str(exc)
 elif detail.exists():
  d=json.loads(detail.read_text());rejected=not d['pass'] and mutation['mesh'] in d['source_differences']['meshes']
result={'control':a.control,'mutation_in_memory_only':mutation,'rejected_at_intended_invariant':rejected,'failure':failure,'validator_sha256':sha(validator),'baseline_sha256':shas[0],'candidate_sha256':shas[1],'baseline_file_unchanged':sha(source)==shas[0],'candidate_file_unchanged':sha(candidate)==shas[1],'source_saved':False,'scope':'Intentional corruption injected immediately after candidate read inside actual validation flow. No modified validator/model saved; raw exception and detailed comparison retained. Not a real candidate defect.'}
report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));assert rejected and result['baseline_file_unchanged'] and result['candidate_file_unchanged'],'Control failed expected rejection'
