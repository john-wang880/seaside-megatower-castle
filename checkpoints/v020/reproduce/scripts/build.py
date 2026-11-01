"""Bounded additive west threshold craft prototype; no renders/source overwrite."""
import argparse,bpy,bmesh,math,json,sys,hashlib,collections
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--plan',required=True);p.add_argument('--output',required=True);p.add_argument('--report',required=True);args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);assert not Path(args.output).is_symlink() and not Path(args.report).is_symlink();src=Path(args.source).resolve();out=Path(args.output).resolve();rp=Path(args.report).resolve();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();SHA='e71778349c4c65eafbda3eb0a3d0753cd11e1b368a3456c4de1db2f4c0f8647a'
assert not sys.flags.optimize and sha(src)==SHA and not out.exists() and not out.is_symlink() and not rp.exists() and not rp.is_symlink() and len({src,out,rp})==3
plan=json.load(open(args.plan));assert plan['source_sha256']==SHA
bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False)
sys.path.insert(0,str(Path(__file__).resolve().parent));from deep_snapshot import mesh_snapshot,tree_snapshot,digest
oldmeshes={m.name:mesh_snapshot(m) for m in bpy.data.meshes};oldmaterials={m.name:digest(tree_snapshot(m.node_tree)) for m in bpy.data.materials};oldworld=digest(tree_snapshot(bpy.context.scene.world.node_tree))
hosts={}
for h in plan['hosts']:
 o=bpy.data.objects[h['object']];assert not o.modifiers and o.data.users==1
 c=h['component'];ids=sorted(int(i)for i in c['vertices']);index={i:j for j,i in enumerate(ids)};vs=[o.matrix_world@o.data.vertices[i].co for i in ids]
 assert all(tuple(v)==tuple(c['vertices'][str(i)]) for i,v in zip(ids,vs))
 fs=[[index[i] for i in f['ids']]for f in c['faces']];center=sum(vs,Vector())/len(vs);hosts[o.name]=((BVHTree.FromPolygons([v-center for v in vs],fs,all_triangles=False),center),h)
DIRECTIONS=[Vector(v).normalized()for v in [(1,.371,.613),(.217,1,.489),(.529,.193,1)]]
def inside(pair,p):
 bvh,origin=pair;votes=[]
 for direction in DIRECTIONS:
  q=Vector(p)-origin;n=0
  for _ in range(300):
   hit,_,_,dist=bvh.ray_cast(q,direction,1000)
   if hit is None:break
   n+=1;q=hit+direction*1e-5
  else:raise RuntimeError('Ray loop')
  votes.append(bool(n%2))
 return votes==[True]*3
collection='UNACCEPTED | v020 western threshold craft';assert collection not in bpy.data.collections;C=bpy.data.collections.new(collection);bpy.context.scene.collection.children.link(C);mat=bpy.data.materials['West_Cool weathered limestone'];rows=[]
def add(name,parts,host):
 assert name not in bpy.data.objects and name not in bpy.data.meshes
 verts=[];faces=[];ranges=[]
 for vs,fs,witness in parts:
  offset=len(verts);bm=bmesh.new();bv=[bm.verts.new(v) for v in vs];bm.verts.ensure_lookup_table()
  for f in fs:bm.faces.new([bv[i]for i in f])
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));volume=bm.calc_volume(signed=True);assert volume>1e-9
  bm.verts.index_update();vs=[list(v.co)for v in bm.verts];fs=[[v.index for v in f.verts]for f in bm.faces];assert all(e.is_manifold for e in bm.edges);bm.free()
  center=sum((Vector(v)for v in vs),Vector())/len(vs);bvh=(BVHTree.FromPolygons([Vector(v)-center for v in vs],fs),center);assert inside(bvh,witness) and inside(hosts[host][0],witness),('embedded witness failed',name,witness)
  verts.extend(vs);faces.extend([[offset+i for i in f]for f in fs]);ranges.append({'first_vertex':offset,'vertex_count':len(vs),'faces':len(fs),'volume':volume,'embedded_witness':witness,'three_ray_inside_addition_and_host':True})
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(mat);me.update();ob=bpy.data.objects.new(name,me);C.objects.link(ob)
 rows.append({'object':name,'host':host,'host_seed':hosts[host][1]['component']['seed'],'parts':ranges,'vertices':len(verts),'faces':len(faces),'bounds':[[min(v[k]for v in verts)for k in range(3)],[max(v[k]for v in verts)for k in range(3)]]})
