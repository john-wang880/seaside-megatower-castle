"""Actual authored conifer geometry/contact audit, candidate read-only. No save/render."""
import bpy,sys,argparse,json,hashlib,collections,math
import numpy as np
from pathlib import Path
if sys.flags.optimize: raise RuntimeError('Run with assertions enabled; optimized Python is unsupported')
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser()
for key in ['candidate','mapping','route-report','report']:p.add_argument('--'+key,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(a.candidate);mapping=json.load(open(a.mapping));bpy.ops.wm.open_mainfile(filepath=str(Path(a.candidate).resolve()),use_scripts=False)
fol=bpy.data.objects['V019 candidate | articulated conifer foliage'];wood=bpy.data.objects['V019 candidate | connected conifer boughs'];trunk=bpy.data.objects['V010 | woodland trunks with gate exit clearance'];issues=[]
for o in [fol,wood]:
 assert not o.modifiers and all(abs(o.matrix_world[i][j]-(i==j))<1e-9 for i in range(4) for j in range(4));assert all(math.isfinite(x) for v in o.data.vertices for x in v.co)
assert [m.name for m in fol.data.materials]==['Fir needles — forest green','Sunlit needle tips','Cypress needles — deep blue green'];assert [m.name for m in wood.data.materials]==['Pine bark']
wood.data.calc_loop_triangles();tt=collections.defaultdict(list)
for t in wood.data.loop_triangles:tt[t.polygon_index].append(tuple(t.vertices))
DIRS=[Vector(v).normalized() for v in [(1,.371,.613),(.217,1,.489),(.529,.193,1)]]
def solid(vs,faces,triangles,label):
 counts=collections.defaultdict(list)
 for f in faces:
  for x,y in zip(f,f[1:]+f[:1]):counts[tuple(sorted((x,y)))].append((x,y))
 assert all(len(v)==2 and v[0]==v[1][::-1] for v in counts.values()),('Open/inconsistent wood',label)
 center=sum(vs,Vector())/len(vs);vol=sum((vs[t[0]]-center).dot((vs[t[1]]-center).cross(vs[t[2]]-center))/6 for t in triangles);assert vol>1e-12,('Nonpositive wood volume',label,vol)
 return {'bvh':BVHTree.FromPolygons([v-center for v in vs],triangles,all_triangles=True),'bvh_origin':center,'volume':vol,'verts':vs,'triangles':triangles,'label':label}
def bvh_containment(pt,s):
 pt=pt-s['bvh_origin']
 hit,normal,index,dist=s['bvh'].find_nearest(pt)
 if hit is None:return {'state':'uncertain','reason':'no surface'}
 if dist<=2e-6:return {'state':'uncertain','reason':'near surface','margin':dist}
 votes=[]
 for d in DIRS:
  q=pt.copy();seen=set();n=0
  for _ in range(128):
   h,no,idx,length=s['bvh'].ray_cast(q,d,100)
   if h is None:break
   if idx not in seen:n+=1;seen.add(idx)
   q=h+d*1e-5
  else:return {'state':'uncertain','reason':'ray limit'}
  votes.append(n%2)
 return {'state':('inside' if votes[0] else 'outside') if len(set(votes))==1 else 'uncertain','margin':dist,'parities':votes}
def exact_triangle_parity(pt,s):
 if 'double_triangles' not in s:
  verts=np.asarray([list(v) for v in s['verts']],dtype=np.float64);origin=verts.mean(axis=0);s['double_origin']=origin;s['double_triangles']=(verts-origin)[np.asarray(s['triangles'])]
 tri=s['double_triangles'];q=np.asarray(list(pt),dtype=np.float64)-s['double_origin'];e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];votes=[];counts=[]
 for d in [(1.,.371,.613),(.217,1.,.489),(.529,.193,1.)]:
  d=np.asarray(d);d/=np.linalg.norm(d);h=np.cross(d,e2);det=np.sum(e1*h,axis=1);good=abs(det)>1e-18;inv=np.zeros_like(det);inv[good]=1/det[good];v=q-tri[:,0];u=np.sum(v*h,axis=1)*inv;cross=np.cross(v,e1);w=(cross@d)*inv;dist=np.sum(e2*cross,axis=1)*inv;hits=sorted(dist[good&(u>=-1e-12)&(w>=-1e-12)&(u+w<=1+1e-12)&(dist>1e-10)]);unique=[]
  for t in hits:
   if not unique or abs(t-unique[-1])>1e-10:unique.append(float(t))
  counts.append(len(unique));votes.append(len(unique)%2)
 return {'state':('inside' if votes[0] else 'outside') if len(set(votes))==1 else 'uncertain','parities':votes,'crossing_counts':counts,'method':'float64 all-authoritative-triangles, no BVH ray restart or advance; shared-edge coincident distances deduplicated at1e-10m'}
