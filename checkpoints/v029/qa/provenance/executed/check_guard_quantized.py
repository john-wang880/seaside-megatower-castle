"""Independent read-only local partition/route/floor proof. Produces no mesh."""
import argparse,json,hashlib,itertools,struct,collections,sys
from pathlib import Path
from fractions import Fraction as F
import numpy as np
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'checkpoints/v028/qa'))
from continuous_box_cover import solid_winding,oriented_closed,box_inside
from body_support import analyze
NAMES=['V028 | foundation outside chamber guard','V028 | ashlar outside chamber guard','V028 | local receiving chamber shell']
SHA='f0d135e0c6e554b5ae7c520ef9ccefc61e2a7c4abc3129eef1d3d4118bca8096'
def require(v,msg):
 if not v:raise RuntimeError(msg)
def inside(p,b):return all(b[0][k]<p[k]<b[1][k] for k in range(3))
def clip(poly,b):
 p=[[F(x)for x in v]for v in poly]
 for k in range(3):
  for bound,sign in ((F(b[0][k]),1),(F(b[1][k]),-1)):
   out=[]
   if not p:return []
   for a,z in zip(p,p[1:]+p[:1]):
    da=sign*(a[k]-bound);dz=sign*(z[k]-bound)
    if da>=0:out.append(a)
    if (da<0<dz)or(dz<0<da):
     t=da/(da-dz);out.append([a[j]+t*(z[j]-a[j])for j in range(3)])
   p=out
 return p
def area2(poly):
 if len(poly)<3:return [F(0)]*3
 a=poly[0];s=[F(0)]*3
 for b,c in zip(poly[1:],poly[2:]):
  u=[b[i]-a[i]for i in range(3)];v=[c[i]-a[i]for i in range(3)]
  for k in range(3):s[k]+=u[(k+1)%3]*v[(k+2)%3]-u[(k+2)%3]*v[(k+1)%3]
 return s
def affect(c,G):
 faces=[set(f)for f in c['local_faces']];affected=set();zero=0
 for t in c['local_triangles']:
  p=[c['vertices'][i]for i in t]
  if not any(area2([[F(x)for x in v]for v in p])):zero+=1;continue
  if not any(any(area2(clip(p,g)))for g in G):continue
  parents=[i for i,s in enumerate(faces)if set(t)<=s];require(len(parents)==1,'Ambiguous nonzero parent');affected.add(parents[0])
 rows=[]
 for i in sorted(affected):
  p=[c['vertices'][j]for j in c['local_faces'][i]];axes=[k for k in range(3)if len({v[k]for v in p})==1];require(len(axes)==1,'Actual intersecting non-axis parent');k=axes[0];rows.append({'local_face':i,'source_face':c['faces'][i]['id'],'axis':k,'plane':p[0][k]})
 return {'object':c['object'],'affected':rows,'remote_face_ids':[c['faces'][i]['id']for i in range(len(faces))if i not in affected],'zero_measure_derived_triangles':zero}
def margins(G,C):
 result=[]
 for c in C:
  q=[min(*[c[0][k]-g[0][k]for k in range(3)],*[g[1][k]-c[1][k]for k in range(3)])for g in G];require(max(q)>0,'Cavity not strictly inside guard');result.append(max(q))
 return result
def non_target_free(c,b):
 v=np.asarray(c['vertices']);lo,hi=map(np.array,b);t=np.array(c['local_triangles'],int);a=v[t];idx=np.flatnonzero(np.all(a.max(1)>=lo,axis=1)&np.all(a.min(1)<=hi,axis=1));hits=[]
 for i in idx:
  p=clip(a[i].tolist(),b)
  if any(area2(p)):
   mid=[sum(v[k]for v in p)/len(p)for k in range(3)]
   if inside(mid,b):hits.append(int(i))
 if hits:return False
 if oriented_closed(c['local_faces']):
  w=solid_winding(v,t,(lo+hi)/2)
  if abs(w)>.5:return False
 return True

