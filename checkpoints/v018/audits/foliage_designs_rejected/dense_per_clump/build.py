"""One dense canopy experiment. No source edits, no automatic renders."""
import bpy,bmesh,json,hashlib,math,sys,collections
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('work/forest_dense_trial');src=Path('work/v018/castle_v018.blend');output=P/'dense_candidate.blend';SHA='c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(src)==SHA and not output.exists()
sys.path.insert(0,str(Path('work/navigation_v015').resolve()));from deep_snapshot import mesh_snapshot,tree_snapshot,digest
bo=bpy.data.objects['V010 | woodland boughs with gate exit clearance'];tr=bpy.data.objects['V010 | woodland trunks with gate exit clearance'];assert bo.data.users==1 and not bo.modifiers and not bo.vertex_groups
oldmesh=mesh_snapshot(bo.data);other={m.name:mesh_snapshot(m) for m in bpy.data.meshes if m!=bo.data};materials={m.name:digest(tree_snapshot(m.node_tree)) for m in bpy.data.materials};spec=json.loads((P/'source_components.json').read_text());selected=set(range(90395,90693));assert len(spec['components'])==25
C=bpy.data.collections.new('EXPERIMENT | dense foreground tree');bpy.context.scene.collection.children.link(C);allnew=[];results=[];volume_counts=[0,0,0];trunkpts=[(v.index,tr.matrix_world@v.co) for v in tr.data.vertices if 26760<=v.index<27010]
def inside(bvh,p):
 d=Vector((.827,.391,.404)).normalized();q=p.copy();n=0
 for _ in range(100):
  h,_,_,dist=bvh.ray_cast(q,d,1000)
  if h is None:break
  n+=1;q=h+d*1e-5
 return bool(n%2)
def make_bvh(vs,fs):return BVHTree.FromPolygons(vs,fs,all_triangles=False)
def volume(vs,fs):
 c=sum(vs,Vector())/len(vs);val=0
 for f in fs:
  for i in range(1,len(f)-1):val+=(vs[f[0]]-c).dot((vs[f[i]]-c).cross(vs[f[i+1]]-c))/6
 return val
for spec0 in sorted(spec['components'],key=lambda x:x['ids'][0]):
 ids=spec0['ids'];idset=set(ids);im={v:i for i,v in enumerate(ids)};ov=[bo.matrix_world@bo.data.vertices[i].co for i in ids];of=[[im[i] for i in bo.data.polygons[f].vertices] for f in spec0['faces']];bv=make_bvh(ov,of);center=sum(ov,Vector())/len(ov);assert inside(bv,center);lo=Vector(spec0['bounds'][0]);hi=Vector(spec0['bounds'][1]);h=hi.z-lo.z;rx=(hi.x-lo.x)/2;ry=(hi.y-lo.y)/2;axis=Vector((center.x+82.09366,center.y-42.23069,0));axis=axis.normalized() if axis.length>1e-4 else Vector((1,0,0));verts=[];faces=[];parts=[]
 def clip(p):
  d=p-center
  if d.length<1e-8:return p.copy()
  hit,_,_,dist=bv.ray_cast(center,d.normalized(),100)
  assert hit is not None
  return center+d.normalized()*min(d.length,dist*.999)
 # Broad lower/central masses and smaller upper shoulder, overlapping ~half their height.
 for k,(zc,rz,wide) in enumerate([(.24,.34,.98),(.49,.34,1.0),(.73,.29,.83)]):
  vv=[];ff=[];phase=(ids[0]%13)*.17+k*.22;cx=(lo.x+hi.x)/2;cy=(lo.y+hi.y)/2
  for zfrac,rad in [(-1,0),(-.57,.82),(0,1),(.57,.78),(1,0)]:
   z=lo.z+h*(zc+rz*zfrac);shift=axis*(min(rx,ry)*(.16*(-zfrac)+(.09 if k==0 else -.04)))
   if rad==0:vv.append(clip(Vector((cx+shift.x,cy+shift.y,z))));continue
   for j in range(8):
    a=phase+math.tau*j/8;notch=1-.04*(1+math.cos(a*3+k))*.5
    vv.append(clip(Vector((cx+shift.x+rx*wide*rad*math.cos(a)*notch,cy+shift.y+ry*wide*rad*math.sin(a)*notch,z))))
  # 0 lower pole, rings1..8/9..16/17..24,25 upper pole.
  for j in range(8):ff.append([0,1+(j+1)%8,1+j]);ff.append([25,17+j,17+(j+1)%8])
  for ring in range(2):
   for j in range(8):
    a=1+ring*8+j;b=1+ring*8+(j+1)%8;c=b+8;d=a+8;ff.extend([[a,b,c],[a,c,d]])
  # Closed bough masses deliberately remain substantial; no axial carrier object.
  off=len(verts);verts.extend(vv);faces.extend([[off+i for i in f] for f in ff]);parts.append((vv,ff))
 name=f'DENSE TRIAL | bough {ids[0]}';m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();mi=spec0['material_indices'];assert len(mi)==1;m.materials.append(bo.data.materials[mi[0]])
 for f in m.polygons:f.use_smooth=True
 o=bpy.data.objects.new(name,m);C.objects.link(o);allnew.append(o);bvs=[make_bvh(v,f) for v,f in parts];contacts=[(i,p) for i,p in trunkpts if all(lo[a]-1e-5<=p[a]<=hi[a]+1e-5 for a in range(3)) and inside(bv,p)];retained=[i for i,p in contacts if any(inside(b,p) for b in bvs)]
 counts=[0,0,0];sections=[]
 for iz in range(13):
  sc=[0,0,0]
  for ix in range(13):
   for iy in range(13):
    p=Vector((lo.x+(hi.x-lo.x)*(ix+.5)/13,lo.y+(hi.y-lo.y)*(iy+.5)/13,lo.z+h*(iz+.5)/13));old=inside(bv,p);new=any(inside(b,p) for b in bvs);sc[0]+=old;sc[1]+=new;sc[2]+=old and new
  sections.append({'z':lo.z+h*(iz+.5)/13,'old_occupied_samples':sc[0],'new_union_samples':sc[1],'intersection_samples':sc[2]})
  counts=[a+b for a,b in zip(counts,sc)]
 volume_counts=[a+b for a,b in zip(volume_counts,[c*(hi.x-lo.x)*(hi.y-lo.y)*h/(13**3) for c in counts])]
 edgecounts=collections.Counter(tuple(sorted(e)) for f in m.polygons for e in f.edge_keys);assert all(c==2 for c in edgecounts.values());assert all(lo[a]-1e-5<=v.co[a]<=hi[a]+1e-5 for v in m.vertices for a in range(3))
 results.append({'object':name,'source_vertex_ids':ids,'source_faces':spec0['faces'],'source_bounds':spec0['bounds'],'faces':len(m.polygons),'vertices':len(m.vertices),'material':m.materials[0].name,'source_signed_volume':spec0['signed_volume'],'closed_edges_two_faces':True,'source_carrier_inside_vertex_ids':[i for i,p in contacts],'retained_carrier_inside_vertex_ids':retained,'union_grid_counts':counts,'section_profile':sections,'new_component_volumes':[abs(volume(v,f)) for v,f in parts]})
 print('BOUGH',ids[0],'retained',len(retained),'/',len(contacts),'bulk',counts[1]/counts[0],flush=True)