def extrude_x(poly,x0,x1):
 n=len(poly);return [(x,y,z)for x in [x0,x1]for y,z in poly],[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
# Every source aperture knot in a block is retained. Analytic endpoint samples
# lie outside the source chordal aperture; +6mm outward margin never narrows it.
P=plan['proposal'];x0,x1=P['arch_x'];parts=[]
for i in range(P['arch_stones']):
 lo=math.pi*i/13+P['angular_joint_half_gap'];hi=math.pi*(i+1)/13-P['angular_joint_half_gap'];ts=[lo]+[math.pi*j/24 for j in range(25)if lo<math.pi*j/24<hi]+[hi]
 poly=[(38+(2.2+.006)*math.cos(t),29.05+(2+.006)*math.sin(t))for t in ts]+[(38+(2.2+.20)*math.cos(t),29.05+(2+.20)*math.sin(t))for t in reversed(ts)]
 vs,fs=extrude_x(poly,x0,x1);t=(lo+hi)/2;w=[-71.185,38+2.3*math.cos(t),29.05+2.1*math.sin(t)];parts.append((vs,fs,w))
add('V020 candidate | west portal radial stones',parts,'V007 | western stonework with actual bridgehead passage')
parts=[]
for spec in P['imposts']:
 y0,y1=spec['y'];z0,z1=spec['z'];vs,fs=extrude_x([(y0,z0),(y1,z0),(y1,z1),(y0,z1)],x0,x1);parts.append((vs,fs,[-71.185,(y0+y1)/2,(z0+z1)/2]))
add('V020 candidate | restrained portal imposts',parts,'V007 | western stonework with actual bridgehead passage')
def top(x):return 26.45+(x+90)*(1.7/18) if x<-72 else 28.15
for side,(y0,y1) in zip(['south','north'],P['coping_y']):
 parts=[];knots=P['coping_x_knots']
 for i,(a,b)in enumerate(zip(knots,knots[1:])):
  aa=a+(P['coping_joint_gap']/2 if i else 0);bb=b-(P['coping_joint_gap']/2 if i<len(knots)-2 else 0);zz=[top(aa),top(bb)]
  vs=[(x,y,z)for y in [y0,y1]for x,z in [(aa,zz[0]-.025),(bb,zz[1]-.025),(bb,zz[1]+.07),(aa,zz[0]+.07)]]
  fs=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];mid=(aa+bb)/2;parts.append((vs,fs,[mid,(y0+y1)/2,top(mid)-.012]))
 add('V020 candidate | '+side+' short approach coping',parts,'V009 | '+side+' approach parapet')
assert sum(len(r['parts'])for r in rows)==23
assert all(mesh_snapshot(bpy.data.meshes[n])==m for n,m in oldmeshes.items());assert {m.name:digest(tree_snapshot(m.node_tree))for m in bpy.data.materials}==oldmaterials;assert digest(tree_snapshot(bpy.context.scene.world.node_tree))==oldworld
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out),copy=True);assert sha(src)==SHA
report={'status':'UNACCEPTED ARTISTIC PROTOTYPE; INDEPENDENT GEOMETRY AND VISUAL QA PENDING','source_sha256':SHA,'source_unchanged':True,'plan_sha256':sha(args.plan),'candidate_sha256':sha(out),'candidate_bytes':out.stat().st_size,'collection':collection,'objects':rows,'total_components':23,'total_vertices':sum(r['vertices']for r in rows),'total_faces':sum(r['faces']for r in rows),'checks':{'all_source_meshes_exact':True,'all_material_graphs_exact':True,'world_exact':True,'closed_oriented_positive_additions':True,'actual_host_embedded_witnesses':True},'limits':['Witness tests prove provisional intersection only, not full architectural support certification','Independent full opening/route and source-state checks pending','No visual acceptance, no new archive/version publication']};rp.write_text(json.dumps(report,indent=2));print('BUILD_PASS',report['candidate_sha256'],flush=True)
