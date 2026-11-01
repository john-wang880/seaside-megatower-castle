"""Pure camera-only analytic path/time/gaze; no Blender dependency or writes."""
import math
R=.45
STRAIGHT=7.
ARC=math.pi*R/2
LENGTH=STRAIGHT+ARC+20.75
FPS=12
COUNT=336
MOTION_SECONDS=(COUNT-1)/FPS
M=.18125/.6

def S(u):
 u=max(0.,min(1.,u));return u*u*u*(10+u*(-15+6*u))
def Sd(u):return 30*u*u*(u-1)**2 if 0<u<1 else 0.
def Sdd(u):return 60*u*(2*u*u-3*u+1) if 0<u<1 else 0.
def G(u):return u**6-3*u**5+2.5*u**4

def make_segments(v):
 # Quintic velocity transitions: speed/acceleration/jerk match at time joins.
 entries=[('start',1.5,0,v),('hall',(5.5-.75*v)/v,v,v),('slow_for_turn',1.5,v,.35)]
 slow_start=5.5+.75*(v+.35)
 entries += [('rounded_turn',(7.95-slow_start)/.35,.35,.35),('resume',1.5,.35,v)]
 resume_end=7.95+.75*(v+.35)
 entries += [('north_route',(24.8-resume_end)/v,v,v),('slow_for_arrival',1.5,v,.6)]
 final_slow_start=24.8+.75*(v+.6)
 entries += [('arrival',(LENGTH-.6-final_slow_start)/.6,.6,.6),('stop',2.,.6,0)]
 result=[];t=0.;s=0.
 for name,duration,v0,v1 in entries:
  assert duration>0
  result.append({'name':name,'t0':t,'t1':t+duration,'s0':s,'s1':s+duration*(v0+v1)/2,'v0':v0,'v1':v1})
  t+=duration;s+=duration*(v0+v1)/2
 return result
lo,hi=1.2,1.6
for _ in range(80):
 v=(lo+hi)/2
 if make_segments(v)[-1]['t1']>MOTION_SECONDS:lo=v
 else:hi=v
CRUISE=(lo+hi)/2
SEGMENTS=make_segments(CRUISE)

def distance_at(t):
 if t<=0:return 0.,0.,0.
 if t>=MOTION_SECONDS:return LENGTH,0.,0.
 seg=next(q for q in SEGMENTS if t<=q['t1']);D=seg['t1']-seg['t0'];u=(t-seg['t0'])/D;dv=seg['v1']-seg['v0']
 return seg['s0']+D*(seg['v0']*u+dv*G(u)),seg['v0']+dv*S(u),dv*Sd(u)/D

def vertical(y):
 # Stabilized eye ascent: constant incline, smooth C2+ slope on/off transitions.
 if y<=44.9:return 29.,0.,0.
 if y<45.5:
  u=(y-44.9)/.6;return 29+.6*M*G(u),M*S(u),M*Sd(u)/.6
 if y<=56.9:return 29+.090625+M*(y-45.5),M,0.
 if y<57.5:
  u=(y-56.9)/.6;return 32.534375+.6*M*(u-G(u)),M*(1-S(u)),-M*Sd(u)/.6
 return 32.625,0.,0.

def xy(s):
 if s<STRAIGHT:return -3+s,38.,1.,0.,0.,0.
 if s<STRAIGHT+ARC:
  a=-math.pi/2+(s-STRAIGHT)/R
  return 4+R*math.cos(a),38.45+R*math.sin(a),-math.sin(a),math.cos(a),-math.cos(a)/R,-math.sin(a)/R
 return 4.45,38.45+s-STRAIGHT-ARC,0.,1.,0.,0.
# Reach85 degrees at midpoint of original rounded turn,90 at its end.
u0,u1=0.,1.
for _ in range(80):
 u=(u0+u1)/2
 if S(u)<85/90:u0=u
 else:u1=u
TURN_GAZE_END=STRAIGHT+ARC
TURN_GAZE_START=(STRAIGHT+ARC/2-((u0+u1)/2)*TURN_GAZE_END)/(1-(u0+u1)/2)
END_GAZE_START=24.2

def time_at_distance(s):
 lo,hi=0.,MOTION_SECONDS
 for _ in range(80):
  mid=(lo+hi)/2
  if distance_at(mid)[0]<s:lo=mid
  else:hi=mid
 return (lo+hi)/2
TURN_MID_TIME=time_at_distance(STRAIGHT+ARC/2)
TURN_GAZE_TIME_START=SEGMENTS[2]['t0']
TURN_GAZE_TIME_END=TURN_GAZE_TIME_START+(TURN_MID_TIME-TURN_GAZE_TIME_START)/((u0+u1)/2)
END_GAZE_TIME_START=time_at_distance(END_GAZE_START)
END_GAZE_TIME_END=MOTION_SECONDS-.5

