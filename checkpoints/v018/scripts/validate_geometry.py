"""Independent actual western-cap course geometry. No source model saves."""
import argparse,bpy,json,hashlib,math,sys
from pathlib import Path
from collections import defaultdict,Counter
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--baseline-model',required=True);p.add_argument('--candidate',required=True);p.add_argument('--design',required=True);p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();source=Path(a.baseline_model);candidate=Path(a.candidate);source_sha=sha(source);candidate_sha=sha(candidate);assert source_sha=='9ed12e2dd4e21ee91ff65848d3c11601332a690ea80a880fb31bf41f1d7dd943'
design=json.load(open(a.design));params=design['parameters'];names=design['objects'];assert len(names)==8 and len(set(names))==8
TARGET='V002 | western lantern low slate cap'
bpy.ops.wm.open_mainfile(filepath=str(source.resolve()),use_scripts=False);o=bpy.data.objects[TARGET];assert not o.modifiers and len(o.data.vertices)==160 and len(o.data.polygons)==100
sv=[o.matrix_world@v.co for v in o.data.vertices];sf=[list(f.vertices) for f in o.data.polygons]
def source_signature(o):return hashlib.sha256(json.dumps({'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(f.vertices) for f in o.data.polygons],'material_indices':[f.material_index for f in o.data.polygons],'matrix':[list(r) for r in o.matrix_world]},sort_keys=True).encode()).hexdigest()
signature=source_signature(o)
# Precision bound derives from current source magnitude/float32 ULP, not the
# main crown's physical inset/bronze dimensions.
maxcoord=max(abs(c) for v in sv for c in v);TOL=4*2**(math.floor(math.log2(maxcoord))-23)
def planes(vs,fs):
 center=sum(vs,Vector())/len(vs);out=[]
 for f in fs:
  origin=sum((vs[i] for i in f),Vector())/len(f);n=sum(((vs[f[i]]-origin).cross(vs[f[(i+1)%len(f)]]-origin) for i in range(len(f))),Vector()).normalized()
  if n.dot(center-origin)>0:n=-n
  assert max(abs(n.dot(vs[i]-origin)) for i in f)<TOL
  out.append((n,n.dot(origin)))
 assert all(n.dot(v)-d<TOL for v in vs for n,d in out)
 return out
def source_component(lo,hi):
 vv=sv[lo:hi];ff=[[i-lo for i in f] for f in sf if all(lo<=i<hi for i in f)];return vv,ff,planes(vv,ff)
shell=source_component(0,16);finial=source_component(16,32);beams=[source_component(i,i+16) for i in range(32,160,16)]
def bbox(vs):return [[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]]
def boxgap(a,b):return math.sqrt(sum(max(a[0][k]-b[1][k],b[0][k]-a[1][k],0)**2 for k in range(3)))
def area(poly):return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(poly,poly[1:]+poly[:1])))*.5
def clip(poly,a,b):
 def d(q):return (b[0]-a[0])*(q[1]-a[1])-(b[1]-a[1])*(q[0]-a[0])
 out=[]
 for x,y in zip(poly,poly[1:]+poly[:1]):
  dx,dy=d(x),d(y)
  if dx>=0:out.append(x)
  if (dx>=0)!=(dy>=0):
   t=dx/(dx-dy);out.append((x[0]+t*(y[0]-x[0]),x[1]+t*(y[1]-x[1])))
 return out
def ccw(poly):
 return poly if sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(poly,poly[1:]+poly[:1]))>0 else poly[::-1]
def intersection_area(p,q):
 for aa,bb in zip(q,q[1:]+q[:1]):
  p=clip(p,aa,bb)
  if len(p)<3:return 0
 return area(p)
def convex_separated(vs,fs,other):
 vv,ff,pp=other
 if boxgap(bbox(vs),bbox(vv))>TOL:return True
 # Exact convex SAT axis families. Merely touching counts as not-separated,
 # requiring explicit assessment instead of a broad finial exemption.
 def edges(v,f):return [v[b]-v[a] for a,b in {tuple(sorted((p[i],p[(i+1)%len(p)]))) for p in f for i in range(len(p))}]
 pp1=planes(vs,fs);ee=edges(vs,fs);ee2=edges(vv,ff)
 for axis in [n for n,d in pp1+pp]+[x.cross(y) for x in ee for y in ee2]:
  if axis.length<1e-10:continue
  axis=axis.normalized();pa=[axis.dot(v) for v in vs];pb=[axis.dot(v) for v in vv]
  if max(pa)<min(pb)-TOL or max(pb)<min(pa)-TOL:return True
 return False
