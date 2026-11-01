"""Unaccepted analytical roof-cover candidate. Standard Python only; no Blender IO.
Run: python slate_math.py --report candidate_report.json [--geometry scratch.json]
Source-preserving Blender implementation and actual-light visual acceptance remain pending.
"""
import argparse
import collections
import json
import math
from dataclasses import dataclass

def add(a,b): return tuple(x+y for x,y in zip(a,b))
def mul(a,s): return tuple(x*s for x in a)
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def sub(a,b): return add(a,mul(b,-1))
def area(p): return .5*sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(p,p[1:]+p[:1]))

def clip(poly, signed_distance):
    """Convex polygon clipping against one linear >=0 half-plane."""
    out=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        da,db=signed_distance(a),signed_distance(b)
        if da>=-1e-10: out.append(a)
        if (da>=0)!=(db>=0):
            t=da/(da-db); out.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])))
    clean=[]
    for p in out:
        if not clean or math.dist(p,clean[-1])>1e-8: clean.append(p)
    if len(clean)>1 and math.dist(clean[0],clean[-1])<1e-8: clean.pop()
    return clean

@dataclass(frozen=True)
class Parameters:
    exposure: float=.4
    width: float=.6
    length: float=.6
    joint: float=.004
    inset: float=.06
    lip: float=.025
    head: float=.003
    bottom: float=-.015
    min_area: float=.003
    min_span: float=.035
    def validate(self):
        if not all(math.isfinite(v) for v in vars(self).values()): raise ValueError('Nonfinite parameter')
        if not (0<self.exposure<self.length and 0<self.joint<self.width and self.bottom<0<self.head<self.lip): raise ValueError('Invalid overlap or thickness')
        if min(self.inset,self.min_area,self.min_span)<=0: raise ValueError('Invalid clipping limit')

def pitches():
    s=math.hypot(9.65,18);e=math.hypot(14,18)
    data=[('south',(21,32.6,192.55),(1,0,0),(0,9.65/s,18/s),28,s,[(0,0),(28,0),(14,s)]),
          ('east',(49,32.6,192.55),(0,1,0),(-14/e,0,18/e),27.8,e,[(0,0),(27.8,0),(18.15,e),(9.65,e)]),
          ('north',(49,60.4,192.55),(-1,0,0),(0,-9.65/s,18/s),28,s,[(0,0),(28,0),(14,s)]),
          ('west',(21,60.4,192.55),(0,-1,0),(14/e,0,18/e),27.8,e,[(0,0),(27.8,0),(18.15,e),(9.65,e)])]
    return [dict(name=n,origin=o,u=u,v=v,normal=cross(u,v),width=w,length=l,polygon=p) for n,o,u,v,w,l,p in data]

def inset_polygon(poly,d):
    out=poly[:]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        ex,ey=b[0]-a[0],b[1]-a[1];ln=math.hypot(ex,ey)
        out=clip(out,lambda p,a=a,ex=ex,ey=ey,ln=ln:(ex*(p[1]-a[1])-ey*(p[0]-a[0]))/ln-d)
        if not out: break
    return out

def solid(face,poly,y0,p):
    def point(x,y,z): return add(face['origin'],add(mul(face['u'],x),add(mul(face['v'],y),mul(face['normal'],z))))
    n=len(poly)
    heights=[p.lip+(p.head-p.lip)*(y-y0)/p.length for x,y in poly]
    vertices=[point(x,y,p.bottom) for x,y in poly]+[point(x,y,z) for (x,y),z in zip(poly,heights)]
    faces=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]
    volume=0
    for i in range(1,n-1):
        a,b,c=poly[0],poly[i],poly[i+1]
        ar=((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))/2
        volume+=ar*((heights[0]+heights[i]+heights[i+1])/3-p.bottom)
    return dict(vertices=vertices,faces=faces,volume=volume,top_heights=heights)

def generate(p=Parameters()):
    p.validate();tiles=[];discarded=[];stats=[]
    for face in pitches():
        domain=inset_polygon(face['polygon'],p.inset);start=len(tiles)
        for row in range(math.ceil(face['length']/p.exposure)):
            y0=row*p.exposure;offset=(row%2)*p.width/2
            for col in range(-1,math.ceil(face['width']/p.width)+1):
                x0=col*p.width+offset+p.joint/2;x1=x0+p.width-p.joint
                poly=domain[:]
                for fn in [lambda q:q[0]-x0,lambda q:x1-q[0],lambda q:q[1]-y0,lambda q:y0+p.length-q[1]]:
                    poly=clip(poly,fn)
                    if len(poly)<3:break
                if len(poly)<3:continue
                ar=area(poly);span=min(max(v[k] for v in poly)-min(v[k] for v in poly) for k in [0,1])
                if ar<p.min_area or span<p.min_span:
                    discarded.append(dict(pitch=face['name'],row=row,col=col,area=ar,span=span));continue
                mesh=solid(face,poly,y0,p)
                tiles.append(dict(pitch=face['name'],row=row,col=col,row_start=y0,column_start=x0,polygon=poly,**mesh))
        stats.append(dict(pitch=face['name'],tiles=len(tiles)-start,original_area=area(face['polygon']),inset_area=area(domain),slope_length=face['length'],normal=face['normal']))
    return tiles,discarded,stats

def manifold(tile):
    edges=collections.Counter();directions=collections.Counter()
    for f in tile['faces']:
        for a,b in zip(f,f[1:]+f[:1]):edges[tuple(sorted((a,b)))]+=1;directions[a,b]+=1
    return all(v==2 for v in edges.values()) and all(directions[a,b]==directions[b,a] for a,b in edges)

def report(p,tiles,discarded,stats):
    vs=[v for t in tiles for v in t['vertices']]
    lo=[min(v[k] for v in vs) for k in range(3)];hi=[max(v[k] for v in vs) for k in range(3)]
    return dict(status='UNACCEPTED analytical candidate; no Blender model produced',parameters=vars(p),pitches=stats,tiles=len(tiles),vertices=len(vs),faces=sum(len(t['faces']) for t in tiles),bounds=[lo,hi],summed_solid_volume_not_union=sum(t['volume'] for t in tiles),all_closed_oriented=all(manifold(t) for t in tiles),minimum_solid_volume=min(t['volume'] for t in tiles),discarded_slivers=len(discarded),discarded_footprint_area=sum(t['area'] for t in discarded),row_overlap=p.length-p.exposure,normal_embedding=-p.bottom,macro_plan_and_height_preserved=lo[0]>=21 and hi[0]<=49 and lo[1]>=32.6 and hi[1]<=60.4 and hi[2]<=210.55,limits=['Source shell/bronze contacts are analytic predictions only; current evaluated scene must be checked later.','Discarded edge slivers reveal original slate underneath; verify visual hip coverage rather than pretending every footprint is tiled.','Sum of individual volumes double-counts intentional overlap; not union or load calculation.','No rendered visual gain, historical accuracy, waterproofing or engineering claim.'])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--report',required=True);ap.add_argument('--geometry');a=ap.parse_args();p=Parameters();t,d,s=generate(p)
    with open(a.report,'x') as f:json.dump(report(p,t,d,s),f,indent=2)
    if a.geometry:
        with open(a.geometry,'x') as f:json.dump(dict(tiles=t,discarded=d),f)
if __name__=='__main__':main()
