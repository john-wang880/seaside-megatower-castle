import bpy,bmesh,sys,json,hashlib,math,copy
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;R=P.parents[1];sys.path.insert(0,str(P));import snapshot_support as ss
from complement import complement_snapshot
source=R/'work/v021/castle_v021.blend';candidate=R/'work/v022_rib_study/candidate.blend';plan=json.loads((R/'work/v022_rib_study/plan.json').read_text());build=json.loads((R/'work/v022_rib_study/build.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();hashes={'source':sha(source),'candidate':sha(candidate)};assert hashes=={'source':'457348497ba7dade666a909c029f6641a0945012f264fe088b8f06513a937ae9','candidate':'99156d901f9d498b86bae4834a642d1d9110dc6e4e3a4273bca64fda17a9dfd2'}
def snap():
 r=ss.snap();r['collections']=ss.collections_snapshot();r['scene_custom']=dict(bpy.context.scene.items())
 for n in ['Traveler | full length ivory skirt','Traveler | purple-red shoulder cape','Traveler | white tunic']:r['visible_evaluated'][n],_=ss.render_semantic_with_ui_report(r['visible_evaluated'][n])
 return r
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);base=snap();o=bpy.data.objects[plan['object']];m=o.data;selected=set(range(56,64));original=[tuple(m.vertices[i].co)for i in range(56,64)];faces=[f for f in m.polygons if not selected.intersection(f.vertices)];assert len(m.polygons)-len(faces)==6
maps={'POINT':[v.index for v in m.vertices if v.index not in selected],'EDGE':[e.index for e in m.edges if not selected.intersection(e.vertices)],'FACE':[f.index for f in faces],'CORNER':[i for f in faces for i in f.loop_indices]};complement=complement_snapshot(m,maps)
bpy.ops.wm.open_mainfile(filepath=str(candidate),use_scripts=False);o=bpy.data.objects[plan['object']];mod=o.modifiers[0];assert len(o.modifiers)==len(o.vertex_groups)==1 and o.vertex_groups[0].name==plan['group'];assert [(v.index,[(g.group,g.weight)for g in v.groups])for v in o.data.vertices if v.groups]==[(i,[(0,1.)])for i in range(56,64)];assert mod.name==plan['modifier']and mod.type=='MASK'and mod.mode=='VERTEX_GROUP'and mod.vertex_group==plan['group']and mod.invert_vertex_group and mod.threshold==.5 and not mod.use_smooth and mod.show_viewport and mod.show_render
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();eo=o.evaluated_get(dg);em=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg);assert complement_snapshot(em,maps,True)==complement;eo.to_mesh_clear()
u=bpy.data.objects[plan['replacement']];me=u.data;assert not u.modifiers and not u.parent and not u.constraints and not u.hide_render and not u.hide_viewport and not u.hide_get();assert [list(r)for r in u.matrix_world]==[[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]];assert [x.name for x in me.materials]==[plan['stone_material'],plan['backing_material']];assert all(not f.use_smooth for f in me.polygons)
# Actual mesh connected components independently of receipt ranges.
adj=[set()for _ in me.vertices]
for e in me.edges:a,b=e.vertices;adj[a].add(b);adj[b].add(a)
unseen=set(range(len(me.vertices)));parts=[]
while unseen:
 todo=[min(unseen)];seen=set(todo);unseen-=seen
 while todo:
  for j in adj[todo.pop()]:
   if j in unseen:unseen.remove(j);seen.add(j);todo.append(j)
 parts.append(sorted(seen))
assert len(parts)==16 and len(me.vertices)==336 and len(me.polygons)==356
me.calc_loop_triangles();coords=np.array([v.co[:]for v in me.vertices],dtype=float)
def triangles(mesh,ids):return np.array([[mesh.vertices[i].co[:]for i in t.vertices]for t in mesh.loop_triangles if all(i in ids for i in t.vertices)],dtype=float)
def winding(ts,p):
 a,b,c=np.moveaxis(ts-np.asarray(p),1,0);la=np.linalg.norm(a,axis=1);lb=np.linalg.norm(b,axis=1);lc=np.linalg.norm(c,axis=1);return float(np.sum(2*np.arctan2(np.einsum('ij,ij->i',a,np.cross(b,c)),la*lb*lc+np.einsum('ij,ij->i',a,b)*lc+np.einsum('ij,ij->i',b,c)*la+np.einsum('ij,ij->i',c,a)*lb))/(4*np.pi))
rows=[];ts_by=[]
for ids,receipt in zip(parts,build['parts']):
 assert ids==list(range(receipt['first_vertex'],receipt['first_vertex']+receipt['vertex_count']))
 fs=[f for f in me.polygons if set(f.vertices)<=set(ids)];assert len(fs)==receipt['face_count'] and all(f.material_index==receipt['material_slot']for f in fs)
 bm=bmesh.new();vs={i:bm.verts.new(me.vertices[i].co)for i in ids}
 for f in fs:bm.faces.new([vs[i]for i in f.vertices])
 assert all(e.is_manifold and e.is_contiguous for e in bm.edges);volume=bm.calc_volume(signed=True);assert volume>0;bm.free();ts=triangles(me,set(ids));assert all(np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))>1e-10 for t in ts);ts_by.append(ts);rows.append({'role':receipt['role'],'vertex_count':len(ids),'face_count':len(fs),'positive_volume':volume})
