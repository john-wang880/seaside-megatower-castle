import bpy,json,hashlib,collections
from pathlib import Path
from mathutils import Vector,Matrix
P=Path('work/lateral_coverage_v025');src=Path('work/v025/castle_v025.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();h=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src.resolve()),use_scripts=False);s=bpy.context.scene;cfg=json.loads((P/'views.json').read_text());c=bpy.data.objects.new('READONLY rear target probes',s.camera.data.copy());s.collection.objects.link(c);c.matrix_world=Matrix(cfg['views']['west_lateral']['reference_matrix'])
for k,v in cfg['views']['west_lateral']['camera_data'].items():setattr(c.data,k,v)
s.render.resolution_x=1200;s.render.resolution_y=866;s.render.resolution_percentage=100;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();frame=c.data.view_frame(scene=s);xmin=min(v.x/-v.z for v in frame);xmax=max(v.x/-v.z for v in frame);ymin=min(v.y/-v.z for v in frame);ymax=max(v.y/-v.z for v in frame)
def volume(o):
 for m in o.data.materials:
  if m and m.use_nodes:
   for n in m.node_tree.nodes:
    if n.type=='OUTPUT_MATERIAL'and n.is_active_output and n.inputs['Surface'].is_linked:return False
 return True
pixels=[(x,y)for y in[200,225,250,300,340,375,420,450]for x in[640,660,670,680,690,700,710]]
rays=[];targets=collections.defaultdict(set)
for x,y in pixels:
 org=c.matrix_world.translation.copy();dr=(c.matrix_world.to_3x3()@Vector((xmin+(x+.5)/1200*(xmax-xmin),ymax-(y+.5)/866*(ymax-ymin),-1))).normalized();hits=[]
 for _ in range(45):
  ok,p,n,fi,o,mat=s.ray_cast(dg,org,dr)
  if not ok:break
  if not o.hide_render and not o.hide_get()and not volume(o):hits.append({'object':o.name,'face':fi,'point':list(p),'normal':list(n),'distance':(p-c.location).length});targets[o.name].add(fi)
  if len(hits)>=4:break
  org=p+dr*.0005
 rays.append({'pixel':[x,y],'origin':list(c.location),'direction':list(dr),'hits':hits})
objects=[]
for name,fids in targets.items():
 o=bpy.data.objects[name];eo=o.evaluated_get(dg);m=eo.to_mesh();m.calc_loop_triangles();parent=list(range(len(m.vertices)))
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for e in m.edges:
  a,b=map(root,e.vertices);parent[max(a,b)]=min(a,b)
 seeds={root(m.polygons[i].vertices[0])for i in fids if i>=0 and i<len(m.polygons)};fg=collections.defaultdict(list);vg=collections.defaultdict(list)
 for f in m.polygons:
  seed=root(f.vertices[0])
  if seed in seeds:fg[seed].append(f)
 for v in m.vertices:
  seed=root(v.index)
  if seed in seeds:vg[seed].append(v.index)
 comps=[]
 for seed,ids in vg.items():
  faces=fg[seed];vs=[o.matrix_world@m.vertices[i].co for i in ids];edges=collections.Counter(tuple(sorted(e))for f in faces for e in f.edge_keys)
  comps.append({'seed':seed,'bounds':[[min(v[k]for v in vs)for k in range(3)],[max(v[k]for v in vs)for k in range(3)]],'vertex_count':len(ids),'face_count':len(faces),'edge_usage':dict(collections.Counter(edges.values())),'hit_faces':[{'face':f.index,'vertices':list(f.vertices),'coords':[list(o.matrix_world@m.vertices[i].co)for i in f.vertices],'normal':list(o.matrix_world.to_3x3()@f.normal),'material_index':f.material_index}for f in faces if f.index in fids]})
 objects.append({'object':name,'materials':[m.name if m else None for m in m.materials],'modifiers':[(x.name,x.type)for x in o.modifiers],'components':comps});eo.to_mesh_clear()
# Independently intersect every evaluated shaft triangle; retain all same-distance hits.
from mathutils.geometry import intersect_ray_tri
o=bpy.data.objects['V005 | main tower calibrated stone surface'];eo=o.evaluated_get(dg);m=eo.to_mesh();m.calc_loop_triangles();wv=[o.matrix_world@v.co for v in m.vertices];coinc=[]
for r in rays:
 dr=Vector(r['direction']);org=Vector(r['origin']);hits=[]
 for t in m.loop_triangles:
  p=intersect_ray_tri(*(wv[i]for i in t.vertices),dr,org,True)
  if p is not None and (p-org).dot(dr)>0:hits.append({'face':t.polygon_index,'distance':(p-org).length,'point':list(p),'normal':list(m.polygons[t.polygon_index].normal)})
 hits.sort(key=lambda a:a['distance']);near=[]
 if hits:
  near=[v for v in hits if abs(v['distance']-hits[0]['distance'])<.0001]
 coinc.append({'pixel':r['pixel'],'nearest_shaft_faces':near,'unique_nearest_faces':sorted(set(v['face']for v in near))})
shaft={'vertices':[list(v)for v in wv],'faces':[{'id':f.index,'vertices':list(f.vertices),'normal':list(f.normal),'material_index':f.material_index}for f in m.polygons],'raw_counts':[len(o.data.vertices),len(o.data.polygons)],'mesh_users':o.data.users,'modifiers':[(x.name,x.type)for x in o.modifiers],'vertex_groups':[g.name for g in o.vertex_groups],'materials':[x.name if x else None for x in m.materials]};eo.to_mesh_clear()
(P/'shaft_geometry.json').write_text(json.dumps(shaft,indent=2));(P/'coincident_rays.json').write_text(json.dumps(coinc,indent=2))
(P/'target_probe.json').write_text(json.dumps({'source_sha256':h,'source_unchanged':sha(src)==h,'rays':rays,'objects':objects},indent=2));print('DONE',len(rays),len(objects))
