"""Read-only independent actual-mesh footing, tread, headroom and topology checks."""
import argparse,bmesh,bpy,json,sys
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
body=bpy.data.objects['V008 | eastern stepped approach embedded in rock'];ground=bpy.data.objects['Castle headland | level courtyard and broken coastal escarpment']
def cast(o,p,d):
 inv=o.matrix_world.inverted();hit,loc,n,idx=o.ray_cast(inv@p,(inv.to_3x3()@d).normalized())
 return (o.matrix_world@loc) if hit else None
samples=[]
for i in range(11):
 x=-15.5+i
 for y in (36.0,38.0,40.0):
  down=Vector((0,0,-1));top=cast(body,Vector((x,y,40)),down);assert top
  rock=cast(ground,Vector((x,y,40)),down);assert rock
  bottom=cast(body,top-Vector((0,0,.1)),down);assert bottom
  blockers=[]
  for o in bpy.data.objects:
   if o.type!='MESH' or o.hide_render or o.name.startswith(('Volume cloud','Air perspective')):continue
   start=top+Vector((0,0,.06));hit=cast(o,start,Vector((0,0,1)))
   if hit and -.001<=hit.z-start.z<2.1:blockers.append(o.name)
  samples.append({'x':x,'y':y,'actual_tread_z':top.z,'rock_z':rock.z,'actual_footing_z':bottom.z,'embed_depth':rock.z-bottom.z,'headroom_blockers':blockers})
meshes=[]
for o in bpy.data.objects:
 if o.type=='MESH' and o.name.startswith('V008 |') and not o.name.startswith('V008 | coastal rock'):
  bm=bmesh.new();bm.from_mesh(o.data);meshes.append({'name':o.name,'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume':bm.calc_volume(signed=True)});bm.free()
r={'actual_geometry_samples':samples,'topology':meshes,'footings_embedded':all(x['embed_depth']>.2 for x in samples),'treads_above_rock':all(x['actual_tread_z']>x['rock_z'] for x in samples),'headroom_clear':all(not x['headroom_blockers'] for x in samples),'new_meshes_closed':all(x['nonmanifold_edges']==0 and x['signed_volume']>0 for x in meshes)}
Path(a.report).write_text(json.dumps(r,indent=2));print(json.dumps(r));assert all(r[k] for k in ('footings_embedded','treads_above_rock','headroom_clear','new_meshes_closed'))
