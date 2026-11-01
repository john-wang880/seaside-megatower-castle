import json,math,collections,hashlib,argparse,sys
from pathlib import Path
from overlay_math import *
P=Path(__file__).resolve().parent
if sys.flags.optimize:raise RuntimeError('Assertions required')
ap=argparse.ArgumentParser();ap.add_argument('--geometry',required=True);ap.add_argument('--report',required=True);a=ap.parse_args();geometry_path=Path(a.geometry).resolve();report_path=Path(a.report).resolve()
if geometry_path==report_path or report_path.exists()or not report_path.parent.is_dir():raise RuntimeError('New distinct report required')
x=json.loads(geometry_path.read_text());source=x['source_path'];V=x['patch']['vertices'];F=x['patch']['faces'];terrain=[r['coords']for r in x['terrain']if signed([v[:2]for v in r['coords']])>0];original=[f for f in source['faces']if 1140<=f['id']<1260];SV=source['vertices'];S=[(f,[SV[i]for i in f['vertices']])for f in original];ulp=lambda q:2.**(math.frexp(abs(q))[1]-24)if q else 2.**-149;epsxy=math.hypot(max(ulp(v[0])for v in V),max(ulp(v[1])for v in V));epsz=max(ulp(v[2])for v in V);perim=lambda p:sum(math.dist(a,b)for a,b in zip(p,p[1:]+p[:1]));rows=[];gaplo=float('inf');gaphi=-float('inf');areaSum=0.;wrong=outside=0.;displacements=[];gradients=[];overlaps=[];sourceAreas=collections.defaultdict(float);piecesBySource=collections.defaultdict(list);edges=collections.Counter();triangles=[]
omitted=[r for r in x['terrain']if signed([v[:2]for v in r['coords']])<=0];assert len(omitted)==42 and all(v[2]==-6.5 for r in omitted for v in r['coords']), 'Unexpected omitted terrain geometry'
terrain_gradients=[]
for tt in terrain:
 tz=plane(tt);q=tt[0];terrain_gradients.append(math.hypot(tz((q[0]+1,q[1]))-tz(q),tz((q[0],q[1]+1))-tz(q)))
for f in F:
 ids=f['vertices'];t=[V[i]for i in ids];xy=[tuple(v[:2])for v in t];ar=area(xy);assert ar>1e-12 and signed(xy)<0;areaSum+=ar;triangles.append(t)
 for a,b in zip(ids,ids[1:]+ids[:1]):edges[tuple(sorted((a,b)))]+=1
 pieces=triangle_overlay(t,terrain);coverage=sum(p['area']for p in pieces);assert abs(coverage-ar)<max(1e-9,ar*1e-8),(f['id'],'terraincoverage',coverage,ar)
 
 for i,aa in enumerate(pieces):
  for bb in pieces[i+1:]:assert area(clip(aa['polygon'],bb['polygon']))<1e-9,'Upper terrain overlay double coverage'
 g0=min(p['minimum']for p in pieces);g1=max(p['maximum']for p in pieces);assert .016<=g0<=g1<=.030,(f['id'],'gap',g0,g1);gaplo=min(gaplo,g0);gaphi=max(gaphi,g1);pz=plane(t);bounds0=bounds(t);covered=wrong0=0.
 for sf,st in S:
  sb=bounds(st)
  if bounds0[0]>sb[2]or sb[0]>bounds0[2]or bounds0[1]>sb[3]or sb[1]>bounds0[3]:continue
  poly=clip(xy,[tuple(v[:2])for v in st]);a=area(poly)
  if a<=1e-13:continue
  covered+=a;sourceAreas[sf['id']]+=a;piecesBySource[sf['id']].append(poly);sz=plane(st);displacements.extend(pz(q)-sz(q)for q in poly)
  if sf['material_index']!=f['material_index']:wrong0+=a
 bound=epsxy*perim(xy)+math.pi*epsxy**2+1e-10;assert abs(covered-ar)<=bound,(f['id'],'outside',covered,ar,bound);assert wrong0<=bound,(f['id'],'material',wrong0,bound);wrong+=wrong0;outside+=max(0,ar-covered)
 origin=xy[0];grad=[pz((origin[0]+1,origin[1]))-pz(origin),pz((origin[0],origin[1]+1))-pz(origin)];gradients.append(math.hypot(*grad));rows.append({'face':f['id'],'area':ar,'gap_min':g0,'gap_max':g1,'terrain_pieces':len(pieces),'wrong_material_overlap_area':wrong0,'outside_source_area':max(0,ar-covered)})
