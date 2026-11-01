"""Small simple-polygon boundary splitter. No scene/file side effects."""
import math
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def sub(a,b):return (a[0]-b[0],a[1]-b[1])
def signed(poly):return sum(cross(a,b)for a,b in zip(poly,poly[1:]+poly[:1]))/2
def area(poly):return abs(signed(poly))
def ccw(poly):return list(poly) if signed(poly)>0 else list(reversed(poly))
def within(p,poly):
 value=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:value=not value
 return value
def boolean(A,B,mode):
 assert mode in ['DIFFERENCE','INTERSECT','UNION'];A=ccw(A);B=ccw(B);segments=[];cert=[]
 for label,poly,other in [('A',A,B),('B',B,A)]:
  for i,(a,b)in enumerate(zip(poly,poly[1:]+poly[:1])):
   d=sub(b,a);cuts=[0.,1.]
   for c,e in zip(other,other[1:]+other[:1]):
    v=sub(e,c);den=cross(d,v)
    if abs(den)<1e-15:continue
    t=cross(sub(c,a),v)/den;u=cross(sub(c,a),d)/den
    if -1e-12<=t<=1+1e-12 and -1e-12<=u<=1+1e-12:cuts.append(max(0,min(1,t)))
   cuts=sorted(set(cuts))
   for t0,t1 in zip(cuts,cuts[1:]):
    if t1-t0<1e-12:continue
    mid=(a[0]+d[0]*(t0+t1)/2,a[1]+d[1]*(t0+t1)/2);inside=within(mid,other)
    keep=(inside if mode=='INTERSECT' else not inside if mode=='UNION' or label=='A' else inside)
    if keep:
     x=(a[0]+d[0]*t0,a[1]+d[1]*t0);y=(a[0]+d[0]*t1,a[1]+d[1]*t1)
     if mode=='DIFFERENCE' and label=='B':x,y=y,x
     segments.append((x,y));cert.append({'source':label,'edge':i,'parameter_interval':[t0,t1],'inside_other':inside,'ends':[x,y]})
 assert segments,'Empty result unsupported'
 loops=[]
 while segments:
  first=segments.pop(0);ordered=[first];poly=[first[0]]
  while math.dist(ordered[-1][1],poly[0])>=1e-8:
   last=ordered[-1][1];matches=[i for i,(x,y)in enumerate(segments)if math.dist(x,last)<1e-8];assert matches,('Unclosed boundary',last)
   incoming=sub(ordered[-1][1],ordered[-1][0])
   # At a point-touch junction, separate CCW cycles rather than making a
   # non-manifold figure-eight polygon. Choose largest signed left turn.
   def turn(i):
    outgoing=sub(segments[i][1],segments[i][0]);return math.atan2(cross(incoming,outgoing),incoming[0]*outgoing[0]+incoming[1]*outgoing[1])
   n=segments.pop(max(matches,key=turn));ordered.append(n);poly.append(n[0])
  assert len(poly)>=3 and area(poly)>1e-12
  loops.append(poly)
 return loops,cert