def require_planes(coords,required):
 require(all(p in coords[k] for k,p in required),'Missing actual source plane')
def require_floor(rows):require(rows and all(r['after'] for r in rows),'Floor coverage gap')
def require_air(rows):require(rows and all(not r['after'] for r in rows),'Intended air blocked')
def require_unique(rows):require(len(rows)==len(set(rows)),'Duplicate expected oriented boundary')
def validate_targets(n,plan,domains=None):
 require(sorted((t['object'],t['seed'])for t in plan['targets'])==sorted((x,0)for x in NAMES),'Wrong target identities')
 for t in plan['targets']:
  c=next(c for c in n['components']if c['object']==t['object'] and c['seed']==0)
  require(t['raw_vertex_ids']==list(range(len(c['vertices']))),'Wrong raw target vertices')
  if domains is not None:
   d=next(d for d in domains if d['object']==t['object']);require(t['remote_face_ids']==d['remote_face_ids'],'Remote-domain mapping drift');require(sorted(x['face_id']for x in t['affected_faces'])==sorted(x['source_face']for x in d['affected']),'Affected-domain mapping drift')
def run(n,G,C):
 hosts=[next(c for c in n['components']if c['object']==name and c['seed']==0)for name in NAMES];other=[c for c in n['components']if c['object']not in NAMES];buffers=margins(G,C);domains=[affect(c,G)for c in hosts]
 # Refine independently with floor, air-slice and intended body planes as well.
 floors=[[[14.8,35.5,28.95],[16.4,36.9,29]],[[16.4,34,28.95],[23.4,38.5,29]]]
 air=[[[14.8,35.5,29],[16.4,36.9,29.025]],[[16.4,34,29],[23.4,38.5,29.025]]]
 body=[[14.8,35.6,29.025],[23.3,36.8,31.1]]
 # Derived saved-coordinate floor and air extents; body remains the same conservative real-valued lane.
 import struct
 f32=lambda x:struct.unpack('f',struct.pack('f',x))[0]
 floors=[[[f32(x)for x in row]for row in b]for b in floors];air=[[[f32(x)for x in row]for row in b]for b in air]
 coords=[set(b[e][k]for b in G+C+floors+air+[body]for e in (0,1))for k in range(3)]
 required=[]
 for d in domains:
  for f in d['affected']:coords[f['axis']].add(f['plane']);required.append((f['axis'],f['plane']))
 coords=[sorted(x)for x in coords];require_planes(coords,required);states={};volumes=[0.,0.];maxres=0.
 for ijk in itertools.product(*(range(len(x)-1)for x in coords)):
  lo=np.array([coords[k][ijk[k]]for k in range(3)]);hi=np.array([coords[k][ijk[k]+1]for k in range(3)]);mid=(lo+hi)/2
  if not any(inside(mid,g)for g in G):continue
  votes=[]
  for h in hosts:
   w=solid_winding(h['vertices'],h['local_triangles'],mid);r=min(abs(w),abs(abs(w)-1));maxres=max(maxres,r);require(r<1e-8,'Uncertain winding');votes.append(abs(w)>.5)
  src=any(votes);after=src and not any(inside(mid,c)for c in C);states[ijk]={'source':src,'after':after,'mid':mid.tolist(),'lo':lo.tolist(),'hi':hi.tolist()};dv=float(np.prod(hi-lo));volumes[0]+=dv*src;volumes[1]+=dv*after
 interfaces=[];boundaries=[]
 for i,row in states.items():
  for k in range(3):
   for sign in (-1,1):
    j=list(i);j[k]+=sign;j=tuple(j)
    if j not in states:
     require(row['source']==row['after'],'Changed guard interface');interfaces.append({'axis':k,'sign':sign,'plane':row['lo'][k]if sign<0 else row['hi'][k],'occupied':row['source'],'cell_lo':row['lo'],'cell_hi':row['hi']})
    elif row['after'] and not states[j]['after']:boundaries.append((i,k,sign))
 floorcells=[r for r in states.values()if any(inside(r['mid'],b)for b in floors)];aircells=[r for r in states.values()if any(inside(r['mid'],b)for b in air)];bodycells=[r for r in states.values()if inside(r['mid'],body)]
 require_floor(floorcells);require_air(aircells);require_air(bodycells);require_unique(boundaries)
 for b in C+air+[body]:
  for c in other:require(non_target_free(c,b),'Non-target intersects interior '+c['object'])
 oldbox=[[7.1,35.6,29.025],[14.8,36.8,31.1]];old=[analyze(c,oldbox)for c in n['components']];require(all(x['disjoint']for x in old),'Existing receiving cross-lane blocked')
 # Actual finite seats beside/above new opening, on both sides of old X15.1 interface.
 seats=[]
 for label,y in [('south',[35.42,35.48]),('north',[36.92,36.98])]:
  for host,x in [(hosts[2],[15.02,15.08]),(hosts[0],[15.12,15.18])]:
   b=[[x[0],y[0],29.1],[x[1],y[1],31.3]];q=box_inside(host,*b);require(q['pass'],'Jamb source seat');require(not any(all(b[0][k]<c[1][k]and c[0][k]<b[1][k]for k in range(3))for c in C),'Seat cut away');seats.append({'role':label,**q})
 for host,x in [(hosts[2],[15.02,15.08]),(hosts[1],[15.12,15.18])]:
  b=[[x[0],35.6,31.47],[x[1],36.8,31.53]];q=box_inside(host,*b);require(q['pass'],'Lintel source seat');seats.append({'role':'lintel',**q})
 west_floor=box_inside(hosts[2],[14.7,35.4,28.91],[14.9,37,28.99]);require(west_floor['pass'],'Old floor across west guard gap')
 return {'pass':True,'old_floor_cross_guard_positive_box':west_floor,'guard':G,'cavities':C,'minimum_cavity_guard_buffer':min(buffers),'domains':domains,'coordinate_planes':coords,'refined_cell_count':len(states),'source_union_volume_in_guard':volumes[0],'after_union_volume_in_guard':volumes[1],'removed_volume':volumes[0]-volumes[1],'added_volume':0,'max_winding_residual':maxres,'interfaces':interfaces,'changed_interface_cells':0,'old_air_interface_rectangles':sum(not x['occupied']for x in interfaces),'expected_unique_oriented_boundary_rectangles':len(boundaries),'floor_positive_cells':len(floorcells),'floor_air_cells':len(aircells),'clear_new_body_cells':len(bodycells),'old_connection_box':oldbox,'new_body_box':body,'retained_seats':seats,'non_target_components_checked':len(other),'_states':states,'_required_planes':required,'_floor_boxes':floors,'_floor_cells':floorcells,'_body_cells':bodycells,'_boundaries':boundaries}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--export',required=True);p.add_argument('--plan',required=True);p.add_argument('--output',required=True);a=p.parse_args();n=json.loads(Path(a.export).read_text());plan=json.loads(Path(a.plan).read_text());require(n['source_sha256']==SHA,'Source');validate_targets(n,plan);G=plan['guard'];C=plan['cavities'];r=run(n,G,C);validate_targets(n,plan,r['domains']);r={k:v for k,v in r.items()if not k.startswith('_')};r.update(source_sha256=SHA,input_sha256={x:hashlib.sha256(Path(x).read_bytes()).hexdigest()for x in (a.export,a.plan,__file__)},scope='Independent pre-cut expected occupancy; no model generated. Uniform cells proven by all intersecting actual source planes. Floor/body tests continuous, not samples. No engineering/load/global-access claim. Saved-coordinate geometry/material/domain checks remain mandatory.');Path(a.output).write_text(json.dumps(r,indent=2)+'\n');print('INDEPENDENT GUARD PASS',r['refined_cell_count'])
