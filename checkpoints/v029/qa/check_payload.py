import os
"""Independent exact-rational payload domains/caps/volume against actual source and directed saved guard."""
import json,sys,hashlib,itertools,struct,collections,argparse
from pathlib import Path
from fractions import Fraction as F
import numpy as np
ROOT=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(ROOT))
import exact_axis_boundary as e
from planar_triangulation import triangulate
from continuous_box_cover import solid_winding,oriented_closed
sys.path.insert(0,str(Path(__file__).parent));import check_guard as q
UP=28.900001525878906
def f32(x):return struct.unpack('f',struct.pack('f',x))[0]
def quant(x):return UP if x==28.9 else f32(x)
def box(b):return [[quant(x)for x in row]for row in b]
def signed_volume(v,tris):
 v=[e.fraction3(p)for p in v];o=v[0];s=F(0)
 for t in tris:
  a,b,c=[tuple(v[i][k]-o[k]for k in range(3))for i in t];n=e.cross(b,c);s+=sum(a[k]*n[k]for k in range(3))/6
 return s
def half(poly,k,bound,sign):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=sign*(a[k]-bound);db=sign*(b[k]-bound)
  if da>=0:out.append(a)
  if (da<0<db)or(db<0<da):out.append(tuple(a[j]+(b[j]-a[j])*da/(da-db)for j in range(2)))
 return out
def minus_rect(poly,lo,hi):
 current=poly;outside=[]
 for k,b,s in [(0,lo[0],1),(0,hi[0],-1),(1,lo[1],1),(1,hi[1],-1)]:
  p=half(current,k,b,-s)
  if e.area(p)>0:outside.append(p)
  current=half(current,k,b,s)
  if e.area(current)==0:break
 return outside
def source_reference(c,face_ids,G,explicit=None):
 groups=collections.defaultdict(list);ordered=[];offset=0
 for fi,face in enumerate(c['local_faces']):
  ts=c['local_triangles'][offset:offset+len(face)-2];q.require(len(ts)==len(face)-2 and all(set(t)<=set(face) for t in ts),'Ordered source triangle slice');ordered.extend((fi,t)for t in ts);offset+=len(face)-2
 q.require(offset==len(c['local_triangles']),'Ordered source triangle count')
 if explicit is not None:ordered=explicit
 for fi,t in ordered:
  p=[e.fraction3(c['vertices'][i])for i in t];normal=e.cross(tuple(p[1][k]-p[0][k]for k in range(3)),tuple(p[2][k]-p[0][k]for k in range(3)))
  if not any(normal):continue
  fid=c['faces'][fi]['id']
  if fid not in face_ids:continue
  axis=next(k for k in range(3)if all(x[k]==p[0][k]for x in p));other=[k for k in range(3)if k!=axis];pieces=[[tuple(x[k]for k in other)for x in p]]
  for g in G:
   if not F(g[0][axis])<p[0][axis]<F(g[1][axis]):continue
   pieces=[out for piece in pieces for out in minus_rect(piece,tuple(F(g[0][k])for k in other),tuple(F(g[1][k])for k in other))]
  groups[(axis,p[0][axis],1 if normal[axis]>0 else -1)].extend(pieces)
 return groups