bpy.ops.wm.open_mainfile(filepath=str(candidate.resolve()),use_scripts=False);assert not bpy.data.objects[TARGET].modifiers;assert source_signature(bpy.data.objects[TARGET])==signature,'source roof signature changed'
actual={o.name for o in bpy.data.objects if o.name.startswith(design['object_prefix'])};assert actual==set(names)
results=[];allverts=[];finial_intersections=[];seam_margin=[]
for facet,name in enumerate(names):
 obj=bpy.data.objects[name];assert obj.type=='MESH' and not obj.modifiers and not obj.hide_render;assert [m.name for m in obj.data.materials]==['V002 | quiet blue-grey roof slate']
 shellface=shell[1][facet+2];facepoints=[shell[0][i] for i in shellface];n,d=shell[2][facet+2]
 low=sorted([q for q in facepoints if abs(q.z-min(v.z for v in facepoints))<TOL],key=lambda q:tuple(q));assert len(low)==2
 # Same geometric orientation regardless of source face winding.
 u=Vector((0,0,1)).cross(n).normalized();v=n.cross(u).normalized();origin=min(low,key=lambda q:q.dot(u));domain=ccw([((q-origin).dot(u),(q-origin).dot(v)) for q in facepoints]);domain_edges=list(zip(domain,domain[1:]+domain[:1]))
 me=obj.data;vv=[obj.matrix_world@q.co for q in me.vertices];allverts+=vv;parents=list(range(len(vv)))
 def root(i):
  while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
  return i
 for e in me.edges:
  x,y=map(root,e.vertices)
  if x!=y:parents[y]=x
 groups=defaultdict(list)
 for f in me.polygons:groups[root(f.vertices[0])].append(list(f.vertices))
 tiles=[];minvolume=1e9;minembed=1e9;edgecovered=0;facet_margin=[]
 gradient=(params['lip']-params['head'])/params['length'];row_delta=gradient*params['exposure'];assert row_delta>10*TOL
 for fs in groups.values():
  ids=sorted({i for f in fs for i in f});remap={x:i for i,x in enumerate(ids)};vs=[vv[i] for i in ids];ff=[[remap[i] for i in f] for f in fs];edgecounts=Counter(tuple(sorted((f[i],f[(i+1)%len(f)]))) for f in ff for i in range(len(f)));directions=Counter((f[i],f[(i+1)%len(f)]) for f in ff for i in range(len(f)))
  assert all(c==2 for c in edgecounts.values()) and all(c==directions[b,a] for (a,b),c in directions.items()),'tile closed orientation invalid'
  anchor=vs[0];volume=sum((vs[f[0]]-anchor).dot((vs[f[i]]-anchor).cross(vs[f[i+1]]-anchor))/6 for f in ff for i in range(1,len(f)-1));assert volume>1e-8;minvolume=min(minvolume,volume)
  heights=[n.dot(q)-d for q in vs];bottom=min(ff,key=lambda f:sum(heights[i] for i in f)/len(f));top=max(ff,key=lambda f:sum(heights[i] for i in f)/len(f));assert len(bottom)==len(top) and len(vs)==2*len(bottom)
  for i in bottom:
   margin=min(dd-nn.dot(vs[i]) for nn,dd in shell[2]);minembed=min(minembed,margin);assert margin>TOL,'tile bottom outside source shell';assert abs(heights[i]-params['bottom'])<2*TOL
  xy=[((vs[i]-origin).dot(u),(vs[i]-origin).dot(v)) for i in top];hh=[heights[i] for i in top];assert min(hh)>=params['head']-2*TOL and max(hh)<=params['lip']+2*TOL
  intercept=sum(h+gradient*q[1] for h,q in zip(hh,xy))/len(hh);row=round((intercept-params['lip'])/row_delta);assert max(abs(h-(intercept-gradient*q[1])) for h,q in zip(hh,xy))<2*TOL;assert abs(intercept-(params['lip']+row*row_delta))<2*TOL
  for i,q in zip(top,xy):
   for aa,bb in domain_edges:
    distance=((bb[0]-aa[0])*(q[1]-aa[1])-(bb[1]-aa[1])*(q[0]-aa[0]))/math.dist(aa,bb);assert distance>=params['inset']-2*TOL
    # Side seams only: original eave and tiny top-cap edges are not falsely
    # attributed to the bronze hip seams.
    if abs(aa[1]-bb[1])<TOL:continue
    if abs(distance-params['inset'])<2*TOL:
     margin=max(min(dd-nn.dot(vs[i]) for nn,dd in beam[2]) for beam in beams);assert margin>TOL,'actual bronze seam does not cover tile edge';facet_margin.append(margin);edgecovered+=1
  if not convex_separated(vs,ff,finial):finial_intersections.append({'facet':facet,'seed':min(ids),'bounds':bbox(vs)})
  poly=ccw(xy);assert area(poly)>=params['min_area']-TOL and min(max(q[k] for q in poly)-min(q[k] for q in poly) for k in range(2))>=params['min_span']-TOL;tiles.append({'row':row,'poly':poly,'intercept':intercept,'bounds':[[min(q[k] for q in poly) for k in range(2)],[max(q[k] for q in poly) for k in range(2)]],'topkey':tuple(sorted(tuple(round(c,5) for c in vs[i]) for i in top))})
 assert len({t['topkey'] for t in tiles})==len(tiles),'duplicate exposed tops'
 byrow=defaultdict(list)
 for t in tiles:byrow[t['row']].append(t)
 overlaps=0;mingap=1e9
 for row,tt in byrow.items():
  for j,t in enumerate(tt):
   for other in tt[j+1:]+byrow.get(row+1,[]):
    if any(t['bounds'][1][k]<=other['bounds'][0][k]+TOL or other['bounds'][1][k]<=t['bounds'][0][k]+TOL for k in range(2)):continue
    if intersection_area(t['poly'],other['poly'])>TOL*TOL:
     assert other['row']==row+1,'same row footprint overlap';gap=other['intercept']-t['intercept'];assert abs(gap-row_delta)<4*TOL and gap>TOL,'coplanar or unordered overlapping tops';mingap=min(mingap,gap);overlaps+=1
 assert overlaps>0 and edgecovered>0
 if 'tile_counts' in design:assert len(tiles)==design['tile_counts'][facet]
 results.append({'facet':facet,'name':name,'tile_count':len(tiles),'minimum_positive_volume':minvolume,'minimum_bottom_shell_margin':minembed,'adjacent_overlaps':overlaps,'minimum_overlap_top_separation':mingap,'bronze_edge_vertices':edgecovered,'minimum_actual_bronze_cover_margin':min(facet_margin),'bounds':bbox(vv)})
