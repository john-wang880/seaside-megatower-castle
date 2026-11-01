"""Pure Python independent polynomial/root audit; no source or approval writes."""
import json,hashlib,importlib.util,ast,math,argparse
from pathlib import Path
import numpy as np
from numpy.polynomial import Polynomial as Poly
parser=argparse.ArgumentParser()
for key in ['new-plan','new-motion','old-plan','old-motion','old-proof','report']:parser.add_argument('--'+key,required=True)
args=parser.parse_args();new_plan=Path(args.new_plan);new_motion=Path(args.new_motion);old_plan=Path(args.old_plan);old_motion=Path(args.old_motion);old_proof=Path(args.old_proof)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('gaze_v2',new_motion);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=json.loads(new_plan.read_text());o=json.loads(old_plan.read_text());proof=json.loads(old_proof.read_text())
assert proof['pass_geometry_and_recipe'];assert sha(new_motion)==p['motion_code_sha256']
# Direct AST identity closes all continuous trajectory functions, not just baked poses.
def funcs(path):return {x.name:ast.dump(x,include_attributes=False) for x in ast.parse(path.read_text()).body if isinstance(x,ast.FunctionDef)}
ospec=importlib.util.spec_from_file_location('old_motion',old_motion);om=importlib.util.module_from_spec(ospec);ospec.loader.exec_module(om)
for key in ['R','STRAIGHT','ARC','LENGTH','FPS','COUNT','MOTION_SECONDS','M','CRUISE','SEGMENTS','END_GAZE_TIME_START','END_GAZE_TIME_END']:assert getattr(m,key)==getattr(om,key)
assert proof['motion_code_sha256']==sha(old_motion) and proof['source_sha256']==p['source_sha256']
f,g=funcs(new_motion),funcs(old_motion);same=['S','Sd','Sdd','G','make_segments','distance_at','vertical','xy','time_at_distance','pose'];assert all(f[n]==g[n] for n in same)
assert p['time_segments']==o['time_segments'] and p['source_sha256']==o['source_sha256'] and len(p['frames'])==336
for k in ['resolution','sensor_width_mm','sensor_fit','camera_proxy_radius_m','expected_cycles','expected_render_except_filepath','expected_view_settings','expected_image_settings']:assert p[k]==o[k]
maxerr=0
for a,b in zip(p['frames'],o['frames']):
 for key in ['index','time_seconds']:assert a[key]==b[key]
 for key in ['location','lens','clip_start','clip_end']:assert a['recipe'][key]==b['recipe'][key]
 q=m.pose(a['time_seconds']);assert a['recipe']['location']==q['location'];assert a['recipe']['target']==q['target'];assert a['yaw_degrees']==q['yaw_degrees'] and a['pitch_degrees']==q['pitch_degrees']
 if a['time_seconds']>=10:assert a==b
assert p['gaze_revision']['spline']==m.YAW_SPLINES
segments=[];maxjoin=[0.,0.,0.];peaks=[0.,0.];yawmin=1e9;yawmax=-1e9
for j,s in enumerate(m.YAW_SPLINES):
 D=s['t1']-s['t0'];q=Poly(s['coefficients']);assert D>0
 ranges=[]
 for order in range(3):
  v=q.deriv(order)/D**order;critical=[0.,1.]+[float(r.real) for r in v.deriv().roots() if abs(r.imag)<1e-8 and 0<r.real<1];vals=[float(v(u)) for u in critical];ranges.append([min(vals),max(vals)])
  if order:peaks[order-1]=max(peaks[order-1],max(abs(x) for x in vals))
 yawmin=min(yawmin,ranges[0][0]);yawmax=max(yawmax,ranges[0][1])
 if j:
  prev=m.YAW_SPLINES[j-1];assert prev['t1']==s['t0'];v=Poly(prev['coefficients']);pd=prev['t1']-prev['t0']
  for order in range(3):maxjoin[order]=max(maxjoin[order],abs(v.deriv(order)(1)/pd**order-q.deriv(order)(0)/D**order))
 segments.append({'t0':s['t0'],'t1':s['t1'],'ranges_yaw_rate_acceleration':ranges})
assert max(maxjoin)<1e-7 and peaks[0]<27 and peaks[1]<28 and yawmin>0 and yawmax<90.01
for t in np.linspace(0,10,10001):maxerr=max(maxerr,abs(m.opening_yaw(float(t))[0]-m.raw_opening_yaw(float(t))))
assert maxerr<.002
assert max(abs(x) for x in m.opening_yaw(0)[1:])==0 and max(abs(x) for x in m.opening_yaw(10)[1:])==0
report={'pass':True,'scope':'C2 piecewise quintic gaze and immutable continuous spatial/timing recipe. No actual V2 render or continuous occlusion certification.','plan_sha256':sha(new_plan),'motion_sha256':sha(new_motion),'source_sha256':p['source_sha256'],'old_plan_sha256':sha(old_plan),'inherited_continuous_proxy_proof_sha256':sha(old_proof),'continuous_functions_ast_identical':same,'all_336_locations_timestamps_camera_gates_exact':True,'arrival_frames_after_10_seconds_exact':True,'historical_arrival_303_to_310_recipes_exact':all(p['frames'][i-1]==o['frames'][i-1] for i in range(303,311)),'historical_arrival_note':'Recipe equality only; prior rendered frames are not relabeled or reused in the new run.','exact_polynomial_extrema_max_yaw_rate_acceleration':peaks,'max_join_C0_C1_C2_error':maxjoin,'yaw_global_range':[yawmin,yawmax],'dense_raw_target_angle_error_max_deg':maxerr,'segments':segments,'nearplane_proof_rebinding':'Unchanged position functions, timing segments, sensor/lens/resolution/clip and radius0.12 preserve orientation-invariant sphere coverage. Actual new camera receipts must still match.','limits':['Existing C1 translation lateral acceleration jump remains unchanged.','Exact polynomial extrema are roots solved numerically in float64, checked over every segment; raw-target deviation only sampled.','181 source rays do not prove all continuous gaze rays or entire viewport clear. Actual affected pilot must be visually accepted before full render.']}
Path(args.report).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='segments'},indent=2))
