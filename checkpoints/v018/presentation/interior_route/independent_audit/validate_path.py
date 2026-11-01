"""Pure-Python continuous analytic camera-head containment, no Blender/model IO.
Interval enclosures + exact axis-aligned union cells, not finite point occupancy.
"""
import argparse,hashlib,json,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--route-report',required=True);p.add_argument('--report',required=True);a=p.parse_args();P=json.load(open(a.plan));R=json.load(open(a.route_report));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert P['source_sha256']==R['model_sha256']=='c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd';E=R['continuous_envelope'];assert E['clear'] and R['route_acceptance_pass'];assert not E['collisions'] and not E['uncertain']
prisms=[q['bounds'] for q in E['prisms']];g=P['geometry'];assert g=={'start':[-3,38],'straight_length':7.,'turn_center':[4,38.45],'turn_radius':.45,'turn_angle_radians':[-math.pi/2,0],'north_end_y':59.2};radius=P['proxy']['sphere_radius_m'];assert radius==.12
straight=7.;arc=math.pi*.45/2;total=straight+arc+20.75
# Independently reconstructed clamped cubic; do not execute the owner's script.
def smooth(q):
 if q<=0:return 0.
 if q>=1:return 1.
 return 3*q*q-2*q*q*q
def pos(s):
 if s<=straight:x,y=-3+s,38.
 elif s<=straight+arc:
  angle=-math.pi/2+(s-straight)/.45;x=4+.45*math.cos(angle);y=38.45+.45*math.sin(angle)
 else:x,y=4.45,38.45+s-straight-arc
 eye=30.65+sum(.18125*smooth((y-45.5-i*.6+.3)/.6) for i in range(20));return [x,y,eye]
assert abs(total-P['xy_length_m'])<1e-10
sample_agreement=max(max(abs(x-y) for x,y in zip(pos(s['distance_xy']),s['location'])) for s in P['samples']);assert sample_agreement<1e-10
# x,y,z are globally nondecreasing: straight then quartercircle with nonnegative
# dx/ds,dy/ds then north; each clamped cubic has derivative6t(1−t)>=0.
# Thus endpoint extrema enclose EVERY continuous position in each interval.
knots=sorted(set([total*i/math.ceil(total/.05) for i in range(math.ceil(total/.05)+1)]+[straight,straight+arc]))
def envelope(lo,hi,r=radius):return [[x-r-.0001 for x in pos(lo)],[x+r+.0001 for x in pos(hi)]]
def inside_box(point,b,tol=1e-10):return all(b[0][k]-tol<=point[k]<=b[1][k]+tol for k in range(3))
def union_covers(box,boxes):
 candidates=[b for b in boxes if all(b[1][k]>=box[0][k] and b[0][k]<=box[1][k] for k in range(3))]
 if not candidates:return False,{'reason':'no_overlap'}
 cuts=[]
 for k in range(3):
  raw=sorted(set([box[0][k],box[1][k]]+[q for b in candidates for q in (b[0][k],b[1][k]) if box[0][k]<q<box[1][k]]));cc=[]
  for x in raw:
   if not cc or x-cc[-1]>1e-10:cc.append(x)
  cuts.append(cc)
 count=0
 for i in range(len(cuts[0])-1):
  for j in range(len(cuts[1])-1):
   for k in range(len(cuts[2])-1):
    low=[cuts[0][i],cuts[1][j],cuts[2][k]];high=[cuts[0][i+1],cuts[1][j+1],cuts[2][k+1]]
    # Each cell has constant cover membership: its boundaries include every
    # possible prism boundary. Test full low/high corners in ONE covering prism.
    if not any(inside_box(low,b) and inside_box(high,b) for b in candidates):return False,{'uncovered_cell':[low,high]}
    count+=1
 return True,{'cells':count}
rows=[];fail=[]
for lo,hi in zip(knots,knots[1:]):
 box=envelope(lo,hi);okay,detail=union_covers(box,prisms);row={'s_interval':[lo,hi],'swept_head_enclosure':box,'covered':okay,**detail};rows.append(row)
 if not okay:fail.append(row)
