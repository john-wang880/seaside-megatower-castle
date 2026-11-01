import bpy,json,hashlib,collections
from pathlib import Path
from mathutils import Vector,Matrix
P=Path('work/path_arrival_v022');src=Path('work/v022/castle_v022.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();h=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src.resolve()),use_scripts=False);s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();o=next(o for o in s.objects if o.name.startswith('Narrow winding limestone footpath'));m=o.data
obj={'object':o.name,'matrix_world':[list(r)for r in o.matrix_world],'mesh_users':m.users,'modifiers':[{'name':x.name,'type':x.type}for x in o.modifiers],'materials':[x.name for x in m.materials],'vertices':[list(o.matrix_world@v.co)for v in m.vertices],'faces':[{'id':f.index,'vertices':list(f.vertices),'material_index':f.material_index,'normal':list(f.normal)}for f in m.polygons]};edges=collections.Counter(tuple(sorted(e))for f in m.polygons for e in f.edge_keys);obj['boundary_edges']=[list(e)for e,c in edges.items()if c==1];obj['nonmanifold_edge_uses']=[(list(e),n)for e,n in edges.items()if n>2]
views=[];cfg=json.load(open('work/midground_stand_v022/camera_proposal.json'));c=bpy.data.objects.new('READONLY stand path locator',s.camera.data.copy());s.collection.objects.link(c);c.matrix_world=Matrix(cfg['camera_matrix_world'])
for k,v in cfg['camera_data'].items():setattr(c.data,k,v)
views.append(('stand',c,[(x,y)for x in[730,760,790,820]for y in[490,515,540,580,620,640]]))
c=bpy.data.objects.new('READONLY approach path locator',s.camera.data.copy());s.collection.objects.link(c);c.location=(-99,38,32);c.rotation_euler=(Vector((-79,38,26.5))-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=38;c.data.shift_x=c.data.shift_y=0;c.data.sensor_fit='HORIZONTAL';views.append(('approach',c,[(x,y)for x in[400,600,800]for y in[600,720,820]]));s.render.resolution_x=1200;s.render.resolution_y=866;s.render.resolution_percentage=100;bpy.context.view_layer.update();rays=[]
for name,c,pixels in views:
 frame=c.data.view_frame(scene=s);xmin=min(v.x/-v.z for v in frame);xmax=max(v.x/-v.z for v in frame);ymin=min(v.y/-v.z for v in frame);ymax=max(v.y/-v.z for v in frame)
 for x,y in pixels:
  origin=c.location.copy();dr=(c.matrix_world.to_3x3()@Vector((xmin+(x+.5)/1200*(xmax-xmin),ymax-(y+.5)/866*(ymax-ymin),-1))).normalized();hits=[]
  for _ in range(40):
   ok,loc,n,fi,ob,mat=s.ray_cast(dg,origin,dr)
   if not ok:break
   if not ob.hide_render and not ob.hide_get():hits.append({'object':ob.name,'face':fi,'location':list(loc),'normal':list(n)})
   if len(hits)>=3:break
   origin=loc+dr*.001
  rays.append({'view':name,'pixel':[x,y],'hits':hits})
near=[]
for ob in s.objects:
 if ob.type=='MESH'and not ob.hide_render and not ob.hide_get()and('V009'in ob.name or'landing'in ob.name.lower()or'apron'in ob.name.lower()):
  vs=[ob.matrix_world@Vector(v)for v in ob.bound_box];near.append({'object':ob.name,'bounds':[[min(v[k]for v in vs)for k in range(3)],[max(v[k]for v in vs)for k in range(3)]]})
(P/'survey.json').write_text(json.dumps({'source_sha256':h,'source_unchanged':sha(src)==h,'scene_units':{'system':s.unit_settings.system,'scale_length':s.unit_settings.scale_length,'length_unit':s.unit_settings.length_unit},'path':obj,'rays':rays,'route_objects':near},indent=2));print('PATH',len(m.vertices),len(m.polygons),'BOUNDS',obj['vertices'][:5],obj['vertices'][-5:]);print('RAYS',[(r['view'],r['pixel'],[(q['object'],q['location'])for q in r['hits'][:1]])for r in rays])
