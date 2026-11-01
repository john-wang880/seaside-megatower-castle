import bpy,json,hashlib,collections
from pathlib import Path
from mathutils import Vector,Matrix
P=Path('work/remaining_returns_v024');src=Path('work/v024/castle_v024.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();h=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src.resolve()),use_scripts=False);s=bpy.context.scene;cfg=json.loads(Path('work/rear_landward_v023/views.json').read_text());c=bpy.data.objects.new('READONLY rear target probes',s.camera.data.copy());s.collection.objects.link(c);c.matrix_world=Matrix(cfg['views']['rear_landward']['reference_matrix'])
for k,v in cfg['views']['rear_landward']['camera_data'].items():setattr(c.data,k,v)
s.render.resolution_x=1200;s.render.resolution_y=866;s.render.resolution_percentage=100;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();frame=c.data.view_frame(scene=s);xmin=min(v.x/-v.z for v in frame);xmax=max(v.x/-v.z for v in frame);ymin=min(v.y/-v.z for v in frame);ymax=max(v.y/-v.z for v in frame)
def volume(o):
 for m in o.data.materials:
  if m and m.use_nodes:
   for n in m.node_tree.nodes:
    if n.type=='OUTPUT_MATERIAL'and n.is_active_output and n.inputs['Surface'].is_linked:return False
 return True

import sys
sys.path.insert(0,str(P.resolve()));from overlay import area,clip
name='V008 | gallery with genuine eastern approach portal';o=bpy.data.objects[name];eo=o.evaluated_get(dg);m=eo.to_mesh();parent=list(range(len(m.vertices)))
def root(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
for e in m.edges:
 a,b=map(root,e.vertices);parent[max(a,b)]=min(a,b)
F=[]
for f in m.polygons:
 if f.normal.y<.99999:continue
 vs=[o.matrix_world@m.vertices[i].co for i in f.vertices];lo=[min(v[k]for v in vs)for k in range(3)];hi=[max(v[k]for v in vs)for k in range(3)]
 if abs(vs[0].y-65.5)<.001:continue
 if not(lo[0]<35 and hi[0]>-15 and 52<=lo[1]<=67 and lo[2]<90 and hi[2]>35):continue
 F.append({'id':f.index,'seed':root(f.vertices[0]),'coords':[list(v)for v in vs],'y':vs[0].y,'poly':[(v.x,v.z)for v in vs],'bounds':[lo,hi],'material_index':f.material_index})
def cast(q):
 origin=c.location.copy();dr=(q-origin).normalized()
 for _ in range(40):
  ok,loc,n,fi,ob,mat=s.ray_cast(dg,origin,dr)
  if not ok:return None
  if not ob.hide_render and not ob.hide_get()and not volume(ob):return {'object':ob.name,'face':fi,'point':list(loc),'distance_to_overlay_centroid':(loc-q).length}
  origin=loc+dr*.0005
from bpy_extras.object_utils import world_to_camera_view
import itertools,math
assert h=='89f9f6a8a57103d99100935b96624469ddf1fd52b9703e0d9177a352e735c856'
pairs=[]
for i,a in enumerate(F):
 for b in F[i+1:]:
  if a['seed']==b['seed']or abs(a['y']-b['y'])>1e-6:continue
  poly=clip(a['poly'],b['poly']);ar=area(poly)
  if ar<1e-8:continue
  q=Vector((sum(v[0]for v in poly)/len(poly),a['y'],sum(v[1]for v in poly)/len(poly)));hit=cast(q);pairs.append({'faces':[a['id'],b['id']],'components':[a['seed'],b['seed']],'y':a['y'],'area':ar,'xz':poly,'centroid_first_hit':hit,'centroid_exposed':bool(hit and hit['object']==name and hit['distance_to_overlay_centroid']<.003)})
def inside(q,poly):
 sign=sum(a[0]*b[1]-a[1]*b[0]for a,b in zip(poly,poly[1:]+poly[:1]));poly=poly if sign>0 else poly[::-1]
 return all((b[0]-a[0])*(q[1]-a[1])-(b[1]-a[1])*(q[0]-a[0])>=-1e-8 for a,b in zip(poly,poly[1:]+poly[:1]))
def plane_point(px,py,y):
 dr=(c.matrix_world.to_3x3()@Vector((xmin+px/1200*(xmax-xmin),ymax-py/866*(ymax-ymin),-1))).normalized();return c.location+((y-c.location.y)/dr.y)*dr
rank=[]
for y in sorted({p['y']for p in pairs}):
 pp=[p for p in pairs if p['y']==y];polys=[p['xz']for p in pp];union=0
 for count in range(1,len(polys)+1):
  for combination in itertools.combinations(polys,count):
   poly=combination[0]
   for q in combination[1:]:poly=clip(poly,q)
   union+=(-1)**(count+1)*area(poly)
 proj=[world_to_camera_view(s,c,Vector((q[0],y,q[1])))for p in polys for q in p];bb=[[min(v.x for v in proj)*1200,max(v.x for v in proj)*1200],[(1-max(v.y for v in proj))*866,(1-min(v.y for v in proj))*866]]
 visible=[];blocked=collections.Counter();total=0;estimated_visible_area=0
 for py in range(max(0,math.floor(bb[1][0])),min(866,math.ceil(bb[1][1]))):
  for px in range(max(0,math.floor(bb[0][0])),min(1200,math.ceil(bb[0][1]))):
   q=plane_point(px+.5,py+.5,y)
   if not any(inside((q.x,q.z),p)for p in polys):continue
   total+=1;hit=cast(q)
   if hit and hit['object']==name and hit['distance_to_overlay_centroid']<.003:
    visible.append([px,py]);corners=[plane_point(x,z,y)for x,z in[(px,py),(px+1,py),(px+1,py+1),(px,py+1)]];estimated_visible_area+=area([(p.x,p.z)for p in corners])
   else:blocked[hit['object']if hit else 'no hit']+=1
 rank.append({'plane_y':y,'pair_count':len(pp),'pair_centroids_exposed':sum(p['centroid_exposed']for p in pp),'duplicate_union_plane_area':union,'projected_duplicate_bounds_px':bb,'duplicate_pixel_centers':total,'visible_pixel_centers':len(visible),'visible_pixel_bounds':[[min(p[k]for p in visible),max(p[k]for p in visible)]for k in range(2)]if visible else None,'pixel_quadrature_visible_area_estimate':estimated_visible_area,'blockers':dict(blocked),'visible_pixels':visible})
# Raw/evaluated component association by exact bounding extrema, then explicit vertex IDs.
raw=o.data;rp=list(range(len(raw.vertices)))
def rr(i):
 while rp[i]!=i:rp[i]=rp[rp[i]];i=rp[i]
 return i
for e in raw.edges:
 a,b=map(rr,e.vertices);rp[max(a,b)]=min(a,b)
rg=collections.defaultdict(list)
for v in raw.vertices:rg[rr(v.index)].append(v.index)
rawgroups=[]
for seed,ids in rg.items():
 vs=[o.matrix_world@raw.vertices[i].co for i in ids];rawgroups.append({'seed':seed,'ids':ids,'bounds':[[min(v[k]for v in vs)for k in range(3)],[max(v[k]for v in vs)for k in range(3)]]})
mapping=[]
for seed in sorted({q for p in pairs for q in p['components']}):
 ids=[v.index for v in m.vertices if root(v.index)==seed];vs=[o.matrix_world@m.vertices[i].co for i in ids];bb=[[min(v[k]for v in vs)for k in range(3)],[max(v[k]for v in vs)for k in range(3)]];matches=[r for r in rawgroups if max(abs(bb[j][k]-r['bounds'][j][k])for j in range(2)for k in range(3))<.00003];assert len(matches)==1;mapping.append({'evaluated_seed':seed,'evaluated_vertex_ids':ids,'raw':matches[0],'bounds':bb})
state={'mesh_users':raw.users,'raw_counts':[len(raw.vertices),len(raw.polygons)],'evaluated_counts':[len(m.vertices),len(m.polygons)],'modifiers':[{'name':md.name,'type':md.type,'show_viewport':md.show_viewport,'show_render':md.show_render,'mode':getattr(md,'mode',None),'group':getattr(md,'vertex_group',None),'invert':getattr(md,'invert_vertex_group',None),'width':getattr(md,'width',None)}for md in o.modifiers],'groups':[{'name':g.name,'index':g.index,'weights':[[v.index,w.weight]for v in raw.vertices for w in v.groups if w.group==g.index]}for g in o.vertex_groups],'attributes':[(a.name,a.data_type,a.domain)for a in raw.attributes],'materials':[x.name if x else None for x in raw.materials],'uv_layers':[x.name for x in raw.uv_layers]}
eo.to_mesh_clear();(P/'survey.json').write_text(json.dumps({'source_sha256':h,'source_unchanged':sha(src)==h,'input_state':state,'mapping':mapping,'overlaps':pairs,'ranking':sorted(rank,key=lambda r:-r['visible_pixel_centers']),'limits':['Actual evaluated same-facing planar polygons; exact double-precision union area by inclusion-exclusion.','Visibility is finite actual-camera pixel-center rays, not exact occluded polygon area. Pixel-quadrature area is an estimate, not a full geometric visibility proof.','Existing V024 Mask and union preserved; no render/save/camera change in canonical file.']},indent=2));print('DONE',[(r['plane_y'],r['visible_pixel_centers'],r['duplicate_union_plane_area'])for r in rank])
