import bpy,json,math,hashlib,sys
from pathlib import Path
from mathutils import Vector
import argparse
p=argparse.ArgumentParser();p.add_argument('--report',required=True);args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);output=Path(args.report).resolve();assert not output.exists() and output.parent.is_dir()
root=Path(__file__).resolve().parent;sys.path.insert(0,str(root.resolve()));import final_motion as f
sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();assert sha=='c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd';scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
def ray(t):
 p=f.pose(t);origin=Vector(p['location']);direction=(Vector(p['target'])-origin).normalized()
 hit,loc,norm,idx,obj,mat=scene.ray_cast(deps,origin,direction,distance=200)
 r={'time_seconds':t,'yaw_degrees':p['yaw_degrees'],'position':p['location'],'first_hit_distance':(loc-origin).length if hit else None,'first_hit_object':obj.name if hit else None}
 if t<=10:
  # Before crossing just-beyond-bend plane, test entire sightline to that opening.
  length=(39.5-origin.y)/direction.y if origin.y<39.45 else 2.
  h,l,n,i,o,m=scene.ray_cast(deps,origin,direction,distance=max(.05,length-.03))
  r.update({'affected_gaze_check_length_m':max(.05,length-.03),'blocked_before_opening_or_2m_forward':h,'blocker':o.name if h else None})
 return r
frames=[dict(index=i+1,**ray(i/12)) for i in range(336)]
dense=[ray(i*.01) for i in range(1001)];fail=[x for x in dense if x.get('blocked_before_opening_or_2m_forward')]
r={'source_sha256':sha,'motion_code_sha256':hashlib.sha256((root/'final_motion.py').read_bytes()).hexdigest(),'plan_sha256':hashlib.sha256((root/'final_plan.json').read_bytes()).hexdigest(),'all336_actual_pose_center_rays':frames,'dense_affected_0to10s_rays':dense,'dense_opening_sightline_failures':fail,'affected_opening_center_sightlines_pass':not fail,'scope':'Actualevaluatedscene center-ray visibility atall336poses plus.01saffectedinterval samples. Not allpixels norcontinuousmathematicalocclusion proof. Camera/head collisionproof remainsseparate, unchangedpositions.','source_saved':False};assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==sha;output.write_text(json.dumps(r,indent=2)+'\n');print('Failures',len(fail));assert not fail