def containment(pt,s):
 first=bvh_containment(pt,s)
 if first['state']=='inside':return first
 second=exact_triangle_parity(pt,s);second['initial_bvh']=first
 if 'margin' in first:second['margin']=first['margin']
 return second
comps=[];coveredv=set();coveredf=set();primary=None;leader=None
for row in mapping['wood_components']:
 start=row['vertex_start'];end=start+row['vertex_count'];fs=list(range(row['face_start'],row['face_start']+row['face_count']));ids=list(range(start,end));im={i:i-start for i in ids};vs=[wood.matrix_world@wood.data.vertices[i].co for i in ids];faces=[[im[i] for i in wood.data.polygons[f].vertices] for f in fs];triangles=[[im[i] for i in t] for f in fs for t in tt[f]];assert not coveredv.intersection(ids) and not coveredf.intersection(fs);coveredv.update(ids);coveredf.update(fs)
 s=solid(vs,faces,triangles,str(start));s['meta']=row;s['root']=sum(vs[:5],Vector())/5;s['ring_centers']=[list(sum(vs[i:i+5],Vector())/5) for i in range(0,len(vs),5)]
 if row['role']=='primary_bough':primary=len(comps)
 if row['role']=='needle_shoot' and len(row['support_polyline'])==6:s['parent']=primary
 elif row['role']=='needle_shoot':s['parent']='axis'
 if row['role'] not in ['primary_bough','needle_shoot']:leader=len(comps)
 comps.append(s)
assert coveredv==set(range(len(wood.data.vertices))) and coveredf==set(range(len(wood.data.polygons))) and leader is not None
trunk.data.calc_loop_triangles();ids=list(range(*mapping['source_trunk_vertices']));im={v:i for i,v in enumerate(ids)};faces=[f for f in trunk.data.polygons if f.vertices[0] in im];assert all(all(i in im for i in f.vertices) for f in faces);faceids={f.index for f in faces};source_vs=[trunk.matrix_world@trunk.data.vertices[i].co for i in ids];source_faces=[[im[i] for i in f.vertices] for f in faces];source_triangles=[[im[i] for i in t.vertices] for t in trunk.data.loop_triangles if t.polygon_index in faceids]
assert len(source_faces)==5 and len(source_vs)==10
source_boundary_counts=collections.Counter(tuple(sorted((f[j],f[(j+1)%len(f)]))) for f in source_faces for j in range(len(f)));assert sum(v==1 for v in source_boundary_counts.values())==10
caps=[[4,3,2,1,0],[5,6,7,8,9]];cap_triangles=[[f[0],f[j],f[j+1]] for f in caps for j in range(1,4)]
source=solid(source_vs,source_faces+caps,source_triangles+cap_triangles,'legacy trunk section-envelope proxy; two analytical caps NOT model faces')
from mathutils.geometry import intersect_ray_tri
def actual_legacy_side_intersects(solid_wood):
 # Positive hit is actual existing-side surface evidence. No hit does not refute envelope embedding.
 for ta in source_triangles:
  a0,b0,c0=[source_vs[i] for i in ta]
  for f in solid_wood['triangles']:
   tri=[solid_wood['verts'][i] for i in f]
   for first,second in [(tri,[a0,b0,c0]),([a0,b0,c0],tri)]:
    for j in range(3):
     origin=first[j];direction=first[(j+1)%3]-origin;hit=intersect_ray_tri(second[0],second[1],second[2],direction,origin,True)
     if hit is not None and (hit-origin).dot(direction)>=0 and (hit-origin).length<=direction.length+1e-7:return True
 return False
