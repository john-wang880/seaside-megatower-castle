"""One bounded complete lowest-tier rib study. No renders or canonical saves."""
import argparse,sys,json,hashlib,collections,os,tempfile,math
from pathlib import Path
SHA='457348497ba7dade666a909c029f6641a0945012f264fe088b8f06513a937ae9'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 if sys.flags.optimize:raise RuntimeError('Assertions must remain enabled')
 ap=argparse.ArgumentParser()
 for k in ['source','plan','output','report','source-snapshot']:ap.add_argument('--'+k,required=True)
 a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);raw=[Path(getattr(a,k))for k in ['source','plan','output','report','source_snapshot']];assert not any(p.is_symlink()for p in raw)
 src,pp,out,rp,sp=[p.resolve()for p in raw];assert len({src,pp,out,rp,sp})==5 and all(not p.exists()for p in[out,rp,sp]);assert out.suffix=='.blend' and sha(src)==SHA
 plan=json.loads(pp.read_text());assert plan['source_sha256']==SHA;helper=Path(__file__).with_name('deep_snapshot.py');hashes={'source':SHA,'plan':sha(pp),'builder':sha(__file__),'helper':sha(helper)}
 import bpy,bmesh
 from mathutils import Vector
 sys.path.insert(0,str(helper.parent.resolve()));import deep_snapshot as sn
 bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False);o=bpy.data.objects[plan['object']];assert not o.modifiers and not o.vertex_groups and o.data.users==1 and not o.data.shape_keys and not o.animation_data and not o.constraints and not o.parent
 assert all(o.matrix_world[i][j]==(1 if i==j else 0)for i in range(4)for j in range(4))
 assert plan['collection']not in bpy.data.collections and plan['replacement']not in bpy.data.objects and plan['replacement']not in bpy.data.meshes
 component=plan['target'];ids=[v['id']for v in component['vertices']];assert ids==list(range(56,64));assert all(tuple(o.data.vertices[v['id']].co)==tuple(v['co'])for v in component['vertices'])
 for f in component['faces']:assert list(o.data.polygons[f['id']].vertices)==f['vertices']and o.data.polygons[f['id']].material_index==0
 chosen=set(ids);assert sum(set(f.vertices)<=chosen for f in o.data.polygons)==6;assert not any(chosen.intersection(f.vertices)and not set(f.vertices)<=chosen for f in o.data.polygons)
 stone=bpy.data.materials[plan['stone_material']];coremat=bpy.data.materials[plan['backing_material']];assert o.data.materials[0]==stone
 for m in[stone,coremat]:assert not any(l.from_node.bl_idname in['ShaderNodeTexCoord','ShaderNodeObjectInfo','ShaderNodeParticleInfo','ShaderNodeGroup']for l in m.node_tree.links)
 before=sn.snap();source_snapshot_sha=sn.digest(before)
 def face(m,f):return(tuple(tuple(m.vertices[i].co)for i in f.vertices),f.material_index,f.use_smooth)
 complement=collections.Counter(face(o.data,f)for f in o.data.polygons if not set(f.vertices)<=chosen)
 bottom=[tuple(v['co'])for v in component['vertices'][:4]];top=[tuple(v['co'])for v in component['vertices'][4:]];z0=sum(v[2]for v in bottom)/4;z1=sum(v[2]for v in top)/4;cx=sum(v[0]for v in bottom)/4;cy=sum(v[1]for v in bottom)/4
 def ring(z,inset=(0,0)):
  if z==z0:vs=list(bottom)
  elif z==z1:vs=list(top)
  else:
   t=(z-z0)/(z1-z0);vs=[tuple(a+(b-a)*t for a,b in zip(lo,hi))for lo,hi in zip(bottom,top)]
  return[(x+(inset[0]if x<cx else -inset[0]),y+(inset[1]if y<cy else -inset[1]),zz)for x,y,zz in vs]
 FACES=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 def winding(c,point):
  vs={v['id']:tuple(v['co'])for v in c['vertices']}
  def sub(a,b):return tuple(x-y for x,y in zip(a,b))
  def dot(a,b):return sum(x*y for x,y in zip(a,b))
  def cross(a,b):return(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
  total=0
  for f in c['faces']:
   ix=f['vertices']
   for i in range(1,len(ix)-1):
    a,b,cc=[sub(vs[j],point)for j in[ix[0],ix[i],ix[i+1]]];la,lb,lc=[dot(v,v)**.5 for v in[a,b,cc]];total+=2*math.atan2(dot(a,cross(b,cc)),la*lb*lc+dot(a,b)*lc+dot(b,cc)*la+dot(cc,a)*lb)
  return total/(4*math.pi)
 P=plan['proposal'];cuts=[P['nominal_cut_z'][0]+(P['nominal_cut_z'][1]-P['nominal_cut_z'][0])*i/P['course_count']for i in range(P['course_count']+1)];seatchecks=[]
 for z,seat in zip([cuts[0],cuts[-1]],plan['seats']):
  points=ring(z);votes=[winding(seat,p)for p in points];assert all(abs(abs(v)-1)<1e-7 for v in votes),'Endpoint cut not strictly inside actual cornice'
  seatchecks.append({'nominal_z':z,'actual_cut_corners':points,'seat_seed':seat['seed'],'solid_angle_windings':votes,'front_seat_cover_depth':min(p[1]for p in points)-seat['bounds'][0][1]})
 group=mod=coll=newobj=newmesh=None;temp=None;published=[]
 try:
  coll=bpy.data.collections.new(plan['collection']);bpy.context.scene.collection.children.link(coll);verts=[];faces=[];mats=[];parts=[]
  def add(label,lo,hi,mi,bevel=0,inset=(0,0)):
   coords=ring(lo,inset)+ring(hi,inset);bm=bmesh.new();bv=[bm.verts.new(p)for p in coords]
   for f in FACES:bm.faces.new([bv[i]for i in f])
   bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
   if bevel:bmesh.ops.bevel(bm,geom=list(bm.edges),offset=bevel,offset_type='OFFSET',segments=1,profile=.5,affect='EDGES',clamp_overlap=True)
   bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.verts.index_update();assert all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);assert volume>0
   offset=len(verts);vv=[tuple(v.co)for v in bm.verts];ff=[[offset+v.index for v in f.verts]for f in bm.faces]
   # All intended subtraction remains within original XY envelope. Source end-plane test follows for continuations.
   assert all(bottom[0][0]-1e-7<=v[0]<=bottom[1][0]+1e-7 and bottom[0][1]-1e-7<=v[1]<=bottom[2][1]+1e-7 for v in vv)
   verts.extend(vv);faces.extend(ff);mats.extend([mi]*len(ff));parts.append({'role':label,'first_vertex':offset,'vertex_count':len(vv),'first_face':len(faces)-len(ff),'face_count':len(ff),'nominal_z':[lo,hi],'volume':volume,'material_slot':mi,'bevel':bevel,'inset_xy':inset,'closed_oriented':True});bm.free()
  add('unchanged_lower_continuation',z0,cuts[0],0);add('unchanged_upper_continuation',cuts[-1],z1,0)
  add('continuous_recessed_backing',cuts[0]-P['backing_end_overlap'],cuts[-1]+P['backing_end_overlap'],1,inset=P['backing_inset_xy'])
  for i,(lo,hi)in enumerate(zip(cuts,cuts[1:])):add('course_%02d'%(i+1),lo+(P['joint_width']/2 if i else 0),hi-(P['joint_width']/2 if i<len(cuts)-2 else 0),0,P['bevel'])
  newmesh=bpy.data.meshes.new(plan['replacement']);newmesh.from_pydata(verts,[],faces);newmesh.materials.append(stone);newmesh.materials.append(coremat)
  for f,mi in zip(newmesh.polygons,mats):f.material_index=mi;f.use_smooth=False
  newmesh.update();newobj=bpy.data.objects.new(plan['replacement'],newmesh);coll.objects.link(newobj)
  # Both actual original tilted terminal faces survive exactly in new continuation vertices.
  coordset={tuple(v.co)for v in newmesh.vertices};assert all(tuple(v['co'])in coordset for v in component['vertices'])
  group=o.vertex_groups.new(name=plan['group']);group.add(ids,1,'REPLACE');mod=o.modifiers.new(plan['modifier'],'MASK');mod.mode='VERTEX_GROUP';mod.vertex_group=group.name;mod.invert_vertex_group=True;mod.threshold=.5;mod.use_smooth=False
  bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();eo=o.evaluated_get(dg);em=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
  try:assert collections.Counter(face(em,f)for f in em.polygons)==complement
  finally:eo.to_mesh_clear()
  jointchecks=[]
  for z in cuts[1:-1]:
   # Interpolated source front-center keeps original end-plane tilt in the ray height.
   rr=ring(z);zz=(rr[0][2]+rr[1][2])/2;hit,loc,n,fi=newobj.ray_cast(Vector((cx,bottom[0][1]-1,zz)),Vector((0,1,0)));assert hit and newmesh.polygons[fi].material_index==1 and abs(loc.y-(bottom[0][1]+P['backing_inset_xy'][1]))<2e-5
   jointchecks.append({'nominal_z':z,'actual_ray_height':zz,'hit':list(loc),'material_slot':1})
  o.vertex_groups.remove(group);group=None
  assert all(sn.mesh_snapshot(bpy.data.meshes[n])==v for n,v in before['meshes'].items())
  group=o.vertex_groups.new(name=plan['group']);group.add(ids,1,'REPLACE');mod.vertex_group=group.name
  aftermats={m.name:sn.digest({'properties':sn.primitive(m),'nodes':sn.tree_snapshot(m.node_tree)})for m in bpy.data.materials};assert aftermats==before['materials']
  assert {w.name:sn.digest({'properties':sn.primitive(w),'nodes':sn.tree_snapshot(w.node_tree)})for w in bpy.data.worlds}==before['worlds']
  assert sha(src)==SHA and sha(pp)==hashes['plan']and sha(__file__)==hashes['builder']and sha(helper)==hashes['helper']
  receipt={'status':'UNACCEPTED complete lowest-tier rib course study','hashes':hashes,'source_semantic_snapshot_sha256':source_snapshot_sha,'target_object':o.name,'selected_vertices':ids,'collection':coll.name,'replacement':newobj.name,'material_slots':[stone.name,coremat.name],'parts':parts,'course_nominal_exposure':(cuts[-1]-cuts[0])/13,'seat_cut_checks':seatchecks,'joint_backing_rays':jointchecks,'checks':{'source_end_corners_exact':True,'all_parts_closed_positive':True,'no_xy_enlargement':True,'all_cut_corners_inside_original_cornices':True,'all12_joint_rays_hit_existing_subdued_backing':True,'all_original_raw_meshes_exact_except_eight_owned_weights':True,'non_target_evaluated_face_records_exact':True,'all_original_materials_worlds_exact':True},'allowed_deltas':['One8-vertex owned weightgroup and invertedMask on originalribcomponent56','One replacementmesh/object andonecollection;16closedparts including13courses'],'limits':['Occupied volume intentionally reduced at18mmjoints and10mmbevels; notv021union equivalence','Independent fullstate/evaluatedattributes/windowclearance andactualartgate required','Originalseatcontact doesnot certify unexaminedneighbor contacts']}
  for p in[out,rp,sp]:p.parent.mkdir(parents=True,exist_ok=True)
  fd,t=tempfile.mkstemp(prefix='.v022-',suffix='.blend',dir=out.parent);os.close(fd);temp=Path(t);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(temp),copy=True)
  assert sha(src)==SHA and sha(pp)==hashes['plan']and sha(__file__)==hashes['builder']and sha(helper)==hashes['helper'];receipt.update(candidate_sha256=sha(temp),candidate_bytes=temp.stat().st_size,source_unchanged=True)
  os.link(temp,out);published.append(out)
  for path,data in[(rp,receipt),(sp,before)]:
   with path.open('x',encoding='utf-8')as f:published.append(path);json.dump(data,f,indent=2)
  temp.unlink();temp=None;published.clear();print('RIB_BUILD_PASS',receipt['candidate_sha256'],len(verts),len(faces))
 except BaseException:
  if mod and mod.name in o.modifiers:o.modifiers.remove(mod)
  if group and group.name in o.vertex_groups:o.vertex_groups.remove(group)
  if newobj:bpy.data.objects.remove(newobj,do_unlink=True)
  if newmesh:bpy.data.meshes.remove(newmesh)
  if coll:bpy.data.collections.remove(coll)
  for p in published:p.unlink(missing_ok=True)
  if temp:temp.unlink(missing_ok=True)
  assert sha(src)==SHA
  raise
if __name__=='__main__':main()