# Decisive continuous-union controls: slit missed by endpoint-only tests,
# positive touching union, obvious horizontal excursion and low stair camera.
controls={}
controls['touching_boxes_cover_join']=union_covers([[.9,.2,.2],[1.1,.8,.8]],[[[0,0,0],[1,1,1]],[[1,0,0],[2,1,1]]])[0]
controls['thin_internal_gap_rejected']=not union_covers([[.9,.2,.2],[1.1,.8,.8]],[[[0,0,0],[.999,1,1]],[[1.001,0,0],[2,1,1]]])[0]
bad=envelope(straight+arc+10,straight+arc+10.05);bad=[[x+(1 if k==0 else 0) for k,x in enumerate(v)] for v in bad];controls['sideways_excursion_rejected']=not union_covers(bad,prisms)[0]
bad=envelope(straight+arc+10,straight+arc+10.05);bad=[[x-(1.7 if k==2 else 0) for k,x in enumerate(v)] for v in bad];controls['lowered_camera_through_stair_rejected']=not union_covers(bad,prisms)[0]
assert all(controls.values())
# Additional route-union clearance, conservative around these interval boxes.
low,high=0.,.3
for _ in range(18):
 mid=(low+high)/2
 if all(union_covers(envelope(lo,hi,radius+mid),prisms)[0] for lo,hi in zip(knots,knots[1:])):low=mid
 else:high=mid
# Exact floor-relative limits are attained as one-sided riser limits. Sampled
# maximum in the input is slightly smaller because samples miss exact boundary.
height_limits=[1.65-.18125/2,1.65+.18125/2]
# Closed-form orientation-independent near-plane bound conditional on declared
# sensor gate; actual Blender view_frame measurement must verify this later.
clip=P['camera']['clip_start'];lens=P['camera']['lens'];sensor_width=P['camera']['sensor_width_mm'];assert P['camera']['sensor_fit']=='HORIZONTAL';assumed_aspect=P['camera']['preview_aspect'][0]/P['camera']['preview_aspect'][1];halfwidth=clip*sensor_width/(2*lens);halfheight=halfwidth/assumed_aspect;near_bound=math.sqrt(clip*clip+halfwidth*halfwidth+halfheight*halfheight)
r={'pass':not fail,'source_sha256':P['source_sha256'],'plan_sha256':sha(a.plan),'route_report_sha256':sha(a.route_report),'route_clearance_evidence':a.route_report,'planned_recipe_matches_independent_formula_max_error':sample_agreement,'sphere_radius':radius,'extra_numeric_inflation':.0001,'interval_count':len(rows),'intervals':rows,'failed_intervals':fail,'minimum_additional_axis_inflation_certified':low,'exact_one_sided_eye_height_limits_m':height_limits,'horizontal_distance_m':total,'reported_eye_path_distance_m':P['eye_path_length_m'],'average_eye_speed_mps':{str(t):P['eye_path_length_m']/t for t in (8,12,24,28)},'near_plane_conditional':{'sensor_width_mm':sensor_width,'aspect':assumed_aspect,'lens_mm':lens,'clip_start':clip,'corner_radius_bound_m':near_bound,'fits_head_sphere':near_bound<radius,'requires_actual_camera_view_frame_confirmation':True},'negative_and_union_controls':controls,'proven_scope':'Continuous analytic planned camera/head sphere lies within previously accepted static central-route clearance union, including L-turn and stair/terrace joins. Endpoint bounds are valid from monotonicity; each full box is partitioned by all union faces and every entire cell covered. This is not merely dense point sampling.','not_yet_proven':['Actual Blender camera/lens/sensor/interpolation matches recipe','Final timeline speed/acceleration and angular smoothness','Actual frame readability/near-plane visual clipping','Human body, feet, gait, accessibility or full castle navigation'],'required_animation_guard':'No unconstrained BEZIER position overshoot. Linear interpolation between verified monotone points stays in tested boxes; alternate splines need explicit control-hull/derivative bounds. Reparameterization must stay monotone in route distance.'}
Path(a.report).write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='intervals'},indent=2));assert r['pass']
