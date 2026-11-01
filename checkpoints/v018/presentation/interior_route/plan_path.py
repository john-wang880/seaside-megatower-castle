"""Pure geometry recipe; no Blender, source edits or final-animation launch."""
import math,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent
SHA='c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd'
r=.45;straight=7.;arc=math.pi*r/2;north=59.2-38.45;total=straight+arc+north

def smooth(t):return 0 if t<=0 else 1 if t>=1 else t*t*(3-2*t)
def point(s):
 if s<straight:x,y,heading=-3+s,38,0
 elif s<straight+arc:
  theta=-math.pi/2+(s-straight)/r;x=4+r*math.cos(theta);y=38.45+r*math.sin(theta);heading=theta+math.pi/2
 else:x,y,heading=4.45,38.45+s-straight-arc,math.pi/2
 z=29+sum(.18125*smooth((y-(45.5+i*.6)+.3)/.6) for i in range(20))
 floor=29+min(20,max(0,math.floor((y-45.5)/.6)+1))*.18125
 eye=z+1.65;pitch=math.radians(-5)
 direction=[math.cos(heading)*math.cos(pitch),math.sin(heading)*math.cos(pitch),math.sin(pitch)]
 return {'distance_xy':s,'location':[x,y,eye],'target':[x+4*direction[0],y+4*direction[1],eye+4*direction[2]],'floor_z':floor,'eye_height_above_local_tread':eye-floor,'heading_radians':heading,'lens':26,'clip_start':.05,'clip_end':3000}
samples=[point(total*i/math.ceil(total/.01)) for i in range(math.ceil(total/.01)+1)]
length=sum(math.dist(a['location'],b['location']) for a,b in zip(samples,samples[1:]))
plan={'source_sha256':SHA,'source_frame_fixed':1,'status':'Feasibility only; no final timeline/render authorized','path':'Inside entrance centerline→rounded L-turn→north stair→bounded terrace y59.2','xy_length_m':total,'eye_path_length_m':length,'geometry':{'start':[-3,38],'straight_length':straight,'turn_center':[4,38.45],'turn_radius':r,'turn_angle_radians':[-math.pi/2,0],'north_end_y':59.2},'eye_height_nominal_m':1.65,'eye_height_range_sampled_m':[min(p['eye_height_above_local_tread'] for p in samples),max(p['eye_height_above_local_tread'] for p in samples)],'eye_rise_formula':'29+sum(0.18125*smoothstep((y-(45.5+i*.6)+.3)/.6),i0..19)+1.65; smoothstep clamped0..1','proxy':{'kind':'head/camera clearance proxy, not human gait/body certification','sphere_radius_m':.12,'sweep_method_requested':'Conservative swept axis-aligned segment boxes inside union of alreadyvalidated routeprisms, plus actual evaluated geometry tests if needed'},'camera':{'lens':26,'pitch_degrees':-5,'clip_start':.05,'clip_end':3000,'sensor_width_mm':36,'sensor_fit':'HORIZONTAL','preview_aspect':[640,462],'interpolation':'Analytic point(s) evaluated per actual rendered frame; no BlenderBezier interpolation. Finaltimeparameterization still pending.'},'speed_tradeoff':{'8second_average_mps':length/8,'12second_average_mps':length/12,'recommended_full_route_seconds':28,'recommended_fps':12,'recommended_real_frames':336,'turn_speed_cap_mps':.35,'turn_max_angular_speed_degrees_per_second':math.degrees(.35/r),'note':'Final timing requires smooth deceleration around Lturn andendpoints; no finaltiming implemented yet. Fullroute8–12s is accelerated,not ordinarywalking.'},'samples':samples}
(root/'path_plan.json').write_text(json.dumps(plan,indent=2)+'\n')
positions=[0,straight+arc*.5,straight+arc+(45.2-38.45),straight+arc+(53.3-38.45),total]
views={name:{k:p[k] for k in ('location','target','lens','clip_start','clip_end')} for name,p in zip(('entrance','turn','stair_base','upper_stair','terminal'),map(point,positions))}
(root/'keyframes.json').write_text(json.dumps({'source_sha256':SHA,'views':views},indent=2)+'\n');print(json.dumps({k:v for k,v in plan.items() if k!='samples'},indent=2))
