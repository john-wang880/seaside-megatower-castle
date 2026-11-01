"""Compare exact persisted semantics of two fresh builds; no file writes except report."""
import argparse,bpy,json,sys,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from preservation_support import mesh_snapshot,primitive,tree_snapshot,digest
p=argparse.ArgumentParser();p.add_argument('--first',required=True);p.add_argument('--second',required=True);p.add_argument('--prototype');p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);paths=[Path(a.first).resolve(),Path(a.second).resolve()];hashes=[hashlib.sha256(x.read_bytes()).hexdigest() for x in paths]
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
 return {'meshes':{m.name:mesh_snapshot(m) for m in bpy.data.meshes},'objects':{o.name:{'type':o.type,'data':o.data.name if o.data else None,'matrix':[list(r) for r in o.matrix_world],'slots':[(x.link,x.material.name if x.material else None) for x in o.material_slots],'hidden':[o.hide_render,o.hide_viewport,o.hide_get()],'groups':[(g.name,g.index) for g in o.vertex_groups],'modifiers':[primitive(m) for m in o.modifiers],'custom':dict(o.items())} for o in bpy.data.objects},'materials':{m.name:digest({'properties':primitive(m),'nodes':tree_snapshot(m.node_tree)}) for m in bpy.data.materials},'lights':{x.name:digest({'properties':primitive(x),'nodes':tree_snapshot(x.node_tree)}) for x in bpy.data.lights},'worlds':{x.name:digest({'properties':primitive(x),'nodes':tree_snapshot(x.node_tree)}) for x in bpy.data.worlds},'cameras':{x.name:primitive(x) for x in bpy.data.cameras},'collections':{x.name:sorted(o.name for o in x.objects) for x in bpy.data.collections},'scene':{'camera':s.camera.name,'world':s.world.name,'cycles':primitive(s.cycles),'render':primitive(s.render),'view':primitive(s.view_settings),'frame':s.frame_current}}
x=snapshot(paths[0]);y=snapshot(paths[1]);checks={k:x[k]==y[k] for k in x};assert all(checks.values()),[k for k,v in checks.items() if not v]
prototype_match=None
if a.prototype:
 z=snapshot(Path(a.prototype).resolve());prototype_match={f'facet{i:02d}':x['meshes'][f'V018 | western slate facet {i:02d}']==z['meshes'][f'V018 prototype | western slate facet {i:02d}'] for i in range(1,9)};assert all(prototype_match.values())
assert [hashlib.sha256(x.read_bytes()).hexdigest() for x in paths]==hashes
Path(a.report).write_text(json.dumps({'first_sha256':hashes[0],'second_sha256':hashes[1],'checks':checks,'prototype_course_geometry_exact':prototype_match,'pass':True,'scope':'Exact persisted semantic equality, not binary identity; independent actual evaluated geometry/source checks separate.'},indent=2));print('REPEAT PASS')
