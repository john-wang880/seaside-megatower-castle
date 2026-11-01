import bpy,json,hashlib
from pathlib import Path
P=Path('work/gallery_support_graph_v018');rows=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and not o.hide_render and (o.hide_viewport or not o.visible_get()):rows.append({'object':o.name,'hide_viewport':o.hide_viewport,'hide_get':o.hide_get(),'visible_get':o.visible_get(),'collections':[c.name for c in o.users_collection]})
def layer(c):return {'name':c.name,'exclude':c.exclude,'hide_viewport':c.hide_viewport,'children':[layer(x) for x in c.children]}
r={'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'render_enabled_meshes_omitted_by_viewport_filter':rows,'view_layer':layer(bpy.context.view_layer.layer_collection),'all_object_hidden_originals_also_hide_render':not any(o.hide_viewport and not o.hide_render for o in bpy.context.scene.objects if o.type=='MESH'),'saved':False};(P/'visibility_audit.json').write_text(json.dumps(r,indent=2));print('OMITTED',rows)