def general_validate(v,tris,refs):
 groups=collections.defaultdict(list)
 for ids in tris:
  p=[e.fraction3(v[i])for i in ids];normal=e.cross(tuple(p[1][k]-p[0][k]for k in range(3)),tuple(p[2][k]-p[0][k]for k in range(3)));q.require(any(normal),'Zero derived payload triangle');axes=[k for k in range(3)if all(x[k]==p[0][k]for x in p)];q.require(len(axes)==1,'Nonaxis changed domain');a=axes[0];key=(a,p[0][a],1 if normal[a]>0 else -1);poly=[tuple(x[k]for k in range(3)if k!=a)for x in p];bb=e.bounds(poly);ar=e.area(poly);coverage=sum((e.area(e.clip_convex(poly,r))for r in refs.get(key,[])if e.positive_bbox(bb,e.bounds(r))),F(0));q.require(coverage==ar,'Outside original clipped source union '+str(ar-coverage));groups[key].append(poly)
 for key,polys in groups.items():
  for i,a in enumerate(polys):
   for b in polys[i+1:]:q.require(not e.positive_bbox(e.bounds(a),e.bounds(b))or e.area(e.clip_convex(a,b))==0,'Duplicate changed source boundary')
 for key,polys in refs.items():q.require(sum(map(e.area,groups.get(key,[])),F(0))==sum(map(e.area,polys),F(0)),'Uncovered source domain')
 return {'pass':True,'uncovered_area':0,'outside_area':0,'multiply_covered_area':0,'method':'Exact Fraction coverage of combined same-plane affected source domains, not per-parent diagonal tessellation identity.'}
