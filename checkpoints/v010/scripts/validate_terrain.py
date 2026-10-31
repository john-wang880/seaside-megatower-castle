import bpy,json,argparse,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser();p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);o=bpy.data.objects['V010 | headland with local stair-edge clearance'];body=bpy.data.objects['V008 | eastern stepped approach embedded in rock'];verts=[o.matrix_world@v.co for v in o.data.vertices];changes={}
for i,z in changes.items():verts[i].z=z
bvh=BVHTree.FromPolygons(verts,[tuple(p.vertices) for p in o.data.polygons]);inv=body.matrix_world.inverted();violations=[];minmargin=999;localmin=999;samples=0
for i in range(255):
 x=-15.99+i*.05
 if x>=-3.3:continue
 for j in range(92):
  y=35.705+j*.05
  g,n,f,d=bvh.ray_cast(Vector((x,y,60)),Vector((0,0,-1)));h,s,n,sf=body.ray_cast(inv@Vector((x,y,60)),inv.to_3x3()@Vector((0,0,-1)))
  if g is None or not h:continue
  samples+=1;s=body.matrix_world@s;margin=s.z-g.z;minmargin=min(minmargin,margin)
  if -13.5<x<-10.5 and y<37.2:localmin=min(localmin,margin)
  if margin<.08:violations.append({'x':x,'y':y,'margin':margin,'face':f,'stair_z':s.z,'ground_z':g.z})
r={'actual_saved_mesh':True,'samples':samples,'global_min_margin':minmargin,'local_patch_min_margin':localmin,'below_08_margin':violations,'source_model_modified':False};Path(a.report).write_text(json.dumps(r,indent=2));print('DONE',samples,minmargin,len(violations));print(violations[:12])

assert minmargin>0 and localmin>.08
