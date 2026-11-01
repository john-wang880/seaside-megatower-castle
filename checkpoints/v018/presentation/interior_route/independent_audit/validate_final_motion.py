"""Independent camera recipe reconstruction/kinematics and continuous proxy proof.
Pure Python only. No rendering, Blender or source model changes.
"""
import argparse,ast,hashlib,json,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--motion-code',required=True);p.add_argument('--route-report',required=True);p.add_argument('--report',required=True);a=p.parse_args();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();P=json.load(open(a.plan));R=json.load(open(a.route_report));assert P['motion_code_sha256']==sha(a.motion_code);assert P['source_sha256']==R['model_sha256']=='c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd';assert R['continuous_envelope']['clear'] and R['route_acceptance_pass'];prisms=[r['bounds'] for r in R['continuous_envelope']['prisms']]
L=7+math.pi*.45/2+20.75;ARC=math.pi*.45/2;T=335/12;M=.18125/.6
assert P['fps']==12 and P['frame_count']==336 and P['encoded_duration_seconds']==28 and P['first_to_last_pose_seconds']==T
segments=P['time_segments'];gaze_knots=P['gaze_knots_seconds'];assert all(q['t1']>q['t0'] and min(q['v0'],q['v1'])>=0 for q in segments)
assert segments[0]['t0']==segments[0]['s0']==segments[0]['v0']==0 and abs(segments[-1]['s1']-L)<1e-10 and abs(segments[-1]['t1']-T)<1e-10 and segments[-1]['v1']==0
for i,q in enumerate(segments):
 assert abs(q['s1']-q['s0']-(q['t1']-q['t0'])*(q['v0']+q['v1'])/2)<1e-10
 if i:
  prior=segments[i-1];assert q['t0']==prior['t1'] and q['s0']==prior['s1'] and q['v0']==prior['v1']
def Q(u):
 u=max(0.,min(1.,u));return 10*u**3-15*u**4+6*u**5
def Q1(u):return 30*u**2-60*u**3+30*u**4 if 0<u<1 else 0.
def Q2(u):return 60*u-180*u**2+120*u**3 if 0<u<1 else 0.
def I(u):return 2.5*u**4-3*u**5+u**6
def distance(t):
 if t<=0:return 0.,0.,0.
 if t>=T:return L,0.,0.
 q=next(q for q in segments if t<=q['t1']);D=q['t1']-q['t0'];u=(t-q['t0'])/D;dv=q['v1']-q['v0'];return q['s0']+D*(q['v0']*u+dv*I(u)),q['v0']+dv*Q(u),dv*Q1(u)/D
def vertical(y):
 if y<=44.9:return 29.,0.,0.
 if y<45.5:
  u=(y-44.9)/.6;return 29+.18125*I(u),M*Q(u),M/.6*Q1(u)
 if y<=56.9:return 29+.090625+M*(y-45.5),M,0.
 if y<57.5:
  u=(y-56.9)/.6;return 32.534375+.18125*(u-I(u)),M*(1-Q(u)),-M/.6*Q1(u)
 return 32.625,0.,0.
def spatial(s):
 if s<7:x,y,x1,y1,x2,y2=-3+s,38.,1.,0.,0.,0.
 elif s<7+ARC:
  theta=(s-7)/.45-math.pi/2;x,y=4+.45*math.cos(theta),38.45+.45*math.sin(theta);x1,y1=-math.sin(theta),math.cos(theta);x2,y2=-math.cos(theta)/.45,-math.sin(theta)/.45
 else:x,y,x1,y1,x2,y2=4.45,38.45+s-7-ARC,0.,1.,0.,0.
 z,z1,z2=vertical(y);return [x,y,z+1.65],[x1,y1,z1*y1],[x2,y2,z2*y1*y1+z1*y2]
def gaze(t):
 yaw=pitch1=yaw1=yaw2=pitch2=0.;pitch=-5.
 for start,end,angle,tilt in [(gaze_knots['turn_start'],gaze_knots['turn_end'],90.,0.),(gaze_knots['arrival_start'],gaze_knots['arrival_end'],75.,8.)]:
  W=end-start;u=(t-start)/W;yaw+=angle*Q(u);pitch+=tilt*Q(u);yaw1+=angle*Q1(u)/W;pitch1+=tilt*Q1(u)/W;yaw2+=angle*Q2(u)/W**2;pitch2+=tilt*Q2(u)/W**2
 return yaw,pitch,yaw1,pitch1,yaw2,pitch2