assert all(n<=2 for n in edges.values()),'Nonmanifold patch edge'
# Per-original-face partition, plus actual new triangle pair overlap.
areaErrors=[]
for sf,st in S:
 xy=[tuple(v[:2])for v in st];error=abs(sourceAreas[sf['id']]-area(xy));bound=epsxy*perim(xy)+math.pi*epsxy**2+1e-10;assert error<=bound,(sf['id'],'hole/area',error,bound);areaErrors.append(error)
for i,t in enumerate(triangles):
 a=bounds(t)
 for j in range(i+1,len(triangles)):
  u=triangles[j];b=bounds(u)
  if min(a[2],b[2])<=max(a[0],b[0])or min(a[3],b[3])<=max(a[1],b[1]):continue
  aa=area(clip([tuple(v[:2])for v in t],[tuple(v[:2])for v in u]))
  if aa>1e-10:overlaps.append({'faces':[i,j],'area':aa})
assert not overlaps,overlaps[:10]
# Every unmatched mesh edge must lie on original outer patch boundary within local coordinate ULP.
sedge=collections.Counter()
for f in original:
 ids=f['vertices']
 for a,b in zip(ids,ids[1:]+ids[:1]):sedge[tuple(sorted((a,b)))]+=1
boundary=[(a,b)for (a,b),n in sedge.items()if n==1]
def pointseg(p,a,b):
 d=sub(b,a);l=d[0]**2+d[1]**2;t=((p[0]-a[0])*d[0]+(p[1]-a[1])*d[1])/l;t=max(0,min(1,t));q=(a[0]+t*d[0],a[1]+t*d[1]);return math.dist(p,q),t
boundaryRows=[];seamZ=0.;maxbd=0.
for (ia,ib),n in edges.items():
 if n!=1:continue
 a,b=V[ia],V[ib];mid=((a[0]+b[0])/2,(a[1]+b[1])/2);ds=[pointseg(mid,SV[u],SV[v])[0]for u,v in boundary];k=min(range(len(ds)),key=ds.__getitem__);u,v=boundary[k];assert ds[k]<=epsxy+1e-10,('internal hole/unmatched edge',ia,ib,ds[k],epsxy)
 for point in [a,b]:
  d,t=pointseg(point[:2],SV[u],SV[v]);maxbd=max(maxbd,d);assert d<=epsxy+1e-10,('boundary point',d,epsxy)
  if u//7==v//7 and u//7 in [95,105]:
   oldz=SV[u][2]+t*(SV[v][2]-SV[u][2]);err=abs(point[2]-oldz);seamZ=max(seamZ,err);slope=abs(SV[v][2]-SV[u][2])/math.dist(SV[u][:2],SV[v][:2]);assert err<=epsz+slope*epsxy+1e-10,('seam Z',err)
 boundaryRows.append({'edge':[ia,ib],'source_edge':[u,v],'midpoint_xy_error':ds[k]})
report={'pass':True,'input_sha256':x['input_sha256'],'terrain_scope':'Upward projected faces of actual closed headland upper surface; downward underside cap separately excluded, not counted as a second terrain layer. Coverage and overlaps checked.', 'actual_geometry_sha256':hashlib.sha256(geometry_path.read_bytes()).hexdigest(),'actual_patch_faces':len(F),'actual_patch_vertices':len(V),'full_face_gap_range':[gaplo,gaphi],'area':areaSum,'source_area':sum(area([tuple(v[:2])for v in t])for _,t in S),'maximum_sourceface_partition_area_error':max(areaErrors),'total_wrong_material_rounding_overlap_area':wrong,'total_outside_source_rounding_area':outside,'new_new_positive_area_overlaps':overlaps,'boundary_edges':boundaryRows,'maximum_boundary_xy_error':maxbd,'maximum_end_seam_z_error':seamZ,'rounding_bounds':{'one_ulp_xy_euclidean':epsxy,'one_ulp_z':epsz,'area_bound':'local perimeter*XY_ULP_norm+pi*XY_ULP_norm²+1e-10','seam_z_bound':'Z_ULP+source_edge_grade*XY_ULP_norm+1e-10'},'full_surface_z_displacement_range':[min(displacements),max(displacements)],'surface_grade_max':max(gradients),'terrain_grade_max_in_export':max(terrain_gradients),'excluded_terrain_underside':{'triangles':len(omitted),'constant_z':-6.5,'not_ground_support':True},'faces':rows,'scope':'Actual candidate evaluated triangles against actual terrain; complete affine overlay, not vertex sampling. Original XY/material domains within explicit float32-coordinate bounds; no positive-area triangle overlaps or unmatched interior mesh edges. Open downward-oriented surface, not manifold solid. No camera pixel coverage claim.'};report_path.write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items()if k not in ['faces','boundary_edges']},indent=2))
