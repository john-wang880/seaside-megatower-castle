"""Independent mesh-ray checks on western stairs and ground contact."""
import argparse,bpy,bmesh,json,sys,math
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
body=bpy.data.objects['V009 | nine broad western approach treads'];ground=bpy.data.objects['V002 | western headland with solid rock shore'];apron=bpy.data.objects['V009 | terrain-following woodland entry apron']
def cast(o,start,direction):
 inv=o.matrix_world.inverted();h,v,n,i=o.ray_cast(inv@Vector(start),(inv.to_3x3()@Vector(direction)).normalized());return (o.matrix_world@v) if h else None
visible=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and not o.name.startswith(('Volume cloud','Air perspective'))]
samples=[]
for step in range(9):
 for dx in (.15,1,1.85):
  x=-90+step*2+dx
  for y in (36.6,37.3,38,38.7,39.4):
   top=cast(body,(x,y,40),(0,0,-1));rock=cast(ground,(x,y,40),(0,0,-1));assert top and rock
   foot=cast(body,(x,y,top.z-.02),(0,0,-1));assert foot
   blockers=[]
   for o in visible:
    hit=cast(o,top+Vector((0,0,.04)),(0,0,1))
    if hit is not None and 0<=hit.z-top.z<2.1:blockers.append(o.name)
   samples.append({'x':x,'y':y,'tread':top.z,'expected':25.8+.2*step,'ground':rock.z,'footing':foot.z,'blockers':blockers})
mesh_checks=[]
for o in (body,apron,bpy.data.objects['V009 | south approach parapet'],bpy.data.objects['V009 | north approach parapet']):
 bm=bmesh.new();bm.from_mesh(o.data);mesh_checks.append({'name':o.name,'nonmanifold':sum(not e.is_manifold for e in bm.edges),'volume':bm.calc_volume(signed=True)});bm.free()
entry=[]
for x in (-91.49,-91.25,-91,-90.75,-90.5,-90.25,-90.01):
 for y in (36.5,37.2,38,38.8,39.5):
  top=cast(apron,(x,y,40),(0,0,-1));g=cast(ground,(x,y,40),(0,0,-1));assert top and g
  blockers=[]
  for o in visible:
   hit=cast(o,top+Vector((0,0,.04)),(0,0,1))
   if hit is not None and 0<=hit.z-top.z<2.1:blockers.append(o.name)
  entry.append({'x':x,'y':y,'clearance':top.z-g.z,'blockers':blockers})
r={'samples':samples,'topology':mesh_checks,'entry_samples':entry,'treads_at_expected_heights':all(abs(q['tread']-q['expected'])<.002 for q in samples),'footings_embedded':all(q['ground']-q['footing']>.2 for q in samples),'treads_above_terrain':all(q['tread']>q['ground'] for q in samples),'headroom_clear':all(not q['blockers'] for q in samples),'new_architecture_closed':all(q['nonmanifold']==0 and q['volume']>0 for q in mesh_checks),'entry_headroom_clear':all(not q['blockers'] for q in entry),'entry_above_terrain':all(q['clearance']>=-.01 for q in entry)}
Path(a.report).write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if isinstance(v,bool)}));assert all(v for v in r.values() if isinstance(v,bool))
