import bpy,json,hashlib,collections
from pathlib import Path
from mathutils import Vector
P=Path('work/west_lower_tier_v021');src=Path('work/v021/castle_v021.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();h=sha(src);assert h=='457348497ba7dade666a909c029f6641a0945012f264fe088b8f06513a937ae9';bpy.ops.wm.open_mainfile(filepath=str(src.resolve()),use_scripts=False);dg=bpy.context.evaluated_depsgraph_get();out=[];used=set()
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render or o.hide_get():continue
 if not any(s in o.name.lower() for s in ['west']):continue
 eo=o.evaluated_get(dg);m=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg);parent=list(range(len(m.vertices)))
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for e in m.edges:
  a,b=map(root,e.vertices);parent[max(a,b)]=min(a,b)
 groups=collections.defaultdict(list)
 for v in m.vertices:groups[root(v.index)].append(v.index)
 comps=[]
 for seed,ids in groups.items():
  vs=[o.matrix_world@m.vertices[i].co for i in ids];lo=[min(v[k]for v in vs)for k in range(3)];hi=[max(v[k]for v in vs)for k in range(3)]
  if not(lo[0]<-118 and hi[0]>-148 and lo[1]<91 and hi[1]>81 and lo[2]<110 and hi[2]>74):continue
  faces=[f for f in m.polygons if root(f.vertices[0])==seed];selected=[f for f in faces if (o.matrix_world.to_3x3()@f.normal).y<-.8]
  comps.append({'seed':seed,'bounds':[lo,hi],'vertex_count':len(ids),'face_count':len(faces),'south_faces':[{'id':f.index,'vertices':list(f.vertices),'coords':[list(o.matrix_world@m.vertices[i].co)for i in f.vertices],'normal':list(o.matrix_world.to_3x3()@f.normal),'material_index':f.material_index}for f in selected],'vertices':[{'id':i,'co':list(o.matrix_world@m.vertices[i].co)}for i in ids], 'faces':[{'id':f.index,'vertices':list(f.vertices),'material_index':f.material_index}for f in faces], 'material_indices':sorted({f.material_index for f in faces})})
 if comps:
  out.append({'object':o.name,'mesh':o.data.name,'mesh_users':o.data.users,'mesh_counts':[len(o.data.vertices),len(o.data.polygons)],'modifiers':[{'name':x.name,'type':x.type}for x in o.modifiers],'uv_layers':[x.name for x in o.data.uv_layers],'matrix_world':[list(r)for r in o.matrix_world],'material_slots':[{'index':i,'link':s.link,'name':s.material.name if s.material else None}for i,s in enumerate(o.material_slots)],'components':comps})
  used.update(s.material.name for s in o.material_slots if s.material)
 eo.to_mesh_clear()
def value(v):
 try:return list(v)
 except TypeError:return v
mats=[]
for name in sorted(used):
 m=bpy.data.materials[name];t=m.node_tree
 mats.append({'name':name,'users':m.users,'object_users':[{'object':o.name,'hidden_render':o.hide_render,'slots':[i for i,s in enumerate(o.material_slots)if s.material==m]}for o in bpy.data.objects if any(s.material==m for s in o.material_slots)],'nodes':[{'name':n.name,'type':n.bl_idname,'operation':getattr(n,'operation',None),'inputs':{s.name:value(s.default_value)for s in n.inputs if hasattr(s,'default_value')},'ramp':[{'position':e.position,'color':list(e.color)}for e in n.color_ramp.elements] if hasattr(n,'color_ramp')else None}for n in t.nodes]if t else [],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)for l in t.links]if t else []})
(P/'survey.json').write_text(json.dumps({'source_sha256':h,'source_unchanged':sha(src)==h,'objects':out,'materials':mats},indent=2));print([(o['object'],len(o['components']))for o in out])
