import bpy,json,hashlib,collections
from pathlib import Path
from mathutils import Vector
P=Path('work/stair_landing_v027');src=Path('work/v027/castle_v027.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();H=sha(src)
if H!='37c0db0e67d0a0a57b7542c899f687d129a6b31208b43e03857a1f3d9e88a255':raise RuntimeError('source')
bpy.ops.wm.open_mainfile(filepath=str(src.resolve()),use_scripts=False);s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
def ray(a,b,dist):
 ok,p,n,f,o,_=s.ray_cast(dg,Vector(a),Vector(b),distance=dist)
 return {'object':o.name,'face':f,'point':list(p),'normal':list(n)}if ok else None
floor=[]
for y in[57.5,58,58.5,59,59.2,59.5,60,60.5,61,62,64,66]:
 for x in[-15,-10,-5,0,2,3.5,4.45,5.4,7,10]:floor.append({'xy':[x,y],'hit':ray((x,y,33.0),(0,0,-1),35)})
horizontal=[]
for y in[58,59.2,59.5,60,60.5]:
 for z in[32.7,33,33.5,34,34.275,35]:horizontal.append({'yz':[y,z],'west':ray((4.45,y,z),(-1,0,0),30),'east':ray((4.45,y,z),(1,0,0),15)})
# Actual visible evaluated connected components intersecting bounded terminal context.
region=[[-16,56,27],[12,66,38]];components=[];objects=[]
def overlap(a,b):return all(a[1][k]>=b[0][k]and b[1][k]>=a[0][k]for k in range(3))
for o in s.objects:
 if o.type!='MESH' or o.hide_render or o.hide_get():continue
 bb=[o.matrix_world@Vector(c)for c in o.bound_box];bounds=[[min(v[k]for v in bb)for k in range(3)],[max(v[k]for v in bb)for k in range(3)]]
 if not overlap(bounds,region):continue
 eo=o.evaluated_get(dg);me=eo.to_mesh();vs=[eo.matrix_world@v.co for v in me.vertices];parent=list(range(len(vs)))
 def find(a):
  while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
  return a
 for e in me.edges:
  a,b=map(find,e.vertices)
  if a!=b:parent[max(a,b)]=min(a,b)
 groups=collections.defaultdict(list)
 for i in range(len(vs)):groups[find(i)].append(i)
 chosen={}
 for seed,ids in groups.items():
  bound=[[min(vs[i][k]for i in ids)for k in range(3)],[max(vs[i][k]for i in ids)for k in range(3)]]
  if overlap(bound,region):chosen[seed]={'object':o.name,'seed':seed,'bounds':bound,'vertices':{str(i):list(vs[i])for i in ids},'faces':[]}
 for f in me.polygons:
  seed=find(f.vertices[0])
  if seed in chosen:chosen[seed]['faces'].append({'id':f.index,'vertices':list(f.vertices),'material_index':f.material_index,'normal':list(f.normal)})
 if chosen:objects.append({'name':o.name,'mesh':o.data.name,'mesh_users':o.data.users,'modifiers':[(m.name,m.type)for m in o.modifiers],'materials':[{'link':sl.link,'name':sl.material.name if sl.material else None}for sl in o.material_slots]});components.extend(chosen.values())
 eo.to_mesh_clear()
report={'source_sha256':H,'source_unchanged':sha(src)==H,'floor_grid':floor,'horizontal_rays':horizontal,'objects':objects,'components':components,'region':region,'units':{'system':s.unit_settings.system,'scale_length':s.unit_settings.scale_length},'scope':'Bounded visible evaluated terminal context, finite rays and actual polygons. No save/render or global accessibility/engineering proof.'};(P/'native.json').write_text(json.dumps(report,indent=2));print('DONE',len(components),len(objects))
