"""Independent ray and preservation checks on the saved western bridgehead."""
import bpy,json,bmesh,sys,argparse
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
results=[]
for y in (36.6,38.0,39.4):
 for z in (27.6,28.4,29.4):
  blockers=[]
  for ob in bpy.data.objects:
   if ob.type!='MESH' or ob.hide_render or ob.name.startswith(('Volume cloud','Air perspective')):continue
   inv=ob.matrix_world.inverted();origin=Vector((-72,y,z));direction=Vector((1,0,0))
   hit,loc,n,face=ob.ray_cast(inv@origin,(inv.to_3x3()@direction).normalized())
   if hit:
    world=ob.matrix_world@loc;dist=(world-origin).dot(direction)
    if -.001<=dist<=16.5:blockers.append({'object':ob.name,'x':world.x})
  results.append({'y':y,'z':z,'blockers':blockers})
meshes=[]
for ob in bpy.data.objects:
 if ob.type=='MESH' and ob.name.startswith('V007 |') and not ob.name.startswith('V007 | woodland'):
  bm=bmesh.new();bm.from_mesh(ob.data);meshes.append({'name':ob.name,'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges)});bm.free()
r={'ray_samples':results,'new_mesh_topology':meshes,'all_rays_clear':all(not r['blockers'] for r in results),'all_meshes_closed':all(m['nonmanifold_edges']==0 for m in meshes)}
Path(a.report).write_text(json.dumps(r,indent=2));print(json.dumps(r));assert r['all_rays_clear'] and r['all_meshes_closed']
