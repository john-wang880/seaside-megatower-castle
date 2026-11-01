import json,hashlib,math,sys
from pathlib import Path
import final_motion as f
import argparse
r=Path(__file__).resolve().parent
a=argparse.ArgumentParser();a.add_argument('--old-plan',type=Path,default=r/'historical_v1_plan.json');a.add_argument('--output',type=Path,required=True);args=a.parse_args();assert not args.output.exists();old=json.loads(args.old_plan.read_text());p=dict(old)
poses=[f.pose(i/12) for i in range(336)];dense=[f.pose(f.MOTION_SECONDS*i/40000) for i in range(40001)]
p['status']='V2 opening-target gaze revision, unrendered/unaccepted; oldpilot remained rejected for fullcontinuation'
p['revision']='gaze_v2_actual_opening_target';p['motion_code_sha256']=hashlib.sha256((r/'final_motion.py').read_bytes()).hexdigest();p['frames']=[{'index':i+1,'time_seconds':q['time_seconds'],'recipe':{k:q[k] for k in ('location','target','lens','clip_start','clip_end')},'yaw_degrees':q['yaw_degrees'],'pitch_degrees':q['pitch_degrees']} for i,q in enumerate(poses)]
p['gaze_revision']={'opening_target_xy':list(f.OPENING_TARGET),'interpolation':'QuinticHermite yawtime spline withsharedpositions/velocities/accelerations atalljoins','spline':f.YAW_SPLINES,'node_derivatives':'symmetric.02s finite-difference rawtargetangle, frozenintopolynomialcoefficients; not anexactrawlookatclaim','maximum_dense_rawtarget_error_degrees':max(abs(f.opening_yaw(t/4000*10)[0]-f.raw_opening_yaw(t/4000*10)) for t in range(4001))}
p['dense_metrics']={k:max(abs(q[k]) for q in dense) for k in ('horizontal_speed_mps','speed_3d_mps','acceleration_3d_mps2','yaw_rate_degrees_per_second','yaw_acceleration_degrees_per_second2','pitch_rate_degrees_per_second','pitch_acceleration_degrees_per_second2')}
p['pilot_windows']=[list(range(1,9)),list(range(54,62)),list(range(76,84))];p['pilot_indices']=sum(p['pilot_windows'],[])+[336];p['pilot_scope']='GazeV2 affectedapproach/turn/settle25frame pilot only; newidentity,newoutput. Oldarrivalframes retained solelycomparative evidence, notnewversionrenders.'
p['positions_and_speed_unchanged']=all(q['location']==old['frames'][i]['recipe']['location'] for i,q in enumerate(poses));assert p['positions_and_speed_unchanged']
args.output.write_text(json.dumps(p,indent=2)+'\n');print(p['dense_metrics']);print('maxrawerror',p['gaze_revision']['maximum_dense_rawtarget_error_degrees'])
