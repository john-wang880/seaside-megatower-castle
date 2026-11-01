"""Technical planar union of only two authored springer/impost pairs. No render."""
import bpy,bmesh,json,hashlib,sys,argparse,math
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--input-sha256',required=True);p.add_argument('--build-report',required=True);p.add_argument('--output',required=True);p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);assert not Path(a.output).is_symlink() and not Path(a.report).is_symlink();src=Path(a.input).resolve();out=Path(a.output).resolve();rp=Path(a.report).resolve();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(src);assert before==a.input_sha256 and len(a.input_sha256)==64;assert len({src,out,rp,Path(a.build_report).resolve()})==4 and not out.exists() and not rp.exists()
bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False);sys.path.insert(0,str(Path(__file__).resolve().parent));from deep_snapshot import mesh_snapshot,tree_snapshot,digest
arch=bpy.data.objects['V020 candidate | west portal radial stones'];impost=bpy.data.objects['V020 candidate | restrained portal imposts'];originals={m.name:mesh_snapshot(m)for m in bpy.data.meshes if m not in [arch.data,impost.data]};materials={m.name:digest(tree_snapshot(m.node_tree))for m in bpy.data.materials};build=json.load(open(a.build_report));assert build['candidate_sha256']==before and build['source_sha256']=='e71778349c4c65eafbda3eb0a3d0753cd11e1b368a3456c4de1db2f4c0f8647a';ar=next(r for r in build['objects']if r['object']==arch.name);im=next(r for r in build['objects']if r['object']==impost.name)
def piece(o,r):
 first=r['first_vertex'];n=r['vertex_count'];return {'vertices':[list(v.co)for v in o.data.vertices[first:first+n]],'faces':[[i-first for i in f.vertices]for f in o.data.polygons if first<=f.vertices[0]<first+n]}
def measure(s):
 bm=bmesh.new();vs=[bm.verts.new(v)for v in s['vertices']]
 for f in s['faces']:bm.faces.new([vs[i]for i in f])
 closed=all(e.is_manifold for e in bm.edges);center=sum((v.co for v in bm.verts),Vector())/len(bm.verts) if bm.verts else Vector()
 for v in bm.verts:v.co-=center
 volume=bm.calc_volume(signed=True);bm.free();return {'closed':closed,'volume':volume,'faces':len(s['faces'])}
def boolean(A,B,op):
 objs=[]
 try:
  for i,s in enumerate([A,B]):
   m=bpy.data.meshes.new('TEMP union audit mesh');m.from_pydata(s['vertices'],[],s['faces']);m.update();o=bpy.data.objects.new('TEMP union audit object',m);bpy.context.scene.collection.objects.link(o);objs.append(o)
  mod=objs[0].modifiers.new('Exact new-piece '+op,'BOOLEAN');mod.operation=op;mod.solver='EXACT';mod.object=objs[1];dg=bpy.context.evaluated_depsgraph_get();eo=objs[0].evaluated_get(dg);m=eo.to_mesh();result={'vertices':[list(v.co)for v in m.vertices],'faces':[list(f.vertices)for f in m.polygons]};eo.to_mesh_clear();return result
 finally:
  for o in objs:m=o.data;bpy.data.objects.remove(o,do_unlink=True);bpy.data.meshes.remove(m)
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def sub(a,b):return (a[0]-b[0],a[1]-b[1])
def area(poly):return abs(sum(cross(a,b)for a,b in zip(poly,poly[1:]+poly[:1])))/2
def frontpoly(S):
 xmin=min(v[0]for v in S['vertices']);f=next(f for f in S['faces']if all(S['vertices'][i][0]==xmin for i in f));poly=[tuple(S['vertices'][i][1:])for i in f]
 if sum(cross(a,b)for a,b in zip(poly,poly[1:]+poly[:1]))<0:poly.reverse()
 return poly
def within(p,poly):
 value=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:value=not value
 return value
def boundary(A,B,union):
 segments=[];cert=[]
 for label,poly,other in [('arch',A,B),('impost',B,A)]:
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
    if inside!=union:
     x=(a[0]+d[0]*t0,a[1]+d[1]*t0);y=(a[0]+d[0]*t1,a[1]+d[1]*t1);segments.append((x,y));cert.append({'source':label,'edge':i,'parameter_interval':[t0,t1],'midpoint_inside_other':inside,'ends':[x,y]})
 assert segments
 ordered=[segments.pop(0)];poly=[ordered[0][0]]
 while segments:
  last=ordered[-1][1];matches=[i for i,(x,y)in enumerate(segments)if math.dist(x,last)<1e-8];assert len(matches)==1,(last,matches);n=segments.pop(matches[0]);ordered.append(n);poly.append(n[0])
 assert math.dist(ordered[-1][1],poly[0])<1e-8
 return poly,cert

