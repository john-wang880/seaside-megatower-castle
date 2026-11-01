import bpy,json,hashlib,bisect
from pathlib import Path
from mathutils import Vector,Matrix
P=Path('work/midground_stand_v022');src=Path('work/v022/castle_v022.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();h=sha(src);assert h=='99156d901f9d498b86bae4834a642d1d9110dc6e4e3a4273bca64fda17a9dfd2';bpy.ops.wm.open_mainfile(filepath=str(src.resolve()),use_scripts=False);s=bpy.context.scene;cfg=json.load(open('work/exhibition_v020/polished_views.json'))['views']['A_monument'];cam=bpy.data.objects.new('READONLY A locator',s.camera.data.copy());s.collection.objects.link(cam);cam.matrix_world=Matrix(cfg['reference_matrix']);d=cam.data
for k,v in cfg['camera_data'].items():setattr(d,k,v)
s.render.resolution_x=s.render.resolution_y=2400;s.render.resolution_percentage=100;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();frame=d.view_frame(scene=s);xmin=min(v.x/-v.z for v in frame);xmax=max(v.x/-v.z for v in frame);ymin=min(v.y/-v.z for v in frame);ymax=max(v.y/-v.z for v in frame);o=bpy.data.objects['V010 | woodland boughs with gate exit clearance'];lookup={tuple(v.co):v.index for v in o.data.vertices};old=json.load(open('work/forest_v018_audit/visible_components.json'))[o.name];old=sorted(old,key=lambda c:c['seed']);seeds=[c['seed']for c in old];rows=[]
for x in[730,765,800,835]:
 for y in[1335,1360,1385,1410]:
  org=cam.location.copy();dr=(cam.matrix_world.to_3x3()@Vector((xmin+(x+.5)/2400*(xmax-xmin),ymax-(y+.5)/2400*(ymax-ymin),-1))).normalized();r={'pixel':[x,y]}
  for _ in range(150):
   ok,loc,n,face,obj,m=s.ray_cast(dg,org,dr)
   if not ok:break
   if not obj.hide_render and not obj.hide_get():
    r.update(object=obj.name,location=list(loc),face=face)
    if obj==o:
     eo=o.evaluated_get(dg);em=eo.to_mesh();poly=em.polygons[face];ids=[lookup[tuple(em.vertices[i].co)]for i in poly.vertices];r['source_vertex_ids']=ids;r['component_seed']=old[bisect.bisect_right(seeds,min(ids))-1]['seed'];eo.to_mesh_clear()
    break
   org=loc+dr*.001
  rows.append(r)
(P/'locator.json').write_text(json.dumps({'source_sha256':h,'source_unchanged':sha(src)==h,'camera_reference':cfg,'rays':rows},indent=2));print(rows)
