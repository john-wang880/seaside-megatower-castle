"""One reversible local path conformance patch; no render or source save."""
import argparse,sys,json,hashlib,collections,os,tempfile,struct,math
from pathlib import Path
SHA='99156d901f9d498b86bae4834a642d1d9110dc6e4e3a4273bca64fda17a9dfd2'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def f32(x):return struct.unpack('f',struct.pack('f',x))[0]
def main():
 if sys.flags.optimize:raise RuntimeError('Assertions must remain enabled')
 ap=argparse.ArgumentParser()
 for k in ['source','plan','output','report','source-snapshot']:ap.add_argument('--'+k,required=True)
 a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);raw=[Path(getattr(a,k))for k in ['source','plan','output','report','source_snapshot']];assert not any(p.is_symlink()for p in raw)
 src,pp,out,rp,sp=[p.resolve()for p in raw];assert len({src,pp,out,rp,sp})==5 and all(not p.exists()for p in[out,rp,sp]);assert out.suffix=='.blend'and sha(src)==SHA
 plan=json.loads(pp.read_text());assert plan['source_sha256']==SHA and plan['rows']==[95,105]and plan['selected_face_range']==[1140,1260]and plan['mask_vertex_range']==[672,735]
 here=Path(__file__).resolve().parent;files={'source':src,'plan':pp,'builder':Path(__file__).resolve(),'snapshot_helper':here/'deep_snapshot.py','overlay_helper':here/'overlay_math.py'};hashes={k:sha(p)for k,p in files.items()}
 import bpy
 from mathutils import Vector
 sys.path.insert(0,str(here));import deep_snapshot as sn
 from overlay_math import area,ccw,clip,plane
 bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False);s=bpy.context.scene;path=bpy.data.objects[plan['path_object']];terrain=bpy.data.objects[plan['terrain_object']];m=path.data
 assert len(m.vertices)==889 and len(m.polygons)==1512 and all(len(f.vertices)==3 for f in m.polygons)
 assert not path.modifiers and not path.vertex_groups and m.users==1 and not m.uv_layers and not m.shape_keys and not path.animation_data and not path.constraints and not path.parent
 assert all(path.matrix_world[i][j]==(1 if i==j else 0)for i in range(4)for j in range(4))
 assert plan['collection']not in bpy.data.collections and plan['replacement']not in bpy.data.objects and plan['replacement']not in bpy.data.meshes
 before=sn.snap();source_digest=sn.digest(before);V=[tuple(v.co)for v in m.vertices];selected=set(range(*plan['selected_face_range']));maskids=list(range(*plan['mask_vertex_range']));assert {f.index for f in m.polygons if set(f.vertices).intersection(maskids)}==selected
 assert all(not m.polygons[i].use_smooth and m.polygons[i].normal.z<0 for i in selected)
 def record(mesh,f):return(tuple(tuple(mesh.vertices[i].co)for i in f.vertices),f.material_index,f.use_smooth)
 complement=collections.Counter(record(m,f)for f in m.polygons if f.index not in selected)
 # Actual native Mask test is performed before choosing this representation.
 group=path.vertex_groups.new(name=plan['group']);group.add(maskids,1,'REPLACE');mod=path.modifiers.new(plan['modifier'],'MASK');mod.mode='VERTEX_GROUP';mod.vertex_group=group.name;mod.invert_vertex_group=True;mod.threshold=.5;mod.use_smooth=False
 coll=newobj=newmesh=None;temp=None;published=[]
 try:
  bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();eo=path.evaluated_get(dg);em=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
  try:assert len(em.polygons)==1392 and collections.Counter(record(em,f)for f in em.polygons)==complement,'Native Mask touched non-target faces'
  finally:eo.to_mesh_clear()
  coords=[V[i]for fi in selected for i in m.polygons[fi].vertices];lo=[min(v[k]for v in coords)for k in range(2)];hi=[max(v[k]for v in coords)for k in range(2)]
  eo=terrain.evaluated_get(dg);tm=eo.to_mesh();tm.calc_loop_triangles();ground=[]
  for t in tm.loop_triangles:
   vs=[tuple(terrain.matrix_world@tm.vertices[i].co)for i in t.vertices]
   if t.normal.z<=.05 or any(max(v[k]for v in vs)<lo[k]or min(v[k]for v in vs)>hi[k]for k in range(2)):continue
   ground.append({'triangle':t.index,'face':t.polygon_index,'coords':vs,'poly':ccw([(v[0],v[1])for v in vs]),'plane':plane(vs),'lo':[min(v[k]for v in vs)for k in range(2)],'hi':[max(v[k]for v in vs)for k in range(2)]})
  eo.to_mesh_clear()
  seams=[(V[row*7+j],V[row*7+j+1])for row in[95,105]for j in range(6)]
  def seam_z(xy):
   for a,b in seams:
    dx,dy=b[0]-a[0],b[1]-a[1];t=((xy[0]-a[0])*dx+(xy[1]-a[1])*dy)/(dx*dx+dy*dy);err=abs(dx*(xy[1]-a[1])-dy*(xy[0]-a[0]))/math.hypot(dx,dy)
    if -.00000001<=t<=1.00000001 and err<1e-8:return a[2]+t*(b[2]-a[2])
   return None
  vertices=[];index={};faces=[];matids=[];mapping=[];overlay=[];collapsed=[];seamrecords=[];displacements=[]
  def vertex(xy,g,oldplane):
   z=seam_z(xy);on_seam=z is not None
   if z is None:z=g['plane'][0]*xy[0]+g['plane'][1]*xy[1]+g['plane'][2]+plan['offset']
   q=tuple(f32(v)for v in[xy[0],xy[1],z]);key=q
   if key not in index:index[key]=len(vertices);vertices.append(q)
   if on_seam:seamrecords.append({'vertex':index[key],'unrounded_xy':xy,'old_interpolated_z':z,'saved_z':q[2]})
   displacements.append(q[2]-(oldplane[0]*q[0]+oldplane[1]*q[1]+oldplane[2]));return index[key]
  for fi in sorted(selected):
   f=m.polygons[fi];vs=[V[i]for i in f.vertices];poly=ccw([(v[0],v[1])for v in vs]);oldplane=plane(vs);pl=[min(v[k]for v in vs)for k in range(2)];ph=[max(v[k]for v in vs)for k in range(2)];covered=0
   for g in ground:
    if any(ph[k]<g['lo'][k]or pl[k]>g['hi'][k]for k in range(2)):continue
    inter=clip(poly,g['poly']);a=area(inter)
    if a<1e-12:continue
    covered+=a;ix=[vertex(p,g,oldplane)for p in inter]
    # Float32 can merge microscopic adjacent intersection knots. Preserve the resulting polygon boundary without zero triangles.
    unique=[]
    for i in ix:
     if not unique or i!=unique[-1]:unique.append(i)
    if len(unique)>1 and unique[0]==unique[-1]:unique.pop()
    if len(set(unique))<3:collapsed.append({'source_face':fi,'terrain_triangle':g['triangle'],'double_area':a});continue
    for j in range(1,len(unique)-1):
     tri=(unique[0],unique[j+1],unique[j]);vv=[vertices[i]for i in tri];ar=area([(v[0],v[1])for v in vv])
     if len(set(tri))<3 or ar<=1e-12:collapsed.append({'source_face':fi,'terrain_triangle':g['triangle'],'float_triangle_area':ar});continue
     # Source path winds downward; do not silently turn it into an upward solid.
     sign=(vv[1][0]-vv[0][0])*(vv[2][1]-vv[0][1])-(vv[1][1]-vv[0][1])*(vv[2][0]-vv[0][0]);assert sign<0
     gaps=[v[2]-(g['plane'][0]*v[0]+g['plane'][1]*v[1]+g['plane'][2])for v in vv];assert min(gaps)>=plan['full_face_clearance_bounds'][0]and max(gaps)<=plan['full_face_clearance_bounds'][1]
     faces.append(tri);matids.append(f.material_index);mapping.append({'new_face':len(faces)-1,'source_face':fi,'terrain_triangle':g['triangle'],'terrain_face':g['face'],'vertex_clearance':gaps,'affine_gap_min':min(gaps),'affine_gap_max':max(gaps)})
    overlay.append({'source_face':fi,'terrain_triangle':g['triangle'],'double_xy_area':a})
   assert abs(covered-area(poly))<1e-7,('Incomplete ground partition',fi,covered,area(poly))
  assert len({tuple(sorted(f))for f in faces})==len(faces),'Duplicate patch faces'
  # The fourteen original cross-seam vertices must remain bit-identical.
  assert all(V[i]in index for row in[95,105]for i in range(row*7,row*7+7))
  coll=bpy.data.collections.new(plan['collection']);s.collection.children.link(coll);newmesh=bpy.data.meshes.new(plan['replacement']);newmesh.from_pydata(vertices,[],faces)
  for mat in m.materials:newmesh.materials.append(mat)
  for f,mi in zip(newmesh.polygons,matids):f.material_index=mi;f.use_smooth=False
  newmesh.update();newobj=bpy.data.objects.new(plan['replacement'],newmesh);coll.objects.link(newobj)
  assert all(f.area>0 and f.normal.z<0 for f in newmesh.polygons)
  path.vertex_groups.remove(group);group=None;assert all(sn.mesh_snapshot(bpy.data.meshes[n])==v for n,v in before['meshes'].items());group=path.vertex_groups.new(name=plan['group']);group.add(maskids,1,'REPLACE');mod.vertex_group=group.name
  assert {x.name:sn.digest({'properties':sn.primitive(x),'nodes':sn.tree_snapshot(x.node_tree)})for x in bpy.data.materials}==before['materials'];assert {x.name:sn.digest({'properties':sn.primitive(x),'nodes':sn.tree_snapshot(x.node_tree)})for x in bpy.data.worlds}==before['worlds'];assert all(sha(p)==hashes[k]for k,p in files.items())
  receipt={'status':'UNACCEPTED local path conformance candidate','hashes':hashes,'source_semantic_digest':source_digest,'source_object':path.name,'terrain_object':terrain.name,'selected_faces':sorted(selected),'selected_mask_vertices':maskids,'collection':coll.name,'replacement':newobj.name,'patch_vertices':len(vertices),'patch_triangles':len(faces),'mapping':mapping,'overlay_polygons':overlay,'float32_collapsed_microscopic_parts':collapsed,'cross_seam_records':seamrecords,'z_displacement_range':[min(displacements),max(displacements)],'affine_clearance_range':[min(r['affine_gap_min']for r in mapping),max(r['affine_gap_max']for r in mapping)],'checks':{'native_mask_exact1392_face_complement':True,'raw_original_meshes_exact_except63_owned_weights':True,'all_materials_worlds_exact':True,'all120_source_triangles_overlay_partition_complete':True,'source14_cross_seam_vertices_bit_exact':True,'all_patch_faces_positive_area_downward_winding':True,'no_duplicate_patch_triangles':True,'affine_source_terrain_clearance_bounded':True},'limits':['Float32 intersection rounding requires independent XY domain/material/seam and manifold-boundary validation','Affine clearance to generating terrain triangle is provisional until independent overlay against all actual candidate triangles','No newroute or V009landing connection; later rows outside95→105 unchanged'],'units':plan['units']}
  for p in[out,rp,sp]:p.parent.mkdir(parents=True,exist_ok=True)
  fd,t=tempfile.mkstemp(prefix='.v023-',suffix='.blend',dir=out.parent);os.close(fd);temp=Path(t);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(temp),copy=True);assert all(sha(p)==hashes[k]for k,p in files.items());receipt.update(candidate_sha256=sha(temp),candidate_bytes=temp.stat().st_size,source_unchanged=True)
  os.link(temp,out);published.append(out)
  for p,data in[(rp,receipt),(sp,before)]:
   with p.open('x',encoding='utf-8')as f:published.append(p);json.dump(data,f,indent=2)
  temp.unlink();temp=None;published.clear();print('PATH_BUILD_PASS',receipt['candidate_sha256'],len(vertices),len(faces),receipt['affine_clearance_range'])
 except BaseException:
  if mod and mod.name in path.modifiers:path.modifiers.remove(mod)
  if group and group.name in path.vertex_groups:path.vertex_groups.remove(group)
  if newobj:bpy.data.objects.remove(newobj,do_unlink=True)
  if newmesh:bpy.data.meshes.remove(newmesh)
  if coll:bpy.data.collections.remove(coll)
  for p in published:p.unlink(missing_ok=True)
  if temp:temp.unlink(missing_ok=True)
  assert sha(src)==SHA
  raise
if __name__=='__main__':main()
