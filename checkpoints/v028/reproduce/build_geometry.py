"""Pinned, pure-Python local receiving-chamber geometry. Never imports bpy."""
import argparse,collections,hashlib,itertools,json,math,struct,sys
from pathlib import Path
import planar
SOURCE='37c0db0e67d0a0a57b7542c899f687d129a6b31208b43e03857a1f3d9e88a255'
EXPORT='83593439fc128700af9302eb1e53185b3f782b00f39e1b7cb972a72823dc362e'
MANIFEST='9e093cae6a74c6fb849c9b7d28ab35abdd974c4f32ae4e6c95af0277cbc58320'
PLANAR='f1039af8c08ad7d5f0a9012d92af2d903aead318a890adb2944ad7721ea8b88b'
NAMES=['foundation','ashlar','east lining']
TARGETS=[('V012 | foundation with continuous L-shaped passage',128),('V012 | ashlar with bounded entrance and north stairwell',13132),('V012 | hall east stone lining',0)]
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def norm(a):return math.sqrt(dot(a,a))
def f32(x):return struct.unpack('f',struct.pack('f',x))[0]
def area(poly):
 if len(poly)<3:return 0.
 a=poly[0];v=(0.,0.,0.)
 for b,c in zip(poly[1:],poly[2:]):v=tuple(x+y for x,y in zip(v,cross(sub(b,a),sub(c,a))))
 return norm(v)/2

def clip(poly,ax,k,lower):
 """Keep coordinate >= k if lower; <= k otherwise. No proximity snapping."""
 if not poly:return []
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=(a[ax]-k)*(1 if lower else -1);db=(b[ax]-k)*(1 if lower else -1)
  if da>=0:out.append(a)
  if (da<0 and db>0)or(da>0 and db<0):
   t=(k-a[ax])/(b[ax]-a[ax]);p=[a[j]+t*(b[j]-a[j])for j in range(3)];p[ax]=k;out.append(tuple(p))
 return clean(out)
def clean(p):
 q=[]
 for v in p:
  if not q or v!=q[-1]:q.append(v)
 if len(q)>1 and q[0]==q[-1]:q.pop()
 return q if len(q)>=3 else []
def insidebox(p,b):return all(b[0][a]<p[a]<b[1][a]for a in range(3))
def inboxclosed(p,b):return all(b[0][a]<=p[a]<=b[1][a]for a in range(3))
def intersect(poly,b):
 for a in range(3):
  poly=clip(poly,a,b[0][a],True);poly=clip(poly,a,b[1][a],False)
 return poly

def subtract_box(poly,b):
 # Disjoint complement pieces: successively retain one outside halfspace,
 # restricting the remainder to all earlier inside halfspaces.
 rem=poly;out=[]
 for a in range(3):
  for k,lower in ((b[0][a],True),(b[1][a],False)):
   piece=clip(rem,a,k,not lower)
   if area(piece)>1e-14:out.append(piece)
   rem=clip(rem,a,k,lower)
 return out

def winding(p,c):
 total=0.
 for ids in c['local_triangles']:
  a,b,z=[sub(c['vertices'][i],p)for i in ids];la,lb,lz=map(norm,(a,b,z))
  total+=2*math.atan2(dot(a,cross(b,z)),la*lb*lz+dot(a,b)*lz+dot(b,z)*la+dot(z,a)*lb)
 return total/(4*math.pi)

def face_triangles(c,f):
 offset=0
 for face in c['local_faces']:
  count=len(face)-2
  if face is f:
   ts=c['local_triangles'][offset:offset+count]
   require(len(ts)==count and all(set(t)<=set(f)for t in ts),'ordered authoritative loop triangles')
   return ts
  offset+=count
 raise RuntimeError('face identity missing')

def rectangle(ax,k,u,v,a,b,c,d,sgn):
 # cyclic u,v ordering gives cross(e_u,e_v)=e_ax
 p=[]
 for x,y in ((a,c),(b,c),(b,d),(a,d)):
  q=[0.,0.,0.];q[ax]=k;q[u]=x;q[v]=y;p.append(tuple(q))
 return p if sgn>0 else p[::-1]

