import bpy,json,hashlib,pathlib
P=pathlib.Path('/workspace/scratch/8bdb2666bb6b/seaside-megatower-castle'); s=P/'work/v028/castle_v028.blend'; before=hashlib.sha256(s.read_bytes()).hexdigest(); assert before=='f0d135e0c6e554b5ae7c520ef9ccefc61e2a7c4abc3129eef1d3d4118bca8096'
bpy.ops.wm.open_mainfile(filepath=str(s),load_ui=True)
def layer(c): return dict(name=c.name,exclude=c.exclude,hide_viewport=c.hide_viewport,children=[layer(x) for x in c.children])
obs=[]
for o in bpy.data.objects:
 d=dict(name=o.name,type=o.type,data=o.data.name if o.data else None,data_users=o.data.users if o.data else None,collections=[c.name for c in o.users_collection],hide_viewport=o.hide_viewport,hide_render=o.hide_render,hide_select=o.hide_select,parent=o.parent.name if o.parent else None,modifiers=[dict(name=m.name,type=m.type,viewport=m.show_viewport,render=m.show_render,group=getattr(m,'vertex_group',None),invert=getattr(m,'invert_vertex_group',None)) for m in o.modifiers],groups=[g.name for g in o.vertex_groups],layers={})
 for v in bpy.context.scene.view_layers:
  if o.name in v.objects: d['layers'][v.name]=dict(hidden=o.hide_get(view_layer=v),visible=o.visible_get(view_layer=v),selected=o.select_get(view_layer=v))
 if o.type=='MESH': d.update(vertices=len(o.data.vertices),faces=len(o.data.polygons),materials=[dict(name=x.material.name if x.material else None,link=x.link) for x in o.material_slots])
 obs.append(d)
r=dict(source_sha256=before,objects=obs,collections=[dict(name=c.name,hide_viewport=c.hide_viewport,hide_render=c.hide_render,hide_select=c.hide_select,objects=[o.name for o in c.objects],children=[x.name for x in c.children]) for c in bpy.data.collections],view_layers=[dict(name=v.name,active=v.objects.active.name if v.objects.active else None,collection=layer(v.layer_collection)) for v in bpy.context.scene.view_layers],active_layer=bpy.context.view_layer.name,scene_camera=bpy.context.scene.camera.name if bpy.context.scene.camera else None,texts=[t.name for t in bpy.data.texts],screens=[dict(name=sc.name,spaces=[dict(type=a.type,clip_start=a.spaces.active.clip_start,clip_end=a.spaces.active.clip_end,view_distance=a.spaces.active.region_3d.view_distance,view_perspective=a.spaces.active.region_3d.view_perspective) for a in sc.areas if a.type=='VIEW_3D']) for sc in bpy.data.screens])
r['source_sha256_after']=hashlib.sha256(s.read_bytes()).hexdigest(); assert r['source_sha256_after']==before
(P/'work/v028_editability_review/inventory.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
print('READONLY_INVENTORY_PASS',len(obs))
