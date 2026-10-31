"""Unaccepted roof study: add shallow closed slate wedges, preserve all source data."""
import argparse,sys,json,hashlib,math
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import slate_math as sm
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--report',required=True);p.add_argument('--pitches',default='south,east,north,west');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(bpy.data.filepath).resolve();out=Path(a.output).resolve();report=Path(a.report).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='d44a4cdecd11dab152fd656c624755369e575a0f342e2eb0bc2460475c6f65eb';assert sha(source)==expected;assert not out.exists() and not report.exists() and out!=source
pitches=a.pitches.split(',');assert len(set(pitches))==len(pitches) and set(pitches)<={'south','east','north','west'} and pitches
roof=bpy.data.objects['V002 | main crown slate and roof seams'];assert roof.type=='MESH' and not roof.modifiers and len(roof.data.vertices)==166 and len(roof.data.polygons)==105
assert all(abs(roof.matrix_world[i][j]-(1 if i==j else 0))<1e-8 for i in range(4) for j in range(4))
expected_shell=[(21,32.6,192.55),(49,32.6,192.55),(49,60.4,192.55),(21,60.4,192.55),(35,42.25,210.55),(35,50.75,210.55)]
assert all((roof.data.vertices[i].co-Vector(v)).length<1e-4 for i,v in enumerate(expected_shell))
material=bpy.data.materials['V002 | quiet blue-grey roof slate'];assert material in [s.material for s in roof.material_slots]
assert not any(o.name.startswith('V017 |') for o in bpy.data.objects)
params=sm.Parameters();tiles,discarded,stats=sm.generate(params);collection=bpy.data.collections.new('REFINEMENT | v017 crown slate courses');bpy.context.scene.collection.children.link(collection);added=[]
for pitch in pitches:
 selected=[t for t in tiles if t['pitch']==pitch];verts=[];faces=[]
 for t in selected:
  assert sm.manifold(t) and t['volume']>0
  offset=len(verts);verts.extend(t['vertices']);faces.extend([[offset+i for i in f] for f in t['faces']])
 name='V017 | main crown '+pitch+' slate courses';mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update(calc_edges=True);assert not mesh.validate(verbose=True,clean_customdata=False),'Unexpected mesh repair';mesh.materials.append(material)
 obj=bpy.data.objects.new(name,mesh);collection.objects.link(obj);obj['source_model_sha256']=expected;obj['design_status']='Source-preserving slate-course geometry; acceptance is documented in checkpoint validation reports';obj['pitch']=pitch;obj['parameters_json']=json.dumps(vars(params),sort_keys=True)
 added.append({'object':name,'tiles':len(selected),'vertices':len(mesh.vertices),'polygons':len(mesh.polygons),'material':material.name,'analytic_summed_volume_not_union':sum(t['volume'] for t in selected)})
assert sha(source)==expected
out.parent.mkdir(parents=True,exist_ok=True);report.parent.mkdir(parents=True,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
assert sha(source)==expected and out.exists()
r={'status':'UNACCEPTED visual prototype, not a published checkpoint','source_sha256':expected,'candidate_sha256':sha(out),'candidate_bytes':out.stat().st_size,'source_unchanged':True,'pitches':pitches,'parameters':vars(params),'added':added,'existing_objects_removed':0,'existing_materials_modified':0,'source_shell_ribs_finial_pinnacles_untouched':True,'intentional_overlap':'New tile bottoms embed below original shell; successive rows overlap as shallow noncoplanar wedges. Full source shell remains under joints/slivers.','limits':'Visual gain and deep semantic preservation require independent reopened checks. No waterproofing/historical/engineering claim.'}
report.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
