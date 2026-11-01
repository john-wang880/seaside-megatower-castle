from pathlib import Path
p=Path(__file__).resolve().with_name('critical.py');exec(compile(p.read_text().split("print('CRITICAL GEOMETRY PASS'")[0],str(p),'exec'))
import geometry_support as gs
# Actual nonadjacent triangle self-crossings, no shared-vertex/coplanar overclaim.
folds=[]
for part_index,ids in enumerate(parts):
 ts=[tuple(t.vertices)for t in me.loop_triangles if set(t.vertices)<=set(ids)];tr=coords[np.array(ts)];lo=tr.min(1);hi=tr.max(1)
 for i in range(len(ts)):
  for j in range(i+1,len(ts)):
   if set(ts[i])&set(ts[j])or np.any(hi[i]<lo[j])or np.any(hi[j]<lo[i]):continue
   hit=False
   for t,u0 in [(tr[i],tr[j]),(tr[j],tr[i])]:
    e1=u0[1]-u0[0];e2=u0[2]-u0[0]
    for k in range(3):
     d=t[(k+1)%3]-t[k];h=np.cross(d,e2);det=e1@h
     if abs(det)<1e-18:continue
     v=t[k]-u0[0];aa=(v@h)/det;cross=np.cross(v,e1);bb=(d@cross)/det;rr=(e2@cross)/det
     if aa>1e-9 and bb>1e-9 and aa+bb<1-1e-9 and 1e-9<rr<1-1e-9:hit=True
   if hit:folds.append([part_index,i,j])
assert not folds,folds
# Exact actual new-new coplanar face patches: only opposing interfaces allowed.
same=[];opposite=[]
for i in range(16):
 for j in range(i+1,16):
  aa=ts_by[i];bb=ts_by[j]
  if np.any(aa.max((0,1))<bb.min((0,1)))or np.any(bb.max((0,1))<aa.min((0,1))):continue
  for a0 in aa:
   na=np.cross(a0[1]-a0[0],a0[2]-a0[0]);na/=np.linalg.norm(na)
   for b0 in bb:
    nb=np.cross(b0[1]-b0[0],b0[2]-b0[0]);nb/=np.linalg.norm(nb)
    if abs(na@nb)<.999999999:continue
    if max(abs((b0-a0[0])@na))>2e-6:continue
    area=gs.coplanar_triangle_area({'vertices':a0.tolist(),'triangles':[(0,1,2)]},{'vertices':b0.tolist(),'triangles':[(0,1,2)]},plane_tolerance=2e-6)['sum_area_m2']
    if area>1e-8:(same if na@nb>0 else opposite).append({'parts':[i,j],'area':area})
assert not same,same
# Practical fixed-camera rays to source-front joint inset positions; classify actual first scene hit.
cam=data['camera_preflight.json'];origin=Vector(cam['camera_location']);rayrows=[]
for normalprobe in joint:
 x,y,z=normalprobe['hit'];front=Vector((x,float(orig[:,1].min()),z));direction=(front-origin).normalized();hit,loc,n,fi,ob,matrix=bpy.context.scene.ray_cast(dg,origin,direction)
 assert hit,'Practical joint ray escaped scene'
 label='other_original_geometry'
 if ob.name==plan['replacement']:label='backing'if ob.data.polygons[fi].material_index==1 else'course_or_continuation'
 rayrows.append({'joint':normalprobe['joint'],'fraction':normalprobe['fraction'],'hit_object':ob.name,'face':fi,'classification':label,'hit':list(loc),'distance_to_hit':float((loc-origin).length),'distance_to_target_front':float((front-origin).length)})
for r in rayrows:
 if r['hit_object']==plan['object']:
  rawface=maps['FACE'][r['face']];start=o.data.polygons[rawface].vertices[0];adj0=[set()for _ in o.data.vertices]
  for e in o.data.edges:
   a,b=e.vertices;adj0[a].add(b);adj0[b].add(a)
  seen={start};todo=[start]
  while todo:
   for j in adj0[todo.pop()]:
    if j not in seen:seen.add(j);todo.append(j)
  r['original_component_seed']=min(seen);r['original_face']=rawface
# Rays are retained in the final report; no sidecar file needed.
assert all(r['hit_object']==plan['replacement'] or (r['hit_object']==plan['object'] and r['joint']==12 and r.get('original_component_seed')==288 and r['distance_to_hit']<r['distance_to_target_front']) for r in rayrows),[(r['joint'],r['fraction'],r.get('original_component_seed'))for r in rayrows if r['hit_object']!=plan['replacement']]
# Actual active non-target evaluator and repeated paired rollback.
active=snap();ar=copy.deepcopy(active['visible_evaluated']);ar.pop(plan['replacement']);ar.pop(plan['object']);br=copy.deepcopy(base['visible_evaluated']);br.pop(plan['object']);assert ar==br
for repetition in range(2):
 mod.show_viewport=mod.show_render=False;u.hide_viewport=u.hide_render=True;bpy.context.view_layer.update()
 low=snap()['visible_evaluated'];payload=low[plan['object']]['mesh']['debug_payload'];assert payload['weights']==[(i,[(0,1.)])for i in range(56,64)];payload['weights']=[];low[plan['object']]['mesh']['hash']=ss.digest(payload);assert low==base['visible_evaluated']
 mod.show_viewport=mod.show_render=True;u.hide_viewport=u.hide_render=False;bpy.context.view_layer.update()
 assert snap()['visible_evaluated']==active['visible_evaluated']
report={'pass':True,'input_sha256':hashes,'nonadjacent_self_crossings':folds,'same_facing_new_new_coplanar_patches':same,'opposite_facing_shared_interfaces':opposite,'practical_camera_joint_rays':rayrows,'ray_classifications':{s:sum(r['classification']==s for r in rayrows)for s in set(r['classification']for r in rayrows)},'active_non_target_evaluation_exact':True,'paired_rollback_twice_exact':True,'source_unchanged':sha(source)==hashes['source'],'candidate_unchanged':sha(candidate)==hashes['candidate'],'limits':['No all-angle opacity or global manifold certification','Source-neighbor occupied intersections cannot expand because every new solid lies inside original envelope and preserved terminal faces; geometric source contacts remain finite witnessed evidence','Strict nonadjacent crossings exclude shared-vertex/coplanar degeneracy cases; explicit coplanar test separately covers new-new interfaces']};report_path.write_text(json.dumps(report,indent=2));print('DEEPER PASS',report['ray_classifications'],flush=True)
