"""Inject one in-memory corruption after candidate open; never save scripts/models."""
import argparse,bpy,bmesh,hashlib,json,sys,traceback
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--baseline-model',required=True);p.add_argument('--candidate',required=True);p.add_argument('--design',required=True);p.add_argument('--validator',required=True);p.add_argument('--report',required=True);p.add_argument('--control',choices=['detached_tile','reversed_face','source_signature'],required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();source=Path(a.baseline_model).resolve();candidate=Path(a.candidate).resolve();hashes=(sha(source),sha(candidate));report=Path(a.report).resolve();detail=report.with_suffix('.validator.json');assert not report.exists() and not detail.exists();design=json.load(open(a.design));validator=Path(a.validator).resolve();code=validator.read_text();marker="bpy.ops.wm.open_mainfile(filepath=str(candidate.resolve()),use_scripts=False);assert not bpy.data.objects[TARGET].modifiers;assert source_signature";assert code.count(marker)==1;mutation={}
def mutate():
 roof=bpy.data.objects['V002 | western lantern low slate cap']
 if a.control=='source_signature':
  roof.data.vertices[0].co.x+=.01;roof.data.update();mutation.update({'object':roof.name,'vertex':0,'operation':'shift x0.01'});return
 obj=bpy.data.objects[design['objects'][0]];me=obj.data;seed=me.polygons[0].vertices[0];adj=[[] for _ in me.vertices]
 for e in me.edges:
  x,y=e.vertices;adj[x].append(y);adj[y].append(x)
 ids=set();todo=[seed]
 while todo:
  i=todo.pop()
  if i in ids:continue
  ids.add(i);todo.extend(j for j in adj[i] if j not in ids)
 if a.control=='detached_tile':
  delta=roof.data.polygons[2].normal.normalized()*.1
  for i in ids:me.vertices[i].co+=delta
  mutation.update({'object':obj.name,'vertices':sorted(ids),'translation':list(delta)})
 else:
  bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table();bm.faces[0].normal_flip();bm.to_mesh(me);bm.free();mutation.update({'object':obj.name,'face':0,'operation':'reverse winding'})
 me.update();bpy.context.view_layer.update()
code=code.replace(marker,marker.replace(';assert',';_qa_mutate();assert',1));sys.argv=[str(validator),'--','--baseline-model',str(source),'--candidate',str(candidate),'--design',str(Path(a.design).resolve()),'--report',str(detail)]
expected={'detached_tile':'tile bottom outside source shell','reversed_face':'tile closed orientation invalid','source_signature':'source roof signature changed'}[a.control];failure=None;rejected=False
try:exec(compile(code,str(validator),'exec'),{'__name__':'__main__','__file__':str(validator),'_qa_mutate':mutate})
except AssertionError as exc:failure={'message':str(exc),'traceback':traceback.format_exc()};rejected=expected in str(exc)
r={'control':a.control,'rejected_at_expected_invariant':rejected,'expected_marker':expected,'mutation_in_memory_only':mutation,'failure':failure,'baseline_sha256':hashes[0],'candidate_sha256':hashes[1],'baseline_unchanged':sha(source)==hashes[0],'candidate_unchanged':sha(candidate)==hashes[1],'source_saved':False};report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));assert rejected and r['baseline_unchanged'] and r['candidate_unchanged']
