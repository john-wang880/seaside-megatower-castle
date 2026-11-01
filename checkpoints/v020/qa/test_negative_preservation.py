"""Hidden original source mutation must reject additive preservation; memory only."""
import argparse,bpy,hashlib,json,sys,traceback
from pathlib import Path
p=argparse.ArgumentParser()
for k in ['source','candidate','specification','validator','report']:p.add_argument('--'+k,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();shas={k:sha(getattr(a,k)) for k in ['source','candidate']};out=Path(a.report);assert not out.exists();detail=out.with_suffix('.validator.json');code=Path(a.validator).read_text();marker='x=ss.snap()';assert code.count(marker)==1;target='Dense western woodland | irregular three-dimensional needle boughs';changed=[]
def mutate(path):
 if Path(path).resolve()==Path(a.candidate).resolve():
  obj=bpy.data.objects[target];assert obj.hide_render;obj.data.vertices[0].co.x+=.01;obj.data.update();changed.append(obj.data.name)
code=code.replace(marker,'_negative_mutate(path);'+marker);sys.path.insert(0,str(Path(a.validator).resolve().parent));sys.argv=[a.validator,'--','--source',a.source,'--candidate',a.candidate,'--specification',a.specification,'--report',str(detail)];failure=None
try:exec(compile(code,a.validator,'exec'),{'__name__':'__main__','__file__':a.validator,'_negative_mutate':mutate})
except AssertionError as exc:failure={'message':str(exc),'traceback':traceback.format_exc()}
r=json.loads(detail.read_text()) if detail.exists() else {};rejected=bool(changed and not r.get('pass',True) and changed[0] in r.get('changes',{}).get('meshes',[]));unchanged=all(sha(getattr(a,k))==v for k,v in shas.items());out.write_text(json.dumps({'control':'hidden_original_vertex_mutation','rejected_at_intended_invariant':rejected,'failure':failure,'input_sha256':shas,'files_unchanged':unchanged,'model_saved':False},indent=2));assert rejected and unchanged