def merge_rects(records,planes):
 """Greedy maximal rectangles in exact plane-index masks; holes preserved."""
 result=[]
 for key,cells in sorted(records.items()):
  ax,plane,sgn,kind=key;u=(ax+1)%3;v=(ax+2)%3;todo=set(cells)
  while todo:
   i,j=min(todo);ie=i+1
   while (ie,j)in todo:ie+=1
   je=j+1
   while all((x,je)in todo for x in range(i,ie)):je+=1
   for x in range(i,ie):
    for y in range(j,je):todo.remove((x,y))
   result.append((rectangle(ax,planes[ax][plane],u,v,planes[u][i],planes[u][ie],planes[v][j],planes[v][je],sgn),{'kind':kind,'axis':ax,'plane':planes[ax][plane],'sign':sgn}))
 return result

def construct(export,plan_dir):
 require(not sys.flags.optimize,'optimized Python unsupported')
 require(sha(plan_dir/'MANIFEST.json')==MANIFEST,'wrong frozen plan manifest')
 require(sha(Path(__file__).with_name('planar.py'))==PLANAR,'planar helper changed')
 manifest=json.loads((plan_dir/'MANIFEST.json').read_text())
 for n,h in manifest.items():require(sha(plan_dir/n)==h,'input hash '+n)
 require(sha(export)==EXPORT,'wrong source export')
 d=json.loads(export.read_text());require(d['source_sha256']==SOURCE and d['source_unchanged'],'wrong source binding')
 proof=json.loads((plan_dir/'guard_partition_proof.json').read_text());spec=json.loads((plan_dir/'SPEC.json').read_text());mapping=json.loads((plan_dir/'target_mapping_proof.json').read_text());attrs=json.loads((plan_dir/'ATTRIBUTES.json').read_text())
 require(proof['pass'] and proof['source_sha256']==SOURCE,'unapproved proof')
 G=proof['guard_union'];sleeve=proof['proposed_sleeve'];cuts=[spec['room_clear'],spec['connector_clear']];retain=spec['retained_piers']+[spec['retained_roof_band']]
 require(G==[[[6.9,32.4,28.9],[15.1,40.6,32.15]],[[5.35,36.65,28.65],[7.1,38.35,31.6]]],'guard changed')
 cs=[next(c for c in d['components']if(c['object'],c['seed'])==t)for t in TARGETS]
 rawmesh=[[]for _ in range(4)];affected=[];remote=[];planes=[set()for _ in range(3)]
 for b in G+[sleeve]+cuts+retain:
  for ax in range(3):planes[ax].update([b[0][ax],b[1][ax]])
 for ci,c in enumerate(cs):
  for fi,f in enumerate(c['local_faces']):
   poly=[tuple(c['vertices'][i])for i in f];ts=face_triangles(c,f)
   require(abs(sum(area([tuple(c['vertices'][i])for i in t])for t in ts)-area(poly))<1e-8,'authoritative triangle area')
   hit=any(area(intersect([tuple(c['vertices'][i])for i in t],b))>1e-13 for t in ts for b in G)
   lineage={'source_object':c['object'],'source_face':c['faces'][fi]['id']}
   if not hit:
    rawmesh[ci].append((poly,dict(lineage,kind='remote_original')));remote.append(lineage);continue
   affected.append(lineage)
   axes=[a for a in range(3)if max(v[a]for v in poly)==min(v[a]for v in poly)]
   require(len(axes)==1,'non-axis affected face');planes[axes[0]].add(poly[0][axes[0]])
   for t in ts:
    parts=[[tuple(c['vertices'][i])for i in t]]
    for b in G:parts=[q for p in parts for q in subtract_box(p,b)]
    for p in parts:
     rawmesh[ci].append((p,dict(lineage,kind='clipped_source_triangle',source_triangle=t)))
 require(len(remote)==112 and len(affected)==8,'preservation face classification changed')
 # Restrict coordinate planes to global guard bounds; each meaningful source
 # plane crossing guard was independently discovered above.
 planes=[sorted(p)for p in planes];shape=[len(p)-1 for p in planes];cells={};maxres=0.
 for ix in itertools.product(*(range(n)for n in shape)):
  p=tuple((planes[a][ix[a]]+planes[a][ix[a]+1])/2 for a in range(3))
  if not any(insidebox(p,b)for b in G):continue
  ws=[winding(p,c)for c in cs];res=max(min(abs(w),abs(abs(w)-1))for w in ws);maxres=max(res,maxres);require(res<1e-6,'ambiguous cell winding')
  old=tuple(abs(w)>.5 for w in ws);new=(any(old)or insidebox(p,sleeve))and not(any(insidebox(p,b)for b in cuts)and not any(insidebox(p,b)for b in retain))
  cells[ix]=(old,new)
 records=[collections.defaultdict(set)for _ in range(4)]
 for ix,(old,new)in cells.items():
  for ax in range(3):
   u=(ax+1)%3;v=(ax+2)%3
   for sign in (-1,1):
    nb=list(ix);nb[ax]+=sign;nb=tuple(nb);plane=ix[ax]+(sign>0);other=cells.get(nb)
    if new and(other is None or not other[1]):records[3][(ax,plane,sign,'guard_interface'if other is None else'new_local_boundary')].add((ix[u],ix[v]))
    if other is None:
     for ci,inside in enumerate(old):
      if inside:records[ci][(ax,plane,-sign,'buried_guard_cap')].add((ix[u],ix[v]))
 # Recover affected original face domains before sewing, removing artificial
 # clipping rays that would otherwise subdivide remote shared source edges.
 for ci,c in enumerate(cs):
  grouped=collections.defaultdict(list);keep=[]
  for p,l in rawmesh[ci]:
   if l['kind']=='clipped_source_triangle':grouped[l['source_face']].append(p)
   else:keep.append((p,l))
  for fid,parts in grouped.items():
   fi=next(i for i,f in enumerate(c['faces'])if f['id']==fid);orig=[tuple(c['vertices'][i])for i in c['local_faces'][fi]]
   ax=next(a for a in range(3)if len(set(p[a]for p in orig))==1)
   for tri in planar.triangulate(parts,orig,ax):keep.append((tri,{'kind':'clipped_source_domain','source_object':c['object'],'source_face':fid,'derivation':'union of authoritative clipped loop triangles'}))
  rawmesh[ci]=keep
 for i,r in enumerate(records):rawmesh[i]+=merge_rects(r,planes)
 # Common float32 registry before topology sewing; exact source coordinates are
 # already float32, and original remote vertices therefore remain bit-exact.
 registry={};maxquant=0.;collapsed=[]
 for mi,ps in enumerate(rawmesh):
  qp=[]
  for p,l in ps:
   q=[]
   for v in p:
    vv=tuple(f32(x)for x in v);maxquant=max(maxquant,max(abs(x-y)for x,y in zip(v,vv)));registry.setdefault(vv,len(registry));q.append(vv)
   q=clean(q)
   if area(q)<=1e-14:
    collapsed.append({'mesh':mi,'lineage':l,'original_area':area(p)});continue
   qp.append((q,l))
  rawmesh[mi]=qp
 # Propagate every exact collinear knot to all affected face edges. Remote
 # source face cycles must never change; reject rather than weaken contract.
 points=list(registry);meshes=[]
 for mi,ps in enumerate(rawmesh):
  ownpoints=set(v for p,l in ps for v in p)
  points=sorted(ownpoints | {v for v in registry if any(inboxclosed(v,[[f32(x)for x in b[0]],[f32(x)for x in b[1]]]) and any(v[a]in(f32(b[0][a]),f32(b[1][a]))for a in range(3))for b in G)})
  vv=[];index={};ff=[];ll=[]
  for p,l in ps:
   sewn=[]
   for a,b in zip(p,p[1:]+p[:1]):
    ab=sub(b,a);den=dot(ab,ab);knots=[]
    for q in points:
     if q==a or q==b:continue
     aq=sub(q,a);t=dot(aq,ab)/den
     if 0<t<1 and norm(cross(aq,ab))<=1e-11*max(1.,norm(ab)):knots.append((t,q))
    require(not knots or l['kind']!='remote_original','remote face edge would require split '+str((mi,l,a,b,knots)))
    sewn.append(a);sewn.extend(q for _,q in sorted(knots))
   face=[]
   for q in sewn:
    if q not in index:index[q]=len(vv);vv.append(q)
    face.append(index[q])
   ff.append(face);ll.append(l)
  meshes.append({'name':'V028 | '+NAMES[mi]+' outside chamber guard'if mi<3 else'V028 | local receiving chamber shell','vertices':vv,'faces':ff,'face_lineage':ll,'material_index':0,'use_smooth':False,'uniform_attributes':{'select_vertex':True,'select_edge':True,'select_face':True,'sharp_face':True,'edge_seam':False,'edge_sharp':False},'attribute_provenance':'source uniform layers, original corner normals derived flat'})
 diagnostics=[]
 for m in meshes:
  keys=[tuple(sorted(f))for f in m['faces']]
  require(len(set(keys))==len(keys),'duplicate polygon')
  for f,l in zip(m['faces'],m['face_lineage']):
   if l['kind']=='remote_original':
    c=next(c for c in cs if c['object']==l['source_object']);fi=next(i for i,r in enumerate(c['faces'])if r['id']==l['source_face'])
    require([tuple(m['vertices'][i])for i in f]==[tuple(c['vertices'][i])for i in c['local_faces'][fi]],'remote polygon changed')
  directed=collections.Counter((a,b)for f in m['faces']for a,b in zip(f,f[1:]+f[:1]));bad=[(e,n,directed[(e[1],e[0])])for e,n in directed.items()if n!=1 or directed[(e[1],e[0])]!=1]
  volume=0.;center=tuple(sum(v[a]for v in m['vertices'])/len(m['vertices'])for a in range(3))
  for f in m['faces']:
   p=[sub(m['vertices'][i],center)for i in f]
   volume+=sum(dot(p[0],cross(b,c))/6 for b,c in zip(p[1:],p[2:]))
  diagnostics.append({'name':m['name'],'vertices':len(m['vertices']),'faces':len(m['faces']),'triangles':sum(len(f)-2 for f in m['faces']),'volume':volume,'bad_edges':bad[:30],'bad_edge_count':len(bad)})
 total=sum(x['triangles']for x in diagnostics)
 targets=[]
 for ci,t in enumerate(mapping['targets']):
  targets.append({'object':t['object'],'evaluated_seed':t['raw_and_evaluated_seed'],'raw_vertex_ids':t['vertex_ids'],'mask_name':'V028 | receiving chamber original component mask','group_name':'V028 | receiving chamber preserved original component'})
 result={'source_sha256':SOURCE,'input_hashes':{'export':EXPORT,'plan_manifest':MANIFEST,'builder':sha(Path(__file__)),'planar':PLANAR,**manifest},'meshes':meshes,'targets':targets,'preservation':{'remote_faces':remote,'affected_faces':affected},'counts':diagnostics,'total_triangles':total,'registry':{'coordinate_count':len(registry),'max_coordinate_quantization':maxquant,'collapsed_faces':collapsed,'coordinate_planes':planes},'cell_count':len(cells),'max_winding_residual':maxres,'pass':not any(d['bad_edge_count']or d['volume']<=0 for d in diagnostics)and total<=2000}
 return result

def main():
 require(not sys.flags.optimize,'optimized Python unsupported')
 ap=argparse.ArgumentParser();ap.add_argument('--export',required=True,type=Path);ap.add_argument('--plan-dir',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);a=ap.parse_args()
 require(not a.output.exists()and not a.output.is_symlink(),'output exists');require(a.export.resolve()!=a.output.resolve(),'source alias')
 before={p:sha(p)for p in [Path(__file__),Path(__file__).with_name('planar.py'),a.export,*a.plan_dir.glob('*')]if p.is_file()}
 r=construct(a.export,a.plan_dir)
 require(all(sha(p)==h for p,h in before.items()),'input changed')
 # A failing payload is diagnostic-only and never advertises build acceptance.
 with a.output.open('x')as f:json.dump(r,f,indent=2)
 print(json.dumps({'pass':r['pass'],'counts':r['counts'],'total_triangles':r['total_triangles'],'cell_count':r['cell_count']}))
 if not r['pass']:raise SystemExit(2)
if __name__=='__main__':main()
