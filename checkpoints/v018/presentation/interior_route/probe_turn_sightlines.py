import bpy,json,math,hashlib,sys
from pathlib import Path
from mathutils import Vector
import argparse
p=argparse.ArgumentParser();p.add_argument('--report',required=True);args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);output=Path(args.report).resolve();assert not output.exists() and output.parent.is_dir()
r=Path(__file__).resolve().parent;sys.path.insert(0,str(r));import final_motion as motion
sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();assert sha=='c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd'
s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();rows=[]
for j in range(181):
 t=1+j*.05;p=motion.pose(t);origin=Vector(p['location'])
 for target_y in (39.,39.5,40.):
  horizontal=math.hypot(4.45-origin.x,target_y-origin.y)
  if target_y<=origin.y+.1:continue
  target=Vector((4.45,target_y,origin.z-math.tan(math.radians(5))*horizontal));direction=target-origin;distance=direction.length
  hit,loc,norm,idx,obj,mat=s.ray_cast(deps,origin,direction.normalized(),distance=distance-.03)
  rows.append({'t':t,'s':p['distance_xy'],'origin':list(origin),'target_y':target_y,'yaw_degrees':math.degrees(math.atan2(direction.y,direction.x)),'blocked_before_target':hit,'hit_object':obj.name if hit else None,'hit_distance':(loc-origin).length if hit else None})
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==sha
output.write_text(json.dumps({'source_sha256':sha,'source_saved':False,'scope':'Actual evaluated scene first-ray hits to beyond-bend points, not wholeframevisibility/illumination proof.','rays':rows},indent=2)+'\n')
for y in (39.,39.5,40.):
 selected=[x for x in rows if x['target_y']==y];lastblocked=max((x['t'] for x in selected if x['blocked_before_target']),default=None);print(y,'lastblocked',lastblocked,'earlyclear',[(x['t'],x['s']) for x in selected if not x['blocked_before_target']][:1])