# Original eave octagon, not only rectangular bounds.
eave=ccw([(q.x,q.y) for q in shell[0][:8]])
for q in allverts:
 for aa,bb in zip(eave,eave[1:]+eave[:1]):assert (bb[0]-aa[0])*(q.y-aa[1])-(bb[1]-aa[1])*(q.x-aa[0])>=-TOL,'original octagonal eave silhouette exceeded'
 assert q.z<max(v.z for v in shell[0])+TOL and q.z>min(v.z for v in shell[0])-TOL
r={'pass':not finial_intersections,'baseline_sha256':source_sha,'candidate_sha256':candidate_sha,'actual_source_signature':signature,'precision_tolerance_from_source_float32_scale':TOL,'parameters':params,'facets':results,'tile_count':sum(q['tile_count'] for q in results),'finial_intersections_or_touching_uncertainties':finial_intersections,'bounds':bbox(allverts),'baseline_file_unchanged':sha(source)==source_sha,'candidate_file_unchanged':sha(candidate)==candidate_sha,'scope':'Actual tile component topology and signed volume, actual10-plane truncated-octagonal source-shell embedding, face-local overlap/top separation, actual8bronze seam halfspace cover, original octagonal eave/height and convex finial exclusion. No main-crown physical-margin assumptions, no waterproofing/history/load claims. Full source preservation is separate.'}
assert r['baseline_file_unchanged'] and r['candidate_file_unchanged'];Path(a.report).write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));assert r['pass'],'Inspect actual finial contact before any exemption'
