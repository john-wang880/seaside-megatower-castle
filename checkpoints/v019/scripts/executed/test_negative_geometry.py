"""In-memory negative control against actual geometry validator; never saves model."""
import argparse,bpy,sys,json,hashlib,traceback
from pathlib import Path
p=argparse.ArgumentParser()
for k in ['candidate','mapping','route-report','validator','report']:p.add_argument('--'+k,required=True)
p.add_argument('--control',choices=['detached_needle','reversed_face'],required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(a.candidate);out=Path(a.report);assert not out.exists();detail=out.with_suffix('.validator.json');assert not detail.exists();code=Path(a.validator).read_text();marker='for o in [fol,wood]:';assert code.count(marker)==1
mutation={}
def mutate(fol,wood):
 if a.control=='detached_needle':
  mutation['original']=list(fol.data.vertices[0].co);fol.data.vertices[0].co.x+=5;mutation['changed']=list(fol.data.vertices[0].co);fol.data.update()
 else:
  import bmesh
  bm=bmesh.new();bm.from_mesh(wood.data);bm.faces.ensure_lookup_table();bmesh.ops.reverse_faces(bm,faces=[bm.faces[0]]);bm.to_mesh(wood.data);bm.free();wood.data.update();mutation['reversed_wood_face']=0
code=code.replace(marker,'_negative_mutate(fol,wood)\n'+marker);sys.argv=[a.validator,'--','--candidate',a.candidate,'--mapping',a.mapping,'--route-report',a.route_report,'--report',str(detail)];failure=None;rejected=False
try:exec(compile(code,a.validator,'exec'),{'__name__':'__main__','__file__':a.validator,'_negative_mutate':mutate})
except AssertionError as exc:
 failure={'message':str(exc),'traceback':traceback.format_exc()}
 if a.control=='reversed_face':rejected='Open/inconsistent wood' in str(exc)
 elif detail.exists():rejected=any(x.get('kind')=='needle_root_not_strictly_inside_shoot' and x.get('blade')==0 for x in json.load(open(detail))['issues'])
result={'control':a.control,'candidate_sha256':before,'validator_sha256':sha(a.validator),'mutation_in_memory':mutation,'rejected_at_intended_invariant':rejected,'failure':failure,'candidate_unchanged':sha(a.candidate)==before,'saved_model':False};out.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));assert rejected and result['candidate_unchanged']
