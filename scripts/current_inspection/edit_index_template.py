"""Optional manual selection index. Does not isolate, unhide, rename or edit geometry."""
def index_fingerprint(obj):
 import struct
 h=hashlib.sha256()
 # Full positions/topology binding; selection bits intentionally not included.
 a=[0.0]*(len(obj.data.vertices)*3);obj.data.vertices.foreach_get('co',a)
 h.update(struct.pack('<%sf'%len(a),*a))
 for p in obj.data.polygons:
  h.update(struct.pack('<III?',len(p.vertices),p.material_index,p.loop_start,p.use_smooth))
  h.update(struct.pack('<%sI'%len(p.vertices),*p.vertices))
 h.update(repr([[float(x) for x in row] for row in obj.matrix_world]).encode())
 return h.hexdigest()

def index_paths(root,name):
 paths=[]
 def walk(node,path):
  chain=path+[node]
  if name in node.collection.objects:paths.append(chain)
  for child in node.children:walk(child,chain)
 walk(root,[])
 need(len(paths)==1,'Index target requires one collection path')
 for node in paths[0]:
  need(not node.exclude and not node.hide_viewport and not node.collection.hide_viewport and not node.collection.hide_render and not node.collection.hide_select,'Index ancestor hidden, excluded or unselectable')
 return True

def index_find(key,context=None):
 context=context or bpy.context
 need(context.scene == bpy.context.scene and context.view_layer == bpy.context.view_layer,'Foreign index context')
 need(context.mode=='OBJECT' and bpy.context.mode=='OBJECT','Selection index requires Object Mode; no automatic mode changes')
 marker=verify()
 need(CONFIG.get('edit_index_enabled') is True and marker.get('edit_index_enabled') is True,'Editing index not opted in')
 index=CONFIG['edit_index'];need(index['source_sha256']==CONFIG['source_sha256'],'Index source mismatch')
 need(hashlib.sha256(json.dumps(index,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()==CONFIG['edit_index_sha256'],'Index mapping changed')
 need(key in index['groups'],'Unknown editing index key')
 records=index['groups'][key]['objects'];found=[]
 def contains(col,name):return name in col.objects or any(contains(c,name) for c in col.children)
 for spec in records:
  o=bpy.data.objects.get(spec['name'])
  need(o is not None and o.type=='MESH' and o.name in context.scene.objects and o.name in context.view_layer.objects,'Missing index mesh')
  need(o.data.name==spec['data'] and o.data.users==spec['data_users']==1 and len(o.data.vertices)==spec['vertices'] and len(o.data.polygons)==spec['faces'],'Index mesh identity changed')
  need([c.name for c in o.users_collection]==spec['collections'],'Index collection membership changed')
  need([{'name':s.material.name if s.material else None,'link':s.link} for s in o.material_slots]==spec['materials'],'Index material bindings changed')
  need(not o.modifiers and not o.parent and not o.constraints and not o.animation_data and not o.data.animation_data and not o.data.shape_keys,'Index target dependencies changed')
  need(not o.hide_select and not o.hide_render and not o.hide_viewport and not o.hide_get() and o.visible_get(),'Index target hidden/unselectable; no automatic unhide (HIGH tree unavailable in LOW)')
  for layer in context.scene.view_layers:index_paths(layer.layer_collection,o.name)
  for inst in bpy.data.objects:
   need(not(inst.instance_type=='COLLECTION' and inst.instance_collection and contains(inst.instance_collection,o.name)),'Instanced index targets unsupported')
  need(index_fingerprint(o)==CONFIG['edit_index_fingerprints'][o.name],'Index geometry/transform changed; re-export rather than adopting edited targets')
  found.append(o)
 return found

def _index_select_set(obj,value,layer):obj.select_set(value,view_layer=layer)

def select_index(key,context=None):
 context=context or bpy.context;objects=index_find(key,context);layer=context.view_layer
 prior=[(o,o.select_get(view_layer=layer)) for o in layer.objects];active=layer.objects.active
 try:
  selected=set(objects)
  for o,was in prior:
   want=o in selected
   if was!=want:_index_select_set(o,want,layer)
  layer.objects.active=objects[0]
  index_find(key,context)
  need({o.name for o in layer.objects if o.select_get(view_layer=layer)}=={o.name for o in objects},'Selection result mismatch')
  return {'selected':[o.name for o in objects],'active':objects[0].name,'notice':'Selection only. Shared materials/assembly dependencies remain; no isolation or editing certification.'}
 except BaseException:
  for o,was in prior:o.select_set(was,view_layer=layer)
  layer.objects.active=active
  raise

class CASTLE30_INSPECTION_OT_edit_index(bpy.types.Operator):
 bl_idname='castle30_inspection.edit_index';bl_label='Select accepted geometry'
 index_id:bpy.props.StringProperty()
 def execute(self,context):
  try:select_index(self.index_id,context);return {'FINISHED'}
  except Exception as exc:self.report({'ERROR'},str(exc));return {'CANCELLED'}

class CASTLE30_PT_edit_index(bpy.types.Panel):
 bl_label='Selection index / Accepted features';bl_idname='CASTLE30_PT_edit_index';bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='Castle检查'
 def draw(self,context):
  layout=self.layout
  try:
   marker=verify();need(CONFIG.get('edit_index_enabled') is True and marker.get('edit_index_enabled') is True,'Selection index not enabled in this copy')
  except Exception as exc:layout.label(text=str(exc),icon='ERROR');return
  layout.label(text='Manual selection only; no isolation')
  layout.label(text='Shared materials / combined hosts remain')
  for key,g in CONFIG['edit_index']['groups'].items():layout.operator(CASTLE30_INSPECTION_OT_edit_index.bl_idname,text=g['label']).index_id=key
  if 'stores_fittings' in CONFIG['edit_index']['groups']:layout.label(text='Freestanding fittings; architecture unchanged')
  layout.label(text='HIGH tree unavailable while LOW/hidden')
  layout.label(text='Historical candidate labels are provenance')
