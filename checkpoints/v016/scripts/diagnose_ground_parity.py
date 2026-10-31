"""Independent actual-surface sampling: no builder profiles, no model saves.
Bounded sample evidence only, not an all-surface embedding or structural claim.
"""
import bpy,argparse,sys,json,hashlib
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser();p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(bpy.data.filepath);canonical=Path('work/v015/castle_v015.blend');sha=hashlib.sha256(source.read_bytes()).hexdigest();canon=hashlib.sha256(canonical.read_bytes()).hexdigest();assert canon=='578ff47936800fe2a651237b609d95090cd97fefa686a208f8215d57628ac389'
dg=bpy.context.evaluated_depsgraph_get();before=(len(bpy.data.objects),len(bpy.data.meshes))
def geometry(name):
 o=bpy.data.objects[name];assert not o.hide_render and not o.hide_get();eo=o.evaluated_get(dg);me=eo.to_mesh();vs=[eo.matrix_world@v.co for v in me.vertices];fs=[list(f.vertices) for f in me.polygons]
 edges=Counter(tuple(sorted((f[i],f[(i+1)%len(f)]))) for f in fs for i in range(len(f)));assert all(n==2 for n in edges.values()),name+' not closed'
 me.calc_loop_triangles();tris=[tuple(t.vertices) for t in me.loop_triangles];tree=BVHTree.FromPolygons(vs,tris,all_triangles=True);bounds=[[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]];eo.to_mesh_clear();return tree,bounds,len(vs),len(fs)
core,bb,cv,cf=geometry('V016 | offshore terrain-following stair core');rock,rb,rv,rf=geometry('Western citadel_West_Sea stack basalt')
dirs=[Vector((1,.317,.173)).normalized(),Vector((.229,1,.419)).normalized(),Vector((.391,.271,1)).normalized()]
def parity(point,direction):
 q=point.copy();n=0
 for _ in range(128):
  hit,normal,index,distance=rock.ray_cast(q,direction,1000)
  if hit is None:return n%2,n
  q=hit+direction*.0001;n+=1
 return None,n

r=json.load(open('work/v016/reports/independent_grounding_v2.json'))
for row in r['failures']:
 q=Vector(row['point']);events=[]
 for i in range(12):
  hit,normal,index,d=rock.ray_cast(q,dirs[0],1000)
  if hit is None:break
  events.append({'point':list(hit),'distance':d,'normal':list(normal),'index':index});q=hit+dirs[0]*.0001
 print('TRACE',row['point'],events)
