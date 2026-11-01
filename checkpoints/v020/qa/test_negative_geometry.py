"""Inject in-memory geometry corruptions into actual forward validator; never save."""
import argparse,bpy,hashlib,json,sys,traceback
from pathlib import Path
p=argparse.ArgumentParser()
for k in ['candidate','specification','host-plan','validator','report']:p.add_argument('--'+k,required=True)
p.add_argument('--control',choices=['opening_intrusion','floating_piece','unrelated_neighbor'],required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(a.candidate);out=Path(a.report);assert not out.exists();detail=out.with_suffix('.validator.json');code=Path(a.validator).read_text();marker='rows=[];failures=[];new=[]';assert code.count(marker)==1;mutation={};created=[]
def mutate():
 import mathutils
 o=bpy.data.objects['V020 candidate | west portal radial stones'];adj={v.index:[] for v in o.data.vertices}
 for e in o.data.edges:
  x,y=e.vertices;adj[x].append(y);adj[y].append(x)
 seen={0};todo=[0]
 while todo:
  v=todo.pop()
  for n in adj[v]:
   if n not in seen:seen.add(n);todo.append(n)
 ids=sorted(seen);im={v:i for i,v in enumerate(ids)}
 if a.control=='unrelated_neighbor':
  fs=[tuple(im[i] for i in f.vertices) for f in o.data.polygons if all(i in seen for i in f.vertices)];me=bpy.data.meshes.new('QA unapproved neighbor');me.from_pydata([o.data.vertices[i].co for i in ids],[],fs);me.update();obj=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(obj);created.append(obj)
 else:
  center=sum((o.data.vertices[i].co for i in ids),mathutils.Vector())/len(ids)
  delta=mathutils.Vector((-10,0,0)) if a.control=='floating_piece' else mathutils.Vector((-71.25,38,28.5))-center
  for i in ids:o.data.vertices[i].co+=delta
  o.data.update()
 bpy.context.view_layer.update()
code=code.replace(marker,'_negative_mutate();counts=(len(bpy.data.objects),len(bpy.data.meshes))\n'+marker);sys.path.insert(0,str(Path(a.validator).resolve().parent));sys.argv=[a.validator,'--','--candidate',a.candidate,'--specification',a.specification,'--host-plan',a.host_plan,'--report',str(detail)];error=None
try:exec(compile(code,a.validator,'exec'),{'__name__':'__main__','__file__':a.validator,'_negative_mutate':mutate})
except AssertionError as exc:error={'message':str(exc),'traceback':traceback.format_exc()}
finally:
 for obj in created:me=obj.data;bpy.data.objects.remove(obj,do_unlink=True);bpy.data.meshes.remove(me)
result=json.loads(detail.read_text()) if detail.exists() else None;rejected=False
if result:
 if a.control=='opening_intrusion':rejected=any(x.get('reason')=='opening' for x in result['failures'])
 elif a.control=='floating_piece':rejected=any(x.get('reason')=='No proven positive host overlap' for x in result['failures'])
 else:rejected=any(x.get('reason')=='unapproved_neighbor_contact' and x.get('neighbor','').startswith('QA unapproved neighbor::') for x in result['failures'])
r={'control':a.control,'candidate_sha256':before,'rejected_at_intended_invariant':rejected,'failure':error,'candidate_unchanged':sha(a.candidate)==before,'model_saved':False};out.write_text(json.dumps(r,indent=2));assert rejected and r['candidate_unchanged']