def pose(t):
 s,v,acc=distance(t);loc,first,second=spatial(s);yaw,pitch,y1,p1,y2,p2=gaze(t);ya,pi=math.radians(yaw),math.radians(pitch);dr=[math.cos(ya)*math.cos(pi),math.sin(ya)*math.cos(pi),math.sin(pi)]
 return {'time_seconds':t,'distance_xy':s,'location':loc,'target':[loc[i]+4*dr[i] for i in range(3)],'yaw_degrees':yaw,'pitch_degrees':pitch,'horizontal_speed_mps':v,'speed_3d_mps':v*math.sqrt(sum(x*x for x in first)),'acceleration_3d_mps2':math.sqrt(sum((second[i]*v*v+first[i]*acc)**2 for i in range(3))),'yaw_rate_degrees_per_second':y1,'yaw_acceleration_degrees_per_second2':y2,'pitch_rate_degrees_per_second':p1,'pitch_acceleration_degrees_per_second2':p2}
errors={};indices=[]
for i,frame in enumerate(P['frames']):
 assert frame['index']==i+1 and frame['time_seconds']==i/12 and frame['lens']==26 and frame['clip_start']==.05 and frame['clip_end']==3000
 q=pose(i/12)
 for k,val in q.items():
  err=max(abs(x-y) for x,y in zip(val,frame[k])) if isinstance(val,list) else abs(val-frame[k]);errors[k]=max(errors.get(k,0),err)
 indices.append(frame['index'])
assert indices==list(range(1,337)) and max(errors.values())<1e-8
# Load only our previously reviewed pure union-coverage helper definitions,
# never executing a plan generator or top-level validator/report writes.
helper=Path(__file__).with_name('validate_path.py');tree=ast.parse(helper.read_text());funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('inside_box','union_covers')];scope={};exec(compile(ast.Module(body=funcs,type_ignores=[]),str(helper),'exec'),scope);covers=scope['union_covers']
knots=sorted(set([L*i/math.ceil(L/.05) for i in range(math.ceil(L/.05)+1)]+[7,7+ARC]));intervals=[]
for lo,hi in zip(knots,knots[1:]):
 p0,p1=spatial(lo)[0],spatial(hi)[0];box=[[x-.1201 for x in p0],[x+.1201 for x in p1]];okay,detail=covers(box,prisms);assert okay,(lo,hi,detail);intervals.append({'s_interval':[lo,hi],'box':box,**detail})
# Entire t-domain is covered because s(t) is continuous monotone0..L and
# x,y,z remain coordinatewise monotone. Revised vertical law is included here.
metrics=['horizontal_speed_mps','speed_3d_mps','acceleration_3d_mps2','yaw_rate_degrees_per_second','yaw_acceleration_degrees_per_second2','pitch_rate_degrees_per_second','pitch_acceleration_degrees_per_second2'];maxima={k:{'absolute':-1} for k in metrics};arrival_max={'absolute':-1}
N=100000
for i in range(N+1):
 t=T*i/N;q=pose(t)
 for k in metrics:
  if abs(q[k])>maxima[k]['absolute']:maxima[k]={'absolute':abs(q[k]),'signed':q[k],'time':t,'fractional_frame':1+12*t,'distance_xy':q['distance_xy']}
 if t>=gaze_knots['arrival_start'] and abs(q['yaw_rate_degrees_per_second'])>arrival_max['absolute']:arrival_max={'absolute':abs(q['yaw_rate_degrees_per_second']),'time':t,'fractional_frame':1+12*t}
# Polynomial endpoint identities give exact C2 scalar speed and gaze joins;
# finite one-sided probes only quantify numeric reconciling errors.
assert Q(0)==0 and Q(1)==1 and Q1(0)==Q1(1)==Q2(0)==Q2(1)==0
join_probes=[]
for q in segments[:-1]:
 t=q['t1'];before=pose(t-1e-7);after=pose(t+1e-7);join_probes.append({'time':t,'speed_difference':abs(before['horizontal_speed_mps']-after['horizontal_speed_mps']),'yaw_rate_difference':abs(before['yaw_rate_degrees_per_second']-after['yaw_rate_degrees_per_second']),'yaw_acceleration_difference':abs(before['yaw_acceleration_degrees_per_second2']-after['yaw_acceleration_degrees_per_second2'])})
