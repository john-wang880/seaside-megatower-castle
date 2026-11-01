"""Bounded exact evaluated-solid union. No rendering or canonical save."""
import argparse,collections,hashlib,json,os,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
def need(ok,message):
 if not ok:raise RuntimeError(message)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def safe(p,exists=False):
 p=Path(p).expanduser().absolute();need('..'not in p.parts and all(not x.is_symlink()for x in[p,*p.parents])and p.resolve()==p,'Aliased path refused')
 if exists:need(p.is_file(),'Missing input')
 else:need(p.parent.is_dir()and not os.path.lexists(p),'Output/report exists or parent missing')
 return p
def publish(pairs):
 made=[]
 try:
  for temp,dest in pairs:
   safe(dest);owned=os.stat(temp);os.link(temp,dest);made.append((dest,owned))
 except BaseException:
  for dest,owned in reversed(made):
   try:
    now=os.lstat(dest)
    if(now.st_dev,now.st_ino)==(owned.st_dev,owned.st_ino):os.unlink(dest)
   except FileNotFoundError:pass
  raise

PINNED={'plan.json': '2d4673f76244d1c7d1bf40f002370e219f35db7198ba413a309a6008f0384e78', 'support_envelope.json': '8fe6d70b4b6f24b5ae83a4bfb2df3734d3644f5ca2fa229a20478e1cae60352e', 'snapshot_support.py': 'ef8b575c70fbb394bfd76cba93b97bc07a6c03abdfe7f4eb2752cfd236be6249'}
def main():
 need(not sys.flags.optimize,'Optimized Python refused');ap=argparse.ArgumentParser()
 for k in ['source','output','report']:ap.add_argument('--'+k,required=True)
 a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);src=safe(a.source,True);out=safe(a.output);rep=safe(a.report)
 need(len({src,out,rep})==3 and out.suffix=='.blend'and rep.suffix=='.json','Invalid roles')
 for n,h in PINNED.items():need(sha(ROOT/n)==h,'Pinned dependency changed')
 plan=json.loads((ROOT/'plan.json').read_text());need(sha(src)==plan['source_sha256']and src.stat().st_size==plan['source_bytes'],'Source mismatch');scriptsha=sha(__file__)
 import bpy,bmesh,math
 from mathutils import Vector
 from mathutils.bvhtree import BVHTree
 from mathutils.geometry import intersect_ray_tri
 sys.path.insert(0,str(ROOT));import snapshot_support as sn
 need(not bpy.data.filepath,'Factory-empty Blender required');bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
 for n,items in [(plan['object'],bpy.data.objects),(plan['mesh'],bpy.data.meshes),(plan['collection'],bpy.data.collections)]:need(len(n.encode())<=63 and n not in items,'Name collision/length')
 before=sn.snap();collections_before=sn.collections_snapshot();coll=bpy.data.collections.new(plan['collection']);bpy.context.scene.collection.children.link(coll)
 operands=[];objects=[];mat=bpy.data.materials[plan['material']]
 def create(label,verts,faces,extra=None):
  name='V027 temporary '+label;need(name not in bpy.data.objects and name not in bpy.data.meshes,'Temporary name collision')
  me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  need(all(e.is_manifold for e in bm.edges)and bm.calc_volume()>0,'Operand topology');bm.to_mesh(me);bm.free();me.update();me.materials.append(mat)
  ob=bpy.data.objects.new(name,me);coll.objects.link(ob);objects.append(ob)
  operands.append({'label':label,'vertices':[list(v.co)for v in me.vertices],'faces':[list(f.vertices)for f in me.polygons],'sections':extra})
  return ob
 S=((2.04**2-.6**2)+.35**2)/.7;R=math.sqrt(S*S+.6*.6);zc=32.5-S
 def profile(y):return zc+math.sqrt(R*R-(y-(38.6 if y<=38 else 37.4))**2)
 # Seven equal sweep-angle course sectors; middle sector is an ordinary-sized key.
 theta0=math.asin(-2.04/R);theta1=math.asin(-.6/R)
 def yy(t):
  if t<=.5:return 38.6+R*math.sin(theta0+(theta1-theta0)*t*2)
  return 76-yy(1-t)
 joints=[yy(j/7)for j in range(1,7)]
 ys=sorted(set([36.56,39.44,38]+[yy(j/28)for j in range(1,28)]+[v+d for v in joints for d in[-.004,0,.004]]))
 for station in plan['stations']:
  vs=[];sections=[]
  for y in ys:
   y=min(39.44,max(36.56,y));g=max([max(0,1-abs(y-j)/.004)for j in joints]);zi=profile(y)+.006*g;zo=profile(y)+.30+.02*(1-abs(y-38)/1.44);half=.14-.004*g
   pts=[(station-half,y,zi),(station+half,y,zi),(station+.14,y,zo),(station-.14,y,zo)];vs.extend(pts);sections.append({'y':y,'intrados':zi,'extrados':zo,'groove_weight':g,'vertices':pts})
  fs=[]
  for j in range(len(ys)-1):
   for k in range(4):fs.append((4*j+k,4*j+(k+1)%4,4*(j+1)+(k+1)%4,4*(j+1)+k))
  fs.extend([(3,2,1,0),tuple(4*(len(ys)-1)+k for k in range(4))]);create('arch '+str(station),vs,fs,sections)
 for side,lo,hi in [('south',36.56,36.72),('north',39.28,39.44)]:
  vs=[(x,y,z)for x in[-2.5,3.2]for y in[lo,hi]for z in[31.98,32.22]];fs=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)];create(side+' band',vs,fs)
 o=objects[0]
 for other in objects[1:]:
  bpy.context.view_layer.objects.active=o;o.select_set(True);mod=o.modifiers.new('New-only exact join','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=other
  bpy.ops.object.modifier_apply(modifier=mod.name);othermesh=other.data;bpy.data.objects.remove(other,do_unlink=True);bpy.data.meshes.remove(othermesh)
 me=o.data;o.name=plan['object'];me.name=plan['mesh'];need(o.name==plan['object']and me.name==plan['mesh'],'Native name changed')
 # Boolean returns planar n-gons. Triangulate only new geometry for reproducible positive triangles.
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));volume=bm.calc_volume(signed=True);need(volume>0 and all(e.is_manifold for e in bm.edges),'Union not closed positive');bm.to_mesh(me);bm.free();me.update()
 for f in me.polygons:f.use_smooth=False;f.material_index=0
 me.calc_loop_triangles();tris=[tuple(t.vertices)for t in me.loop_triangles];coords=[v.co.copy()for v in me.vertices]
 need(len(tris)<=plan['triangle_budget'],'Triangle budget')
 need(all(f.area>0 for f in me.polygons),'Zero-area new face')
 need(len(set(tuple(sorted(f.vertices))for f in me.polygons))==len(me.polygons),'Duplicate faces')
 need(all(plan['bounds'][0][k]-3e-6<=v.co[k]<=plan['bounds'][1][k]+3e-6 for v in me.vertices for k in range(3)),'Envelope exceeded')
 edges=collections.defaultdict(list)
 for f in me.polygons:
  vs=list(f.vertices)
  for a,b in zip(vs,vs[1:]+vs[:1]):edges[tuple(sorted((a,b)))].append((a,b))
 need(all(len(v)==2 and v[0]==tuple(reversed(v[1]))for v in edges.values()),'Nonoriented/nonmanifold mesh')
 need(all(f.area>0 for f in me.polygons),'Zero-area saved polygon')
 du=collections.Counter(tuple(sorted(tuple(me.vertices[i].co)for i in f.vertices))for f in me.polygons);need(max(du.values())==1,'Duplicate new polygons')
 coords=[v.co.copy()for v in me.vertices];tris=[tuple(t.vertices)for t in me.loop_triangles];bvh=BVHTree.FromPolygons(coords,tris,all_triangles=True);strict=[];eps=1e-7
 for i,j in bvh.overlap(bvh):
  if i>=j or set(tris[i])&set(tris[j]):continue
  for ti,tj in[(tris[i],tris[j]),(tris[j],tris[i])]:
   a,b,c=[coords[k]for k in tj]
   for x,y in zip(ti,ti[1:]+ti[:1]):
    start,end=coords[x],coords[y];delta=end-start
    if delta.length<eps:continue
    hit=intersect_ray_tri(a,b,c,delta.normalized(),start,True)
    if hit is not None and eps<(hit-start).dot(delta.normalized())<delta.length-eps:
     normal=(b-a).cross(c-a)
     if abs(normal.normalized().dot(delta.normalized()))>eps and min((b-a).cross(hit-a).length,(c-b).cross(hit-b).length,(a-c).cross(hit-c).length)>eps:strict.append([i,j])
 if strict:
  diagnostic=out.with_name('selfcrossing_diagnostic.json');need(not diagnostic.exists(),'Diagnostic output exists');diagnostic.write_text(json.dumps({'strict_pairs':strict,'coords':[list(v)for v in coords],'triangles':tris,'operands':operands},indent=2))
 need(not strict,'Strict nonadjacent self crossing')
 after=sn.snap();after['meshes'].pop(me.name);after['objects'].pop(o.name);after['visible_evaluated'].pop(o.name)
 diff=[k for k in before if before[k]!=after[k]];need(not diff,'Original snapshot categories changed: '+str(diff))
 cs=sn.collections_snapshot();cs['collections'].pop(coll.name);cs['root_children'].remove(coll.name);need(cs==collections_before,'Original collection state changed')
 report={'status':'One unaccepted ceiling-bay prototype; independent geometry and actual inspection gate pending','source_sha256':sha(src),'source_bytes':src.stat().st_size,'builder_sha256':scriptsha,'pinned_inputs':PINNED,'owned_names':{k:plan[k]for k in ['collection','object','mesh']},'operands':operands,'vertices':[list(v.co)for v in me.vertices],'faces':[list(f.vertices)for f in me.polygons],'mesh_counts':{'vertices':len(me.vertices),'faces':len(me.polygons),'triangles':len(tris)},'positive_signed_volume':volume,'checks':{'closed_oriented':True,'no_strict_transverse_crossings':True,'source_categories_exact':list(before),'collections_exact':True},'material':{'name':mat.name,'coordinates':'Unchanged existing Geometry.Position driven brick/noise; identity object transform and world-space vertices','derived_material':False},'geometry_contract':'Three continuous backed articulated twin-curve arch operands plus two bands, cleaned by new-only EXACT union. Original ceiling and walls remain separate unchanged solids; no whole-building manifold claim.','support_proof':'Independent per-station crown and heel/lining witnesses pending','source_saved':False,'rendered':False}
 for n,h in PINNED.items():need(sha(ROOT/n)==h,'Pinned input changed before save')
 need(sha(src)==plan['source_sha256']and sha(__file__)==scriptsha,'Source/runtime changed')
 temps=[]
 try:
  def temp(dest,suffix):
   fd,n=tempfile.mkstemp(prefix='.v027-',suffix=suffix,dir=dest.parent);os.close(fd);p=Path(n);temps.append(p);return p
  model=temp(out,'.blend');model.unlink();result=bpy.ops.wm.save_as_mainfile(filepath=str(model),copy=True,compress=True,check_existing=False);need('FINISHED'in result,'Save failed')
  need(sha(src)==plan['source_sha256']and sha(__file__)==scriptsha,'Source/runtime changed after save')
  for n,h in PINNED.items():need(sha(ROOT/n)==h,'Pinned input changed after save')
  report.update(candidate_sha256=sha(model),candidate_bytes=model.stat().st_size);rp=temp(rep,'.json');rp.write_text(json.dumps(report,indent=2)+'\n');publish([(model,out),(rp,rep)]);print(json.dumps({'candidate':str(out),'sha256':report['candidate_sha256'],'counts':report['mesh_counts'],'signed_volume':volume}),flush=True)
 finally:
  for p in temps:p.unlink(missing_ok=True)
if __name__=='__main__':main()
