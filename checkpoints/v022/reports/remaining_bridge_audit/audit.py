import bpy,json,hashlib,collections
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
P=Path('work/remaining_bridge_piers_v021');src=Path('work/v021/castle_v021.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();h=sha(src);assert h=='457348497ba7dade666a909c029f6641a0945012f264fe088b8f06513a937ae9';bpy.ops.wm.open_mainfile(filepath=str(src.resolve()),use_scripts=False);s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();names=['V007 | western stonework with actual bridgehead passage','V012 | legacy ashlar with buried-route clearance'];objs=[]
for name in names:
 o=bpy.data.objects[name];m=o.data;adj=[[]for v in m.vertices]
 for e in m.edges:
  a,b=e.vertices;adj[a].append(b);adj[b].append(a)
 seen=set();cs=[]
 for seed in range(len(adj)):
  if seed in seen:continue
  ids=set();todo=[seed]
  while todo:
   i=todo.pop()
   if i in ids:continue
   ids.add(i);todo.extend(adj[i])
  seen.update(ids)
  if len(ids)!=8:continue
  vs=[o.matrix_world@m.vertices[i].co for i in ids];lo=[min(v[k]for v in vs)for k in range(3)];hi=[max(v[k]for v in vs)for k in range(3)]
  if not(lo[0]>-60 and hi[0]<0 and lo[1]>33 and hi[1]<43 and lo[2]<9 and hi[2]>6):continue
  faces=[f for f in m.polygons if f.vertices[0]in ids];maskselected=any(v.groups for v in[m.vertices[i]for i in ids]);cs.append({'seed':seed,'bounds':[lo,hi],'vertex_ids':sorted(ids),'vertices':[list(v)for v in vs],'face_ids':[f.index for f in faces],'materials':sorted({m.materials[f.material_index].name for f in faces}),'excluded_by_v021_owned_mask':maskselected})
 objs.append({'object':name,'components':cs})
# The raw remaining components are matched by exact evaluated coordinate/face signatures.
for rec in objs:
 o=bpy.data.objects[rec['object']];eo=o.evaluated_get(dg);em=eo.to_mesh();coords={tuple(o.matrix_world@v.co)for v in em.vertices}
 for c in rec['components']:c['all_vertices_present_in_evaluated_mesh']=all(tuple(v)in coords for v in c['vertices'])
 eo.to_mesh_clear()
# Both original hero and actual accepted bridge-close camera, not a new view.
views=[];hero=s.camera
views.append(('original_hero',hero,1200,866))
cfg=json.load(open('work/bridge_ring_feasibility_v020/camera_preflight.json'));d=hero.data.copy();cam=bpy.data.objects.new('READONLY remaining pier camera',d);s.collection.objects.link(cam);cam.matrix_world=Matrix(cfg['camera_matrix_world']);d.lens=55;d.shift_x=d.shift_y=0;views.append(('accepted_bridge_close',cam,1200,866));bpy.context.view_layer.update()
# Candidate duplicated plinth patch at the remaining interior pair nearX-22: exact plan from source, not presumed problem.
ash=objs[1]['components'];pairs=[]
for i,a in enumerate(ash):
 for b in ash[i+1:]:
  if a['excluded_by_v021_owned_mask']or b['excluded_by_v021_owned_mask']:continue
  if a['bounds'][0][1:]!=b['bounds'][0][1:]or a['bounds'][1][1:]!=b['bounds'][1][1:]:continue
  lo=[max(a['bounds'][0][k],b['bounds'][0][k])for k in range(3)];hi=[min(a['bounds'][1][k],b['bounds'][1][k])for k in range(3)]
  if all(hi[k]>lo[k]for k in range(3)):pairs.append({'seeds':[a['seed'],b['seed']],'intersection_bounds':[lo,hi],'duplicate_front_area':(hi[0]-lo[0])*(hi[2]-lo[2])})
rays=[]
regions=[]
for pair in pairs:
 lo,hi=pair['intersection_bounds'];regions.append(('remaining_plinth_duplicate',[(lo[0]+(hi[0]-lo[0])*fx,lo[1],lo[2]+(hi[2]-lo[2])*fz)for fx in[.1,.5,.9]for fz in[.1,.5,.9]]))
# West endpoint burial samples cover actual low pier/front, rather than inventing a second pier.
west=next(c for c in objs[0]['components']if c['seed']==15874);lo,hi=west['bounds'];regions.append(('west_endpoint_pier',[(lo[0]+(hi[0]-lo[0])*fx,lo[1],z)for fx in[.2,.8]for z in[8,14,20,25]]))
for vn,c,w,hh in views:
 s.render.resolution_x=w;s.render.resolution_y=hh;s.render.resolution_percentage=100
 for rn,pts in regions:
  for p in pts:
   pt=Vector(p);origin=c.matrix_world.translation.copy();dr=(pt-origin).normalized();row={'view':vn,'region':rn,'target':p,'projection':list(world_to_camera_view(s,c,pt))}
   for _ in range(150):
    ok,loc,n,f,o,m=s.ray_cast(dg,origin,dr)
    if not ok:break
    if not o.hide_render and not o.hide_get():row.update(first_object=o.name,first_face=f,hit=list(loc),target_error=(loc-pt).length);break
    origin=loc+dr*.001
   rays.append(row)
report={'source_sha256':h,'source_unchanged':sha(src)==h,'objects':objs,'remaining_plinth_coplanar_pairs':pairs,'visibility_samples':rays,'new_camera_proposed':False,'rendered':False,'model_saved':False};(P/'audit.json').write_text(json.dumps(report,indent=2));print([(o['object'],[(c['seed'],c['bounds'])for c in o['components']])for o in objs]);print('PAIRS',pairs);print('RAYS',[(r['view'],r['region'],r.get('first_object'),round(r.get('target_error',-1),3))for r in rays])