# No enlargement, exact original terminal vertices and end faces, intermediate vertices safely between both source ends.
orig=np.array(original);assert np.all(coords[:,:2]>=orig[:,:2].min(axis=0)) and np.all(coords[:,:2]<=orig[:,:2].max(axis=0));assert set(original)<=set(map(tuple,coords));assert set(map(tuple,coords[parts[0]][:4]))==set(original[:4]) and set(map(tuple,coords[parts[1]][4:]))==set(original[4:])
for ids,end in [(parts[0],set(original[:4])),(parts[1],set(original[4:]))]:assert any({tuple(me.vertices[i].co)for i in f.vertices}==end for f in me.polygons if set(f.vertices)<=set(ids))
nonterminal=[v for v in coords if tuple(v)not in set(original)];assert min(v[2]for v in nonterminal)>max(v[2]for v in original[:4]) and max(v[2]for v in nonterminal)<min(v[2]for v in original[4:])
# Actual source cornice triangulation, not builder fan tessellation.
sm=o.data;sm.calc_loop_triangles();seats=[]
for pi,ringindices,sp in [(0,parts[0][4:],plan['seats'][0]),(1,parts[1][:4],plan['seats'][1])]:
 ids={v['id']for v in sp['vertices']};ts=triangles(sm,ids);votes=[winding(ts,coords[i])for i in ringindices];assert all(abs(abs(w)-1)<1e-7 for w in votes),votes;seats.append({'seed':sp['seed'],'actual_cut_corners':coords[ringindices].tolist(),'winding':votes})
core=ts_by[2];connections=[]
for i in [0,1]+list(range(3,16)):
 lower=max(coords[parts[i],2].min(),coords[parts[2],2].min());upper=min(coords[parts[i],2].max(),coords[parts[2],2].max());assert upper>lower
 point=[float(orig[:,0].mean()),float(orig[:,1].mean()),float((lower+upper)/2)];w=[winding(ts_by[i],point),winding(core,point)];assert all(abs(abs(t)-1)<1e-6 for t in w),(i,w);connections.append({'part':i,'interior_overlap_witness':point,'winding':w})
# Every joint: front-normal probes at 5 positions within actual backing width.
corecoords=coords[parts[2]];bv=BVHTree.FromPolygons([Vector(v)for v in coords],[list(t.vertices)for t in me.loop_triangles],all_triangles=True);joint=[]
for i in range(3,15):
 # Course mean nominal height with original tilt interpolated from actual central front edge.
 z=(build['parts'][i]['nominal_z'][1]+build['parts'][i+1]['nominal_z'][0])/2
 originalmean=orig[:4,2].mean();t=(z-originalmean)/(orig[4:,2].mean()-originalmean);frontz=float(((orig[0]+(orig[4]-orig[0])*t)[2]+(orig[1]+(orig[5]-orig[1])*t)[2])/2)
 for frac in [.1,.3,.5,.7,.9]:
  x=float(corecoords[:,0].min()+(corecoords[:,0].max()-corecoords[:,0].min())*frac);zz=frontz+(x-float(orig[:,0].mean()))*((orig[1,2]-orig[0,2])/(orig[1,0]-orig[0,0]));hit,normal,idx,dist=bv.ray_cast(Vector((x,float(orig[:,1].min()-1),zz)),Vector((0,1,0)));assert hit is not None and me.polygons[me.loop_triangles[idx].polygon_index].material_index==1,(i,frac,idx);joint.append({'joint':i-2,'fraction':frac,'hit':list(hit)})
print('CRITICAL GEOMETRY PASS',flush=True)
# Normalize only new owned changes and compare every persistent/evaluated source category.
o.modifiers.remove(mod);o.vertex_groups.remove(o.vertex_groups[0]);bpy.data.objects.remove(u,do_unlink=True);bpy.data.meshes.remove(me);bpy.data.collections.remove(bpy.data.collections[plan['collection']]);bpy.context.view_layer.update();after=snap();checks={k:after[k]==base[k]for k in base};diff={k:[n for n in base[k]if after[k].get(n)!=base[k][n]]for k in base if isinstance(base[k],dict)and not checks[k]};report={'pass':all(checks.values()),'input_sha256':hashes,'source_unchanged':sha(source)==hashes['source'],'candidate_unchanged':sha(candidate)==hashes['candidate'],'full_source_checks':checks,'differences':diff,'evaluated_complement_all_attributes_exact':True,'parts':rows,'seat_contacts':seats,'core_interior_overlap_witnesses':connections,'joint_normal_ray_probes':joint,'no_enlargement':True,'original_tilted_end_faces_exact':True,'limitations':['Finite geometric contacts, not structural capacity','Normal-view inset joint probes, not all grazing-angle opacity or practical-camera visual acceptance','Nonadjacent crossing/whole-neighbor/five negative/repeat gates deferred until actual visual gain warrants further work']};(P/'critical.json').write_text(json.dumps(report,indent=2));assert report['pass'],diff;print('CRITICAL FULL PASS',flush=True)