def previous_gaze_unused(t):
 w=TURN_GAZE_TIME_END-TURN_GAZE_TIME_START;u=(t-TURN_GAZE_TIME_START)/w
 W=END_GAZE_TIME_END-END_GAZE_TIME_START;e=(t-END_GAZE_TIME_START)/W
 return (90*S(u)+75*S(e),-5+8*S(e),90*Sd(u)/w+75*Sd(e)/W,8*Sd(e)/W,90*Sdd(u)/w**2+75*Sdd(e)/W**2,8*Sdd(e)/W**2)

def pose(t):
 s,v,a=distance_at(t);x,y,xs,ys,xss,yss=xy(s);z,zy,zyy=vertical(y);yaw,pitch,yaws,pitchs,yawss,pitchss=gaze(t)
 zs=zy*ys;zss=zyy*ys*ys+zy*yss
 vel=[xs*v,ys*v,zs*v];acc=[xss*v*v+xs*a,yss*v*v+ys*a,zss*v*v+zs*a]
 ya,pi=math.radians(yaw),math.radians(pitch);loc=[x,y,z+1.65];direction=[math.cos(ya)*math.cos(pi),math.sin(ya)*math.cos(pi),math.sin(pi)]
 return {'time_seconds':t,'distance_xy':s,'location':loc,'target':[loc[i]+4*direction[i] for i in range(3)],'yaw_degrees':yaw,'pitch_degrees':pitch,'horizontal_speed_mps':v,'speed_3d_mps':math.sqrt(sum(q*q for q in vel)),'acceleration_3d_mps2':math.sqrt(sum(q*q for q in acc)),'yaw_rate_degrees_per_second':yaws,'yaw_acceleration_degrees_per_second2':yawss,'pitch_rate_degrees_per_second':pitchs,'pitch_acceleration_degrees_per_second2':pitchss,'lens':26,'clip_start':.05,'clip_end':3000}

# V2: gaze toward the independently ray-checked near corridor opening.
# Quintic Hermite interpolation makes yaw, yawrate and yawacceleration continuous
# even where the unchanged XY path is only C1 at its straight/circle joins.
OPENING_TARGET=(4.45,39.5)
def raw_opening_yaw(t):
 s,_,_=distance_at(max(0.,min(MOTION_SECONDS,t)));x,y,*_=xy(s)
 if x>=4.45-1e-11:return 90.
 return math.degrees(math.atan2(OPENING_TARGET[1]-y,OPENING_TARGET[0]-x))
YAW_KNOT_TIMES=sorted(set([i*.25 for i in range(41)]+[time_at_distance(STRAIGHT),time_at_distance(STRAIGHT+ARC)]))
YAW_NODES=[]
for t in YAW_KNOT_TIMES:
 y=raw_opening_yaw(t);h=.02
 v=(raw_opening_yaw(t+h)-raw_opening_yaw(t-h))/(2*h)
 a=(raw_opening_yaw(t+h)-2*y+raw_opening_yaw(t-h))/(h*h)
 if t==0 or t>=9.:v=a=0.
 YAW_NODES.append((t,y,v,a))
YAW_SPLINES=[]
for left,right in zip(YAW_NODES,YAW_NODES[1:]):
 t0,y0,v0,acc0=left;t1,y1,v1,acc1=right;D=t1-t0
 c0=y0;c1=v0*D;c2=.5*acc0*D*D
 A=y1-c0-c1-c2;B=v1*D-c1-2*c2;C=acc1*D*D-2*c2
 YAW_SPLINES.append({'t0':t0,'t1':t1,'coefficients':[c0,c1,c2,10*A-4*B+.5*C,-15*A+7*B-C,6*A-3*B+.5*C]})
def opening_yaw(t):
 if t<=0:return raw_opening_yaw(0),0.,0.
 if t>=10:return 90.,0.,0.
 q=next(q for q in YAW_SPLINES if t<=q['t1']);D=q['t1']-q['t0'];u=(t-q['t0'])/D;c=q['coefficients']
 return (sum(c[i]*u**i for i in range(6)),sum(i*c[i]*u**(i-1) for i in range(1,6))/D,sum(i*(i-1)*c[i]*u**(i-2) for i in range(2,6))/(D*D))
def gaze(t):
 yaw,rate,acc=opening_yaw(t)
 W=END_GAZE_TIME_END-END_GAZE_TIME_START;e=(t-END_GAZE_TIME_START)/W
 return yaw+75*S(e),-5+8*S(e),rate+75*Sd(e)/W,8*Sd(e)/W,acc+75*Sdd(e)/W**2,8*Sdd(e)/W**2
