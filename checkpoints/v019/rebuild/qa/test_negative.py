"""Portable in-memory negative fixtures for accepted-model-bound semantic QA. Never saves."""
import argparse,hashlib,json,sys,traceback
from pathlib import Path
if sys.flags.optimize: raise RuntimeError('Run with assertions enabled; optimized Python is unsupported')
p=argparse.ArgumentParser()
for k in ['baseline','checkpoint','asset','asset-sha256','accepted-model','source-components','validator','report']:p.add_argument('--'+k,required=True)
p.add_argument('--control',choices=['asset_vertex','asset_material','asset_transform','wrong_mask_vertex','hidden_original'],required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();inputs={x:sha(getattr(a,x)) for x in ['baseline','checkpoint','asset','accepted_model']};out=Path(a.report);assert not out.exists();detail=out.with_suffix('.validator.json');assert not detail.exists();code=Path(a.validator).read_text();mutation={}
def mutate():
 import bpy
 if a.control.startswith('asset_'):
  o=bpy.data.objects['CONCEPT | radial articulated needle sprays']
  if a.control=='asset_vertex':o.data.vertices[0].co.x+=.01;o.data.update()
  elif a.control=='asset_transform':o.location.x+=.01
  else:o.data.materials[0].diffuse_color[0]=.314159
 else:
  if a.control=='wrong_mask_vertex':
   o=bpy.data.objects['V010 | woodland boughs with gate exit clearance'];o.vertex_groups['V019 candidate | reversible left tree foliage'].add([0],1,'REPLACE')
  else:
   o=bpy.data.objects['Dense western woodland | irregular three-dimensional needle boughs'];o.data.vertices[0].co.x+=.01;o.data.update()
 mutation['object']=o.name;mutation['mesh']=o.data.name;bpy.context.view_layer.update()
marker="asset_meshes={new:" if a.control.startswith('asset_') else 'check = snap()';assert code.count(marker)==1;code=code.replace(marker,'_negative_mutate();'+marker)
args=[]
for k in ['baseline','checkpoint','asset','asset-sha256','accepted-model','source-components']:args+=['--'+k,str(getattr(a,k.replace('-','_'))) ]
sys.argv=[a.validator,'--']+args+['--report',str(detail)];rejected=False;failure=None
try:exec(compile(code,a.validator,'exec'),{'__name__':'__main__','__file__':a.validator,'_negative_mutate':mutate})
except AssertionError as exc:
 failure={'message':str(exc),'traceback':traceback.format_exc()}
 expected={'asset_vertex':'Generated asset semantic mesh drift','asset_material':'Generated asset material graph/property drift','asset_transform':'Generated object transform drift','wrong_mask_vertex':'Unexpected owned group/weight set'}
 if a.control in expected:rejected=expected[a.control] in str(exc)
 elif detail.exists():d=json.loads(detail.read_text());rejected=not d['pass'] and mutation['mesh'] in d['source_differences']['meshes']
unchanged=all(sha(getattr(a,k))==v for k,v in inputs.items());r={'control':a.control,'rejected_at_intended_invariant':rejected,'failure':failure,'mutation_in_memory_only':mutation,'input_sha256':inputs,'all_inputs_unchanged':unchanged,'model_saved':False};out.write_text(json.dumps(r,indent=2));assert rejected and unchanged