report={'status':'MATH REVIEW BEFORE SAVE','source_sha256':SHA,'recipe':'three broad overlapping opaque closed lobes per old bough; lower shoulder displaced outward/downward; no thin spine or spray arms','selected_vertices':sorted(selected),'source_object':bo.name,'collection':C.name,'new_objects':results,'estimated_source_volume':volume_counts[0],'estimated_new_union_volume':volume_counts[1],'estimated_intersection_volume':volume_counts[2],'estimated_union_volume_ratio':volume_counts[1]/volume_counts[0],'sampling':'13^3 midpoint grid per old clump bbox, per-clump unions; overlaps between original clumps counted separately in both totals, not exact whole-tree union','total_new_faces':sum(len(o.data.polygons) for o in allnew),'source_unchanged':sha(src)==SHA}
(P/'design_metrics.json').write_text(json.dumps(report,indent=2));assert report['total_new_faces']<=4000
# Explicit conservative pre-render bulk/contact gate, not an artistic score.
assert report['estimated_union_volume_ratio']>=.80, 'BULK GATE FAILED: do not save/render'
assert all(r['retained_carrier_inside_vertex_ids'] for r in results if r['source_carrier_inside_vertex_ids']), 'CARRIER GATE FAILED'
def face_record(m,f):return (tuple(tuple(m.vertices[v].co) for v in f.vertices),f.material_index,f.use_smooth)
expected=collections.Counter(face_record(bo.data,f) for f in bo.data.polygons if not all(v in selected for v in f.vertices));removed=[f.index for f in bo.data.polygons if all(v in selected for v in f.vertices)];assert len(removed)==496
for f in bo.data.polygons:assert not(any(v in selected for v in f.vertices) and not all(v in selected for v in f.vertices))
vg=bo.vertex_groups.new(name='DENSE TRIAL | left tree source canopy');vg.add(sorted(selected),1,'REPLACE');mod=bo.modifiers.new('DENSE TRIAL | reversible source canopy mask','MASK');mod.vertex_group=vg.name;mod.invert_vertex_group=True;mod.threshold=.5
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();eo=bo.evaluated_get(dg);em=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg);assert collections.Counter(face_record(em,f) for f in em.polygons)==expected;eo.to_mesh_clear();bo.vertex_groups.remove(vg);assert mesh_snapshot(bo.data)==oldmesh;vg=bo.vertex_groups.new(name='DENSE TRIAL | left tree source canopy');vg.add(sorted(selected),1,'REPLACE');mod.vertex_group=vg.name
assert all(mesh_snapshot(bpy.data.meshes[n])==d for n,d in other.items());assert {m.name:digest(tree_snapshot(m.node_tree)) for m in bpy.data.materials}==materials
bpy.ops.wm.save_as_mainfile(filepath=str(output),copy=True);assert sha(src)==SHA
report.update(status='UNACCEPTED DENSE WHOLE-TREE CANDIDATE',candidate_sha256=sha(output),candidate_bytes=output.stat().st_size,group=vg.name,modifier=mod.name,checks={'other_raw_meshes_exact':True,'target_raw_mesh_except_new_weights_exact':True,'non_target_evaluated_faces_exact':True,'material_graphs_exact':True,'source_sha_unchanged':True})
(P/'build_manifest.json').write_text(json.dumps(report,indent=2));print('BUILD_PASS',flush=True)
