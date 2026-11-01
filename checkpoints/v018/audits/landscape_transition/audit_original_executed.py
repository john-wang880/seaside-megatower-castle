import bpy,json,hashlib,time
from pathlib import Path
from mathutils import Vector
D=Path('work/landscape_v019_audit');s=bpy.context.scene;src=Path(bpy.data.filepath);sha=lambda:hashlib.sha256(src.read_bytes()).hexdigest();before=sha();assert before=='c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd'
out={'source':str(src),'sha_before':before,'objects':[],'samples':[]}
for o in bpy.data.objects:
 if o.type=='MESH' and any(t in o.name.lower() for t in ['headland','coastal rock','grass','meadow']):
  vs=[o.matrix_world@Vector(v) for v in o.bound_box]
  out['objects'].append({'name':o.name,'visible_render':not o.hide_render,'mesh':o.data.name,'mesh_users':o.data.users,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'smooth_faces':sum(p.use_smooth for p in o.data.polygons),'min':[min(v[i] for v in vs) for i in range(3)],'max':[max(v[i] for v in vs) for i in range(3)],'materials':[m.name if m else None for m in o.data.materials],'modifiers':[(m.name,m.type) for m in o.modifiers],'vertex_groups':[g.name for g in o.vertex_groups]})
m=bpy.data.materials['Meadow and slate | slope-based procedural strata'];out['material']={'name':m.name,'users':m.users,'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links],'nodes':[]}
for n in m.node_tree.nodes:
 r={'name':n.name,'type':n.type};r['defaults']={i.name:(list(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value) for i in n.inputs if hasattr(i,'default_value') and not i.is_linked}
 if hasattr(n,'color_ramp'):r['ramp']=[(e.position,list(e.color)) for e in n.color_ramp.elements]
 out['material']['nodes'].append(r)
# Exact hero rays for selected pixels, exclude hidden objects explicitly by per-object cast.
cam=s.camera; frame=cam.data.view_frame(scene=s); xmin=min(v.x/-v.z for v in frame);xmax=max(v.x/-v.z for v in frame);ymin=min(v.y/-v.z for v in frame);ymax=max(v.y/-v.z for v in frame)
obs=[o for o in bpy.context.view_layer.objects if o.type=='MESH' and not o.hide_render and not o.hide_get()];deps=bpy.context.evaluated_depsgraph_get()
for px,py in [(680,610),(700,630),(740,620),(770,600),(800,625),(850,610),(900,630),(930,655)]:
 dr=(cam.matrix_world.to_3x3()@Vector((xmin+(xmax-xmin)*px/1200,ymax-(ymax-ymin)*py/866,-1))).normalized();origin=cam.matrix_world.translation;hits=[]
 for o in obs:
  e=o.evaluated_get(deps);inv=e.matrix_world.inverted();h,l,n,f=e.ray_cast(inv@origin,(inv.to_3x3()@dr).normalized())
  if h:
   w=e.matrix_world@l;hits.append(((w-origin).length,o.name,list(w),f,list(e.matrix_world.to_3x3()@n)))
 hits.sort();out['samples'].append({'pixel':[px,py],'nearest':hits[:3]})
D.joinpath('audit.json').write_text(json.dumps(out,indent=2))
# One actual-light, same-perspective bounded enlargement; no new scene geometry.
r=s.render;receipt={'source_sha':before,'camera':cam.name,'matrix_world':[list(x) for x in cam.matrix_world],'lens':cam.data.lens,'original_resolution':[r.resolution_x,r.resolution_y,r.resolution_percentage],'samples':s.cycles.samples,'max_bounces':s.cycles.max_bounces,'world':s.world.name,'exposure':s.view_settings.exposure,'view_transform':s.view_settings.view_transform,'crop_hero_pixels':[620,575,980,695],'lighting_changed':False,'saved_model':False}
r.resolution_x=3600;r.resolution_y=2598;r.resolution_percentage=100;r.use_border=True;r.use_crop_to_border=True;r.border_min_x=620/1200;r.border_max_x=980/1200;r.border_min_y=1-695/866;r.border_max_y=1-575/866;r.threads_mode='FIXED';r.threads=8;r.filepath=str(D/'hero_slope_detail.png');t=time.time();bpy.ops.render.render(write_still=True);receipt['elapsed_seconds']=time.time()-t;receipt['source_sha_after']=sha();assert sha()==before;D.joinpath('render_receipt.json').write_text(json.dumps(receipt,indent=2));print('AUDIT_COMPLETE')
