import bpy,json,hashlib,collections,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
P=Path('work/midground_stand_v022');src=Path('work/v022/castle_v022.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();h=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src.resolve()),use_scripts=False);s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();groups=json.load(open(P/'selected_groups.json'));fol=bpy.data.objects['V010 | woodland boughs with gate exit clearance'];objects=[]
for name in['Dense western woodland | irregular three-dimensional needle boughs','Woodland tree trunks','V010 | woodland boughs with gate exit clearance','V010 | woodland trunks with gate exit clearance']:
 o=bpy.data.objects[name];objects.append({'object':name,'mesh':o.data.name,'mesh_users':o.data.users,'raw_vertices':len(o.data.vertices),'raw_polygons':len(o.data.polygons),'hidden_render':o.hide_render,'hidden_viewport':o.hide_viewport,'instance_type':o.instance_type,'instance_collection':o.instance_collection.name if o.instance_collection else None,'modifiers':[{'name':m.name,'type':m.type,'vertex_group':getattr(m,'vertex_group',None)}for m in o.modifiers],'vertex_groups':[g.name for g in o.vertex_groups],'material_slots':[m.name for m in o.data.materials],'shape_keys':bool(o.data.shape_keys),'parent':o.parent.name if o.parent else None,'constraints':len(o.constraints),'animation':bool(o.animation_data),'matrix_world':[list(r)for r in o.matrix_world]})
for g in groups:
 lo,hi=g['foliage_vertex_range'];fs=[f for f in fol.data.polygons if all(lo<=i<hi for i in f.vertices)];assert len(fs)==g['counts'][1];assert not any(any(lo<=i<hi for i in f.vertices)and not all(lo<=i<hi for i in f.vertices)for f in fol.data.polygons);assert all(not fol.data.vertices[i].groups for i in range(lo,hi));vs=[fol.matrix_world@fol.data.vertices[i].co for i in range(lo,hi)];g['current_bounds']=[[min(v[k]for v in vs)for k in range(3)],[max(v[k]for v in vs)for k in range(3)]];assert g['current_bounds']==g['bounds'];g['materials']=dict(collections.Counter(fol.data.materials[f.material_index].name for f in fs));g['all_faces_smooth']=all(f.use_smooth for f in fs);g['height_coordinate_units']=g['bounds'][1][2]-g['bounds'][0][2];g['crown_aabb_volume_coordinate_units_cubed']=math.prod(g['bounds'][1][k]-g['bounds'][0][k]for k in range(3));g['crown_actual_occupied_union_volume']='Not measured; disconnected bough solids overlap, AABB is envelope only.';g['selected_faces']=len(fs);g['triangles']=sum(len(f.vertices)-2 for f in fs)
# World-space geometry remains intact; current originalmask targets onlydifferentv019tree.
eo=fol.evaluated_get(dg);em=eo.to_mesh();eco={tuple(v.co)for v in em.vertices}
for g in groups:g['all_selected_source_vertices_present_evaluated']=all(tuple(fol.data.vertices[i].co)in eco for i in range(*g['foliage_vertex_range']))
eo.to_mesh_clear()
views=[];acfg=json.load(open('work/exhibition_v020/polished_views.json'))['views']['A_monument'];cam=bpy.data.objects.new('READONLY A projection',s.camera.data.copy());s.collection.objects.link(cam);cam.matrix_world=Matrix(acfg['reference_matrix'])
for k,v in acfg['camera_data'].items():setattr(cam.data,k,v)
views.append(('exhibition_A',cam,(2400,2400)))
for name,loc,tgt,lens,res in[('existing_west_approach',(-99,38,32),(-79,38,26.5),38,(1200,866)),('proposed_stand_context',(-87.8,-9.6,38),(-109.5,45,34.5),48,(1200,866))]:
 c=bpy.data.objects.new('READONLY '+name,s.camera.data.copy());s.collection.objects.link(c);c.location=loc;c.rotation_euler=(Vector(tgt)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.shift_x=c.data.shift_y=0;c.data.sensor_fit='HORIZONTAL';c.data.clip_start=.05;c.data.clip_end=10000;views.append((name,c,res))
bpy.context.view_layer.update();projections=[];rays=[]
for name,c,res in views:
 s.render.resolution_x,s.render.resolution_y=res;s.render.resolution_percentage=100
 for g in groups:
  vv=[fol.matrix_world@fol.data.vertices[i].co for i in range(*g['foliage_vertex_range'])];pr=[world_to_camera_view(s,c,v)for v in vv];mins=[min(p[k]for p in pr)for k in range(3)];maxs=[max(p[k]for p in pr)for k in range(3)];projections.append({'view':name,'trunk_seed':g['trunk_seed'],'ndc_bounds':[mins,maxs],'pixel_envelope_size':[(maxs[0]-mins[0])*res[0],(maxs[1]-mins[1])*res[1]],'camera_distance_to_crown_center':(sum(vv,Vector())/len(vv)-c.location).length,'all_in_front':mins[2]>0,'all_vertices_inside_frame':mins[0]>=0 and maxs[0]<=1 and mins[1]>=0 and maxs[1]<=1 and mins[2]>0})
  if name!='existing_west_approach':
   lo,hi=g['bounds'];pts=[(g['trunk_xy'][0],g['trunk_xy'][1],lo[2]+(hi[2]-lo[2])*f)for f in[.25,.55,.85]]
   for pt in pts:
    pt=Vector(pt);origin=c.location.copy();dr=(pt-origin).normalized();row={'view':name,'trunk_seed':g['trunk_seed'],'target':list(pt)}
    for _ in range(100):
     ok,loc,n,fi,o,m=s.ray_cast(dg,origin,dr)
     if not ok:break
     if not o.hide_render and not o.hide_get():row.update(first_object=o.name,hit=list(loc),first_face=fi,target_distance_error=(loc-pt).length);break
     origin=loc+dr*.001
    rays.append(row)
 if name=='proposed_stand_context':
  bounds=[[-117,32,26],[-101,54,42]];pr=[list(world_to_camera_view(s,c,Vector((x,y,z))))for x in[bounds[0][0],bounds[1][0]]for y in[bounds[0][1],bounds[1][1]]for z in[bounds[0][2],bounds[1][2]]];margin=min(min(q[0],q[1],1-q[0],1-q[1])for q in pr);camera={'location':list(c.location),'target':[-109.5,45,34.5],'matrix_world':[list(r)for r in c.matrix_world],'rotation_euler':list(c.rotation_euler),'lens':c.data.lens,'sensor_width':c.data.sensor_width,'sensor_height':c.data.sensor_height,'sensor_fit':c.data.sensor_fit,'shift_x':0,'shift_y':0,'clip_start':c.data.clip_start,'clip_end':c.data.clip_end,'resolution':list(res),'target_bounds':bounds,'bounds_projection':pr,'minimum_frame_margin':margin}
pathobj=next(o for o in s.objects if o.name.startswith('Narrow winding limestone footpath'))
pv=[pathobj.matrix_world@v.co for v in pathobj.data.vertices if -117<= (pathobj.matrix_world@v.co).x <=-101 and 32<=(pathobj.matrix_world@v.co).y<=54]
pathreport={'object':pathobj.name,'selected_vertex_bounds':[[min(v[k]for v in pv)for k in range(3)],[max(v[k]for v in pv)for k in range(3)]],'selection':'Only path mesh vertices within worldX−117…−101,Y32…54; not an exact cropped-path footprint or certifiedclearance.'}
tree=BVHTree.FromObject(pathobj,dg);near=[]
for g in groups:
 pt=Vector((*g['trunk_xy'],g['trunk_bounds'][0][2]));loc,n,face,dist=tree.find_nearest(pathobj.matrix_world.inverted()@pt);world=pathobj.matrix_world@loc
 near.append({'trunk_seed':g['trunk_seed'],'trunk_root_reference':list(pt),'nearest_actual_path_surface':list(world),'distance_coordinate_units':(pt-world).length,'path_face':face})
pathreport['nearest_trunk_root_samples']=near
assert margin>.04,margin
report={'path_context':pathreport,'source_sha256' :h,'source_bytes':src.stat().st_size,'source_unchanged':sha(src)==h,'scene_units':{'system':s.unit_settings.system,'scale_length':s.unit_settings.scale_length,'length_unit':s.unit_settings.length_unit,'interpretation':'Coordinate units; scene settings do not establish globally calibrated real-world metres.'},'objects':objects,'groups':groups,'projections':projections,'finite_visibility_rays':rays,'proposed_camera':camera,'rendered':False,'saved':False};(P/'inventory.json').write_text(json.dumps(report,indent=2));print('CAMERA_MARGIN',margin,'UNITS',report['scene_units']);print('PROJECTIONS',projections)