# Eye height at every staircase riser, including one-sided limits.
height_extrema=[]
for i in range(20):
 y=45.5+i*.6;z=vertical(y)[0]+1.65;height_extrema += [z-(29+i*.18125),z-(29+(i+1)*.18125)]
assert abs(min(height_extrema)-1.559375)<1e-10 and abs(max(height_extrema)-1.740625)<1e-10
near=math.sqrt(.05**2+(.05*36/(2*26))**2*(1+(694/960)**2));assert near<.12 and P['resolution']==[960,694] and P['sensor_width_mm']==36 and P['sensor_fit']=='HORIZONTAL'
assert len(P['pilot_indices'])==25 and set(P['pilot_indices'])=={i for w in P['pilot_windows'] for i in w}|{336}
rows=[]
for window in P['pilot_windows']:
 frames=[P['frames'][i-1] for i in window];rows.append({'indices':window,'yaw_range':[min(q['yaw_degrees'] for q in frames),max(q['yaw_degrees'] for q in frames)],'distance_range':[min(q['distance_xy'] for q in frames),max(q['distance_xy'] for q in frames)],'max_sampled_yaw_rate':max(q['yaw_rate_degrees_per_second'] for q in frames)})
angular_exact={'maximum_yaw_rate':max(angle*1.875/(end-start) for start,end,angle in [(gaze_knots['turn_start'],gaze_knots['turn_end'],90),(gaze_knots['arrival_start'],gaze_knots['arrival_end'],75)]),'maximum_yaw_acceleration':max(angle*(10*math.sqrt(3)/3)/(end-start)**2 for start,end,angle in [(gaze_knots['turn_start'],gaze_knots['turn_end'],90),(gaze_knots['arrival_start'],gaze_knots['arrival_end'],75)]),'maximum_pitch_rate':8*1.875/(gaze_knots['arrival_end']-gaze_knots['arrival_start']),'maximum_pitch_acceleration':8*(10*math.sqrt(3)/3)/(gaze_knots['arrival_end']-gaze_knots['arrival_start'])**2}
assert gaze_knots['turn_end']<gaze_knots['arrival_start']
r={'exact_quintic_angular_maxima':angular_exact,'pass_geometry_and_recipe':True,'source_sha256':P['source_sha256'],'plan_sha256':sha(a.plan),'motion_code_sha256':sha(a.motion_code),'route_report_sha256':sha(a.route_report),'all336poses_independently_reconstructed':True,'max_pose_field_errors':errors,'continuous_interval_count':len(intervals),'continuous_intervals':intervals,'continuous_proof':'Independent revised vertical law is monotone; endpoint extrema enclose every analytic spatial segment. Full radius0.12+0.0001 axis boxes partitioned by all static validated-prism faces and entire cells covered. Continuous monotone quintic speed maps entire time range onto certified0..L; not a dense-point-only clearance claim.','exact_eye_height_bounds':[min(height_extrema),max(height_extrema)],'near_plane_radius_target960x694':near,'speed_and_gaze_C2_joins_from_polynomial_identities':True,'join_probes':join_probes,'translation_limit':'XY arc joins are C1 notC2 at nonzero speed: acceleration jump0.35²/0.45=0.272222m/s²; no zero-jerk/globalC2translation claim.','dense_kinematic_maxima':maxima,'dense_maxima_scope':'Independent100001samples, not analytic global extremum certification; exact segment endpoint identities separately checked.','arrival_yaw_rate_peak':arrival_max,'actual_display_timestamps':[0,T],'encoded_duration_with_last_frame_hold':28,'pilot_window_motion_coverage':rows,'pilot_indices':P['pilot_indices'],'extra_terminal_pilot_frame':336,'concerns':['Pilot windows now include peak anticipatoryyaw rate and actual terminal gaze transition; review actualmotion before fullremaining312frames.','Position remains C1 at circle joins, not globallyC2; bounded translation acceleration step is explicitly disclosed.'],'scope':'Camera/head clearance and recipe correctness only; not human body/gait/accessibility. Actual final pilot receipts/render usability still pending.'}
Path(a.report).write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='continuous_intervals'},indent=2))
