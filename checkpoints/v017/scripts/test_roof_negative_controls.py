"""One deliberate in-memory corruption per fresh Blender process. Never saves."""
import argparse,bpy,bmesh,hashlib,json,runpy,sys,traceback
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--control',choices=['detached_tile','reversed_face','source_signature'],required=True);p.add_argument('--validator',required=True);p.add_argument('--baseline-model',required=True);p.add_argument('--baseline-audit',required=True);p.add_argument('--report',required=True);args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();candidate=Path(bpy.data.filepath).resolve();candidate_sha=sha(candidate);baseline=Path(args.baseline_model).resolve();baseline_sha=sha(baseline);assert candidate!=baseline
assert candidate_sha=='9ed12e2dd4e21ee91ff65848d3c11601332a690ea80a880fb31bf41f1d7dd943';assert baseline_sha=='d44a4cdecd11dab152fd656c624755369e575a0f342e2eb0bc2460475c6f65eb'
validator=Path(args.validator).resolve();report=Path(args.report).resolve();assert not report.exists(),'Do not overwrite prior evidence'
mutation={}
if args.control=='source_signature':
 o=bpy.data.objects['V002 | main crown slate and roof seams'];old=list(o.data.vertices[0].co);o.data.vertices[0].co.x+=.01;o.data.update();mutation={'object':o.name,'vertex':0,'before':old,'after':list(o.data.vertices[0].co)}
 expected='assert signature==base'
else:
 o=bpy.data.objects['V017 | main crown south slate courses'];me=o.data;seed=me.polygons[0].vertices[0];adj=[[] for _ in me.vertices]
 for e in me.edges:
  x,y=e.vertices;adj[x].append(y);adj[y].append(x)
 ids=set();todo=[seed]
 while todo:
  i=todo.pop()
  if i in ids:continue
  ids.add(i);todo.extend(j for j in adj[i] if j not in ids)
 assert 6<=len(ids)<=12
 if args.control=='detached_tile':
  delta=Vector((0,-18,9.65)).normalized()*.1
  for i in ids:me.vertices[i].co+=delta
  me.update();mutation={'object':o.name,'component_vertex_ids':sorted(ids),'translation':list(delta)};expected='tile bottom not strictly in actual source shell'
 else:
  bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table();bm.faces[0].normal_flip();bm.to_mesh(me);bm.free();me.update();mutation={'object':o.name,'face':0,'operation':'reverse one face winding in memory'};expected='unclosed/inconsistently oriented tile'
bpy.context.view_layer.update();probe=report.with_suffix('.unexpected_positive.json');assert not probe.exists()
sys.argv=[str(validator),'--','--report',str(probe),'--baseline-model',str(baseline),'--baseline-audit',str(Path(args.baseline_audit).resolve())]
rejected=False;failure=None
try:runpy.run_path(str(validator),run_name='__main__')
except AssertionError as exc:
 failure={'exception_type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()};rejected=expected in failure['traceback']
result={'control':args.control,'mutation_in_memory_only':mutation,'expected_failure_marker':expected,'rejected_at_expected_check':rejected,'failure':failure,'candidate_sha256':candidate_sha,'baseline_sha256':baseline_sha,'candidate_file_unchanged':sha(candidate)==candidate_sha,'baseline_file_unchanged':sha(baseline)==baseline_sha,'validator_sha256':sha(validator),'source_saved':False,'scope':'Deliberate negative fixture in fresh Blender process; original candidate and baseline files never saved or modified. This is not a real candidate defect.'}
report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));assert rejected and result['candidate_file_unchanged'] and result['baseline_file_unchanged'],'Negative control did not reject at expected invariant'
