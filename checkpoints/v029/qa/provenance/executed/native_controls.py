"""Focused native mutation controls of exact same attribute snapshots used by preservation."""
import sys,json,hashlib,argparse
from pathlib import Path
sys.dont_write_bytecode=True
if sys.flags.optimize:raise RuntimeError('Optimization refused')
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent));import snapshot_support as ss
p=argparse.ArgumentParser()
for k in ['candidate','candidate-sha','payload','report']:p.add_argument('--'+k,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(a.candidate)==a.candidate_sha;assert not Path(a.report).exists();d=json.loads(Path(a.payload).read_text());bpy.ops.wm.open_mainfile(filepath=str(Path(a.candidate).resolve()),load_ui=False,use_scripts=False);t=d['targets'][0];o=bpy.data.objects[t['object']];tests=[]
def case(name,get,mutate,restore):
 before=get();mutate();bpy.context.view_layer.update();rejected=get()!=before;restore();bpy.context.view_layer.update();assert rejected and get()==before,name;tests.append({'name':name,'changed_snapshot_rejected':True,'restored_exact':True})
g=o.vertex_groups[t['group_name']];vid=t['raw_vertex_ids'][0]
case('wrong_owned_weight',lambda:ss.mesh_snapshot(o.data),lambda:g.add([vid],.5,'REPLACE'),lambda:g.add([vid],1.,'REPLACE'))
m=o.modifiers[t['mask_name']];case('wrong_mask_inversion',lambda:ss.primitive(m),lambda:setattr(m,'invert_vertex_group',False),lambda:setattr(m,'invert_vertex_group',True))
mat=bpy.data.materials['Citadel • weathered limestone'];old=tuple(mat.diffuse_color);case('source_material_change',lambda:ss.digest({'properties':ss.primitive(mat),'nodes':ss.tree_snapshot(mat.node_tree)}),lambda:setattr(mat,'diffuse_color',(.123,.234,.345,1)),lambda:setattr(mat,'diffuse_color',old))
other=bpy.data.objects['V012 | entrance hall ceiling lining'].data;old=other.vertices[0].co.copy();case('unrelated_source_vertex',lambda:ss.mesh_snapshot(other),lambda:setattr(other.vertices[0],'co',old+__import__('mathutils').Vector((.125,0,0))),lambda:setattr(other.vertices[0],'co',old))
assert sha(a.candidate)==a.candidate_sha;Path(a.report).write_text(json.dumps({'pass':True,'candidate_sha256':a.candidate_sha,'controls':tests,'scope':'Four focused in-memory native mutations exercise snapshot predicates; not four complete full-scene reruns. No save.'},indent=2));print('FOUR NATIVE CONTROLS PASS')
