"""In-memory fixture wrapper around the actual preservation gate; never saves."""
import bpy,sys,runpy,argparse,json,hashlib,traceback
from pathlib import Path
import sys
if sys.flags.optimize:raise RuntimeError('Optimized Python unsupported')
p=argparse.ArgumentParser();p.add_argument('--case',choices=['extra_mask_weight','old_v024_weight','old_v024_union','unrelated_hidden_source'],required=True);p.add_argument('--result',required=True);a,rest=p.parse_known_args(sys.argv[sys.argv.index('--')+1:]);result=Path(a.result);assert not result.exists();script=Path(__file__).with_name('export_preservation.py');original=bpy.ops.wm.open_mainfile;calls=0;mutated=None
# Blender operator wrappers cannot be reassigned reliably; inject fixture at the
# single explicit candidate-open statement in a fresh execution of frozen gate.
text=script.read_text();needle="o=bpy.data.objects[TARGET];assert len(o.modifiers)==3"
assert text.count(needle)==1
if a.case=='extra_mask_weight':inject="bpy.data.objects[TARGET].vertex_groups[1].add([104],1.0,'REPLACE');"
elif a.case=='old_v024_weight':inject="bpy.data.objects[TARGET].vertex_groups[0].add([16],.75,'REPLACE');"
elif a.case=='old_v024_union':inject="bpy.data.objects['V024 | exact evaluated rear stepped union'].data.vertices[0].co.x+=.125;"
else:inject="hidden=next(o for o in bpy.data.objects if o.type=='MESH' and o.hide_render and len(o.data.vertices));hidden.data.vertices[0].co.x+=.125;"
text=text.replace(needle,inject+needle);sys.argv=[str(script),'--']+rest
try:exec(compile(text,str(script),'exec'),{'__name__':'__main__','__file__':str(script)})
except AssertionError as e:
 tb=traceback.format_exc();expected=('line 32' in tb) if False else True
 # Expected guard: extra weight list, or final normalized raw/mesh source equality.
 if a.case in ['extra_mask_weight','old_v024_weight']:assert 'Raw old/new weights changed' in tb,tb
 elif a.case=='old_v024_union':assert 'Other active evaluated geometry changed' in tb,tb
 else:assert 'assert all(checks.values())' in tb,tb
 result.write_text(json.dumps({'pass':True,'case':a.case,'rejected':True,'gate_script_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),'failure':str(e),'traceback':tb,'scope':'Actual candidate loaded, in-memory mutation only; no model save.'},indent=2));print('EXPECTED MODEL NEGATIVE',a.case)
else:raise AssertionError('Mutation incorrectly accepted')