def run(n,plan,payload):
 q.validate_targets(n,plan);hosts=[next(c for c in n['components']if c['object']==name and c['seed']==0)for name in q.NAMES];G=list(map(box,plan['guard']));C=list(map(box,plan['cavities']));q.margins(G,C);domains=[q.affect(c,G)for c in hosts]
 coords=[set(b[j][k]for b in G+C for j in (0,1))for k in range(3)]
 for d in domains:
  for f in d['affected']:coords[f['axis']].add(f['plane'])
 coords=[sorted(x)for x in coords];cells={};occupied=set();host_occ=[set()for _ in hosts];maxres=0.
 for idx in itertools.product(*(range(len(x)-1)for x in coords)):
  mid=np.array([(coords[k][idx[k]]+coords[k][idx[k]+1])/2 for k in range(3)])
  if not any(q.inside(mid,g)for g in G):continue
  votes=[]
  for j,h in enumerate(hosts):
   w=solid_winding(h['vertices'],h['local_triangles'],mid);res=min(abs(w),abs(abs(w)-1));q.require(res<1e-8,'Quantized uncertain cell');maxres=max(res,maxres);yes=abs(w)>.5;votes.append(yes)
   if yes:host_occ[j].add(idx)
  old=any(votes);new=old and not any(q.inside(mid,c)for c in C);cells[idx]=(old,new)
  if new:occupied.add(idx)
 for i,(old,new)in cells.items():
  for k in range(3):
   for sign in (-1,1):
    j=list(i);j[k]+=sign
    if tuple(j)not in cells:q.require(old==new,'Quantized interface changed')
 meshes=payload['meshes'];q.require(len(meshes)==4,'Mesh count');rows=[]
 q.require([m['name']for m in meshes]==['V029 | foundation outside stores guard','V029 | ashlar outside stores guard','V029 | receiving shell outside stores guard','V029 | local stores shell'],'Ordered owned mesh identities')
 for m in meshes:q.require(m['material_index']==0 and m['use_smooth'] is False,'Material/smooth policy')
 for m,h,t,oc in zip(meshes[:3],hosts,plan['targets'],host_occ):
  q.require(m['name'] in ['V029 | foundation outside stores guard','V029 | ashlar outside stores guard','V029 | receiving shell outside stores guard'],'Name');q.require(oriented_closed(m['faces']),'Unclosed payload');remote=[];changed=[];caps=[]
  for i,l in enumerate(m['face_lineage']):
   if l['kind']=='remote_original':
    fid=l['source_face'];j=next(j for j,f in enumerate(h['faces'])if f['id']==fid);q.require([m['vertices'][v]for v in m['faces'][i]]==[h['vertices'][v]for v in h['local_faces'][j]],'Remote original changed');remote.append(fid)
   elif l['kind']=='clipped_source_domain':changed.append(i)
   elif l['kind']=='buried_guard_cap':caps.append(i)
   else:raise RuntimeError('Unexpected lineage')
  q.require(sorted(remote)==sorted(t['remote_face_ids']),'Remote IDs');refs=source_reference(h,{f['face_id']for f in t['affected_faces']},G)
  # Independent ear clipping of each affected parent verifies native ordered slices,
  # including separate uncovered and multiply-covered areas, before subtraction.
  off=0
  for j,face in enumerate(h['local_faces']):
   native=h['local_triangles'][off:off+len(face)-2];off+=len(face)-2
   if h['faces'][j]['id'] not in {f['face_id']for f in t['affected_faces']}:continue
   ref=source_reference(dict(h,local_faces=[face],local_triangles=native,faces=[h['faces'][j]]),{h['faces'][j]['id']},[])
   independent=triangulate(h['vertices'],face);general_validate(h['vertices'],independent,ref)
   iref=source_reference(dict(h,local_faces=[face],local_triangles=native,faces=[h['faces'][j]]),{h['faces'][j]['id']},[],explicit=[(0,tr)for tr in independent])
   general_validate(h['vertices'],native,iref)
  ts=[tr for i in changed for tr in triangulate(m['vertices'],m['faces'][i])];check=general_validate(m['vertices'],ts,refs)
  caprefs=collections.defaultdict(list)
  for idx in oc:
   for axis in range(3):
    for sign in (-1,1):
     adj=list(idx);adj[axis]+=sign
     if tuple(adj)in cells:continue
     other=[k for k in range(3)if k!=axis];key=(axis,F(coords[axis][idx[axis]+(sign>0)]),-sign);lo=tuple(F(coords[k][idx[k]])for k in other);hi=tuple(F(coords[k][idx[k]+1])for k in other);caprefs[key].append((lo,hi))
  capt=[tr for i in caps for tr in triangulate(m['vertices'],m['faces'][i])];capcheck=e.validate(m['vertices'],capt,(dict(caprefs),None));alltris=[(f[0],f[j],f[j+1])for f in m['faces']for j in range(1,len(f)-1)];oldv=signed_volume(h['vertices'],h['local_triangles']);newv=signed_volume(m['vertices'],alltris);removed=e.facets_from_cells(coords,oc)[1];q.require(newv==oldv-removed,'Exact outside volume');rows.append({'name':m['name'],'remote_exact':len(remote),'changed_domains':check,'caps':capcheck,'source_volume':float(oldv),'outside_volume':float(newv),'exact_volume_residual':str(newv-oldv+removed)})
 local=meshes[-1];q.require(oriented_closed(local['faces']),'Local unclosed');tri=[t for f in local['faces']for t in triangulate(local['vertices'],f)];result=e.validate(local['vertices'],tri,e.facets_from_cells(coords,occupied));q.require(payload['total_triangles']<=8000,'Budget')
 return {'pass':True,'effective_guard':G,'effective_cavities':C,'coordinate_planes':coords,'quantized_cells':len(cells),'max_winding_residual':maxres,'changed_interface_cells':0,'outside':rows,'local':result,'nominal_remote_cycles_exact':sum(x['remote_exact']for x in rows),'directed_guard_bottom':UP,'closed_triangle_budget':payload['total_triangles'],'scope':'Exact saved-coordinate boundary/domain/cap/volume proof for CPU payload; saved native attributes/tessellation/rollback remain mandatory. Directed guard partition only, no added physical volume.'}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--payload',required=True);a.add_argument('--report',required=True);args=a.parse_args();paths={'export':Path(os.environ['V029_QA_DATA'])/'native.json','plan':Path(os.environ['V029_QA_DATA'])/'guard_plan.json','payload':Path(args.payload)};d={k:json.loads(v.read_text())for k,v in paths.items()};r=run(d['export'],d['plan'],d['payload']);r['input_sha256']={k:hashlib.sha256(p.read_bytes()).hexdigest()for k,p in paths.items()};Path(args.report).write_text(json.dumps(r,indent=2)+'\n');print('INDEPENDENT PAYLOAD PASS')