contact_rows=[];needle_margins=[];blade_ids=set();min_area=float('inf')
for k,s in enumerate(comps):
 row=s['meta'];role=row['role'];supports=[source] if k==leader else ([source,comps[leader]] if role=='primary_bough' or s.get('parent')=='axis' else [comps[s['parent']]])
 results=[containment(s['root'],q) for q in supports];inside=[x for x in results if x['state']=='inside'];contact_rows.append({'wood_vertex_start':row['vertex_start'],'role':role,'support_labels':[x['label'] for x in supports],'root':list(s['root']),'results':results,'legacy_actual_side_surface_intersection':actual_legacy_side_intersects(s) if source in supports else None})
 if not inside:issues.append({'kind':'wood_root_not_strictly_inside_support','component':row['vertex_start'],'results':results,'legacy_actual_side_surface_intersection':actual_legacy_side_intersects(s) if source in supports else None})
 if role!='needle_shoot':continue
 if isinstance(s.get('parent'),int):assert max(abs(x-y) for p,q in zip(row['support_polyline'],comps[s['parent']]['ring_centers']) for x,y in zip(p,q))<2e-5,'Parent mapping not actual supporting tube'
 for b in range(row['needle_blade_start'],row['needle_blade_start']+row['needle_blade_count']):
  assert b not in blade_ids;blade_ids.add(b);off=5*b;expected=[[off,off+1,off+4],[off+1,off+2,off+4],[off+2,off+3,off+4],[off+3,off,off+4]]
  for j,face in enumerate(expected):
   f=fol.data.polygons[4*b+j];assert list(f.vertices)==face and 0<=f.material_index<3;v=[fol.data.vertices[i].co for i in face];area=(v[1]-v[0]).cross(v[2]-v[0]).length/2;assert area>0;min_area=min(min_area,area)
  result=containment(fol.matrix_world@fol.data.vertices[off].co,s)
  if result['state']!='inside':issues.append({'kind':'needle_root_not_strictly_inside_shoot','blade':b,'wood_start':row['vertex_start'],'result':result})
  else:needle_margins.append(result['margin'])
assert blade_ids==set(range(len(fol.data.vertices)//5)) and len(fol.data.vertices)%5==0 and len(fol.data.polygons)==4*len(blade_ids)
points=[o.matrix_world@v.co for o in [fol,wood] for v in o.data.vertices];bounds=[[min(v[k] for v in points) for k in range(3)],[max(v[k] for v in points) for k in range(3)]];route=json.load(open(a.route_report));assert route['model_sha256']=='c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd' and route['route_acceptance_pass'];gaps=[]
for prism in route['continuous_envelope']['prisms']:
 lo,hi=prism['bounds'];gap=max(max(lo[k]-bounds[1][k],bounds[0][k]-hi[k]) for k in range(3));assert gap>0;gaps.append(gap)
assert bounds[0][1]>40.6
report={'candidate_sha256':before,'mapping_sha256':sha(a.mapping),'geometry_and_attachment_pass':not issues,'issues':issues,'retained_trunk_attachment_semantics':{'actual_side_faces':5,'actual_open_boundary_edges':10,'analytical_caps_only_for_section_envelope':2,'actual_source_mesh_modified':False,'scope':'Legacy trunk is an open-sided-end tube. Root checks against its capped section envelope establish bounded embedding, not actual closed-volume intersection. Actual side-surface hits reported separately.'},'wood_components':len(comps),'wood_positive_volume_min':min(s['volume'] for s in comps),'needle_blades':len(blade_ids),'needle_min_area':min_area,'needle_inside_support_min_margin_m':min(needle_margins) if needle_margins else None,'wood_root_checks':contact_rows,'bounds':bounds,'known_route_separation':{'min_prism_axis_gap':min(gaps),'approach_bridge_north_guard40_6_margin':bounds[0][1]-40.6},'needle_semantics':'Open-backed four-triangle blades; no closed/manifold volume claim. Root attachment checked against actual closed shoot mesh.','scope':'NEW authored wood positive closed capped components and root-inside-support witnesses, not botanical/load certification. Original trunk is open-ended; its explicit section-envelope proxy is not actual model closure. Root inside parent interior establishes local contact, not dynamic branch strength. Bound-based clearance only current known route regions.','candidate_file_unchanged':sha(a.candidate)==before};Path(a.report).write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='wood_root_checks'},indent=2));assert not issues,'Attachment/geometry issues in report'