def planar_union(A,B):
 pa,pb=frontpoly(A),frontpoly(B);u,edges=boundary(pa,pb,True);inter,iedges=boundary(pa,pb,False);expected=area(pa)+area(pb)-area(inter);assert abs(area(u)-expected)<1e-10
 x0=min(v[0]for v in A['vertices']);x1=max(v[0]for v in A['vertices']);n=len(u);vs=[(x,y,z)for x in [x0,x1]for y,z in u];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
 # Positive orientation for X-extruded YZ polygons.
 U={'vertices':vs,'faces':fs}
 if measure(U)['volume']<0:U['faces']=[list(reversed(f))for f in fs]
 return U,{'old_arch_area':area(pa),'old_impost_area':area(pb),'actual_intersection_area':area(inter),'union_area':area(u),'area_identity_error':area(u)-expected,'depth':x1-x0,'exterior_source_edge_intervals':edges,'intersection_boundary_edge_intervals':iedges,'single_closed_boundary':True,'method':'Split actual front polygons at every edge crossing; retain only source subedges outside other polygon; assemble single exterior cycle. Intersection uses complementary inside subedges. No displaced exterior edges.'}
parts=[];mapping=[];proof=[]
for j,r in enumerate(ar['parts']):
 A=piece(arch,r);oldseed=r['first_vertex']
 if j in [0,12]:
  ir=im['parts'][1 if j==0 else 0];B=piece(impost,ir);I=boolean(A,B,'INTERSECT');U,planarproof=planar_union(A,B);ma,mb,mi,mu=[measure(x)for x in [A,B,I,U]]
  assert all(x['closed'] and x['volume']>0 for x in [ma,mb,mi,mu]);expected=ma['volume']+mb['volume']-mi['volume'];assert abs(mu['volume']-expected)<2e-7,(mu,expected)
  differences={'planar_occupied_set_proof':planarproof}
  bounds=lambda s:[[min(v[k]for v in s['vertices'])for k in range(3)],[max(v[k]for v in s['vertices'])for k in range(3)]]
  expectedbounds=[[min(bounds(A)[0][k],bounds(B)[0][k])for k in range(3)],[max(bounds(A)[1][k],bounds(B)[1][k])for k in range(3)]];assert all(abs(bounds(U)[a][k]-expectedbounds[a][k])<1e-8 for a in range(2)for k in range(3))
  assert all(abs(v[0]+71.48)<1e-5 or abs(v[0]+71.17)<1e-5 for v in U['vertices'])
  proof.append({'old_arch_seed':oldseed,'old_impost_seed':ir['first_vertex'],'old_arch':ma,'old_impost':mb,'intersection':mi,'union':mu,'sum_minus_intersection':expected,'volume_error':mu['volume']-expected,'bidirectional_occupied_set_difference':differences,'union_bounds_exact':True,'all_vertices_original_two_extrusion_planes':True});part=U
 else:part=A
 mapping.append({'old_arch_seed':oldseed,'new_arch_seed':sum(len(x['vertices'])for x in parts),'new_vertex_count':len(part['vertices']),'unchanged_component_under_reindex':j not in[0,12]});parts.append(part)
verts=[];faces=[]
for part in parts:
 off=len(verts);verts.extend(part['vertices']);faces.extend([[off+i for i in f]for f in part['faces']])
oldmesh=arch.data;newmesh=bpy.data.meshes.new(oldmesh.name+' joined');newmesh.from_pydata(verts,[],faces);newmesh.materials.append(oldmesh.materials[0]);newmesh.update();arch.data=newmesh;oldname=oldmesh.name;bpy.data.meshes.remove(oldmesh);newmesh.name=oldname
imname=impost.name;immesh=impost.data;bpy.data.objects.remove(impost,do_unlink=True);bpy.data.meshes.remove(immesh)
assert all(mesh_snapshot(bpy.data.meshes[n])==v for n,v in originals.items());assert {m.name:digest(tree_snapshot(m.node_tree))for m in bpy.data.materials}==materials
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out),copy=True);assert sha(src)==before
rp.write_text(json.dumps({'status':'TECHNICAL UNION PROTOTYPE; INDEPENDENT QA AND ART REVIEW PENDING','input_sha256':before,'input_unchanged':True,'candidate_sha256':sha(out),'candidate_bytes':out.stat().st_size,'source_canonical_sha256':'e71778349c4c65eafbda3eb0a3d0753cd11e1b368a3456c4de1db2f4c0f8647a','arch_object':arch.name,'removed_consumed_authored_object':imname,'component_count':21,'mapping':mapping,'union_proofs':proof,'all_other_meshes_exact':True,'all_material_graphs_exact':True,'scope':'Only new springer/impost pairs planarYZunion; no original source edits, dimensions/style unchanged; no renders'},indent=2));print('UNION_PASS',sha(out),flush=True)
