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

PINNED={'plan.json':'aee91740c53c3486759856c4b9b92f70943030f8d6bded7f4f43c07997ebc33e','profiles.json':'03228eb24bc54b06ef2ff7d59907321ff8fca3e5204c9e7ab0208bae28b2c6b3','envelope.json':'4d1429dfe94ad75c7d39652a1ed3a39caf46be49f53dc4324b92acb03b7d5960','snapshot_support.py':'ef8b575c70fbb394bfd76cba93b97bc07a6c03abdfe7f4eb2752cfd236be6249'}
def main():
 need(not sys.flags.optimize,'Optimized Python refused');ap=argparse.ArgumentParser()
 for k in ['source','output','report']:ap.add_argument('--'+k,required=True)
 a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);src=safe(a.source,True);out=safe(a.output);rep=safe(a.report);need(len({src,out,rep})==3 and out.suffix=='.blend'and rep.suffix=='.json','Output roles/aliases invalid')
 for n,h in PINNED.items():need(sha(ROOT/n)==h,'Pinned input changed: '+n)
 plan=json.loads((ROOT/'plan.json').read_text());need(src.stat().st_size==plan['source_bytes']and sha(src)==plan['source_sha256'],'Source mismatch');scriptsha=sha(__file__)
 import bpy,bmesh
 from mathutils import Vector,Matrix
 from mathutils.bvhtree import BVHTree
 from mathutils.geometry import intersect_ray_tri
 sys.path.insert(0,str(ROOT));import snapshot_support as sn
 need(not bpy.data.filepath,'Factory-empty Blender required');bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
 cliff=bpy.data.objects[plan['source_cliff']];need(cliff.matrix_world==Matrix.Identity(4)and not cliff.modifiers,'Unexpected source cliff transform/modifiers')
 for n,items in [(plan['object'],bpy.data.objects),(plan['mesh'],bpy.data.meshes),(plan['collection'],bpy.data.collections)]:need(len(n.encode())<=63 and n not in items,'Owned name collision/length')
 profiles={p['boundary_order_index']:p for p in json.loads((ROOT/'profiles.json').read_text())['profiles']};radials={p['order']:p['radial']for p in json.loads((ROOT/'envelope.json').read_text())['samples']}
 for s in plan['sections']:
  p=profiles[s['order']]
  need(all(list(cliff.data.vertices[i].co)==co for i,co in zip(p['vertex_ids'],p['coords'])),'Profile does not match actual source')
 before=sn.snap();collections_before=sn.collections_snapshot();verts=[];sections=[];N=7
 def at_height(profile,z):
  cs=profile['coords']
  for p,q in zip(cs,cs[1:]):
   if p[2]>=z>=q[2]:
    t=(z-p[2])/(q[2]-p[2]);return[p[k]+t*(q[k]-p[k])for k in range(3)]
  raise RuntimeError('Height outside actual source profile')
 for s in plan['sections']:
  profile=profiles[s['order']];rad=radials[s['order']];crest=s['crest_z'];w=s['width'];need(crest+1<profile['coords'][0][2]*.65,'Shoulder exceeds local65percent rim')
  offsets=[(plan['back_inset'],plan['bottom_z']),(plan['back_inset'],crest+1),(.22*w,crest),(.67*w,crest*.67),(w,3.1),(.94*w,-.65),(.55*w,plan['bottom_z'])]
  pts=[]
  for d,z in offsets:
   p=at_height(profile,z);p=[p[0]+rad[0]*d,p[1]+rad[1]*d,z];need(all(plan['bounds'][0][k]<=p[k]<=plan['bounds'][1][k]for k in range(3)),'Vertex exceeds reviewed outer envelope');pts.append(p);verts.append(p)
  sections.append({'order':s['order'],'profile':profile,'radial':rad,'cross_section_offsets_dz':offsets,'actual_vertices':pts,'buried_taper':s['order']in[191,198]})
 faces=[]
 for j in range(len(sections)-1):
  for k in range(N):
   a=j*N+k;b=j*N+(k+1)%N;c=(j+1)*N+(k+1)%N;d=(j+1)*N+k
   # Alternating diagonals, continuous large angular face breaks, no shelf layers.
   faces.extend([(a,b,c),(a,c,d)]if(j+k)%2==0 else[(a,b,d),(b,c,d)])
 faces.append(tuple(reversed(range(N))));faces.append(tuple((len(sections)-1)*N+k for k in range(N)))
 me=bpy.data.meshes.new(plan['mesh']);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 volume=bm.calc_volume(signed=True)
 if volume<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces));volume=bm.calc_volume(signed=True)
 need(volume>0 and all(e.is_manifold for e in bm.edges),'New asset not closed/positive');bm.to_mesh(me);bm.free();me.update()
 coll=bpy.data.collections.new(plan['collection']);bpy.context.scene.collection.children.link(coll);o=bpy.data.objects.new(plan['object'],me);coll.objects.link(o)
 need(o.name==plan['object']and me.name==plan['mesh']and coll.name==plan['collection'],'Native owned names changed')
 for n in plan['materials']:me.materials.append(bpy.data.materials[n])
 for f in me.polygons:f.use_smooth=False;f.material_index=int(sum(me.vertices[i].co.z for i in f.vertices)/len(f.vertices)<plan['wet_face_center_z_below'])
 me.calc_loop_triangles();need(len(me.loop_triangles)<=plan['triangle_budget'],'Triangle budget exceeded')
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
  diagnostic=out.with_name('selfcrossing_diagnostic.json');need(not diagnostic.exists(),'Diagnostic output exists');diagnostic.write_text(json.dumps({'strict_pairs':strict,'coords':[list(v)for v in coords],'triangles':tris,'sections':sections},indent=2))
 need(not strict,'Strict nonadjacent self crossing')
 after=sn.snap();after['meshes'].pop(me.name);after['objects'].pop(o.name);after['visible_evaluated'].pop(o.name)
 diff=[k for k in before if before[k]!=after[k]];need(not diff,'Original snapshot categories changed: '+str(diff))
 cs=sn.collections_snapshot();cs['collections'].pop(coll.name);cs['root_children'].remove(coll.name);need(cs==collections_before,'Original collection state changed')
 # Actual saved triangle export enables independent continuous solid/contact proof.
 report={'status':'Unaccepted macroform prototype; independent attachment/water/coplanar/visual gates pending','source_sha256':sha(src),'source_bytes':src.stat().st_size,'builder_sha256':scriptsha,'pinned_inputs':PINNED,'owned_names':{k:plan[k]for k in ['collection','object','mesh']},'vertices':[list(v.co)for v in me.vertices],'faces':[list(f.vertices)for f in me.polygons],'material_indices':[f.material_index for f in me.polygons],'sections':sections,'mesh_counts':{'vertices':len(me.vertices),'faces':len(me.polygons),'triangles':len(tris)},'positive_signed_volume':volume,'checks':{'closed_oriented':True,'no_zero_area_saved_polygons':True,'no_exact_duplicate_polygons':True,'no_strict_transverse_selfcrossings':True,'original_snapshot_categories_exact':list(before),'original_collections_exact':True,'all_vertices_within_outer_envelope':True},'geometry_contract':'One closed added asset intersects intact cliff; combined occupied union, not a globally welded/manifold terrain claim','attachment_and_water':'Independent actual geometry verification still required; radial profile inset is construction intention, not final proof','source_saved':False,'rendered':False}
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
