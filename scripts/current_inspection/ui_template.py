"""Manual-only embedded sidebar. Never auto-register via file load or handlers."""
import json,hashlib,sys,types
import bpy
from mathutils import Matrix
CONFIG = None  # Exporter replaces this assignment with literal reviewed config.
TAG='castle_inspection_owner'
OWNER='castle-current-inspection-v1'
REGISTRY='_castle_current_inspection_registry_v1'
CLASS_NAMES=('CASTLE23_INSPECTION_OT_bookmark','CASTLE23_PT_bookmarks')
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def verify():
 need(not sys.flags.optimize,'Optimized Python is unsupported')
 marker=bpy.context.scene.get(CONFIG['marker'])
 need(isinstance(marker,str),'Not an owned inspection copy')
 m=json.loads(marker);need(m.get('owner')==OWNER and m.get('catalog_sha256')==CONFIG['catalog_sha256'] and m.get('source_sha256')==CONFIG['source_sha256'],'Inspection provenance mismatch')
 text=bpy.data.texts.get(CONFIG['text']);need(text is not None and text.get(TAG)==OWNER and not text.use_module,'Manual Text ownership changed')
 need(hashlib.sha256(text.as_string().encode()).hexdigest()==m.get('ui_text_sha256'),'Manual UI text changed; re-export rather than adopting code')
 col=bpy.data.collections.get(CONFIG['collection']);need(col is not None and col.get(TAG)==OWNER and not col.hide_viewport and not col.hide_render and not col.hide_select,'Inspection collection unavailable')
 need(col.name in bpy.context.scene.collection.children and not col.children,'Inspection collection moved')
 need(not bpy.context.view_layer.layer_collection.hide_viewport,'View layer is hidden')
 lc=next((x for x in bpy.context.view_layer.layer_collection.children if x.collection==col),None)
 need(lc is not None and not lc.exclude and not lc.hide_viewport,'Inspection collection excluded/hidden')
 need(set(o.name for o in col.objects)=={v['camera_name'] for v in CONFIG['views'].values() if not v['existing']},'Unexpected inspection objects')
 for key in CONFIG['views']:_checked_camera(key)
 return m

def _checked_camera(key):
 need(key in CONFIG['views'],'Unknown bookmark');v=CONFIG['views'][key];o=bpy.data.objects.get(v['camera_name'])
 need(o is not None and o.type=='CAMERA' and o.name in bpy.context.view_layer.objects,'Bookmark camera missing')
 need(not o.hide_get() and not o.hide_viewport and not o.hide_select and not o.hide_render,'Bookmark hidden; no automatic unhide')
 def visible_path(lc,blocked=False):
  col=lc.collection;blocked=blocked or lc.exclude or lc.hide_viewport or col.hide_viewport or col.hide_render or col.hide_select
  return (not blocked and o.name in col.objects) or any(visible_path(child,blocked) for child in lc.children)
 need(visible_path(bpy.context.view_layer.layer_collection),'Camera parent collection/layer hidden or excluded')
 if not v['existing']:
  col=bpy.data.collections[CONFIG['collection']]
  need(o.get(TAG)==OWNER and o.data.get(TAG)==OWNER and tuple(o.users_collection)==(col,) and o.data.users==1 and o.data.name==v['camera_name']+' data' and o.get('bookmark_key')==key,'Camera ownership changed')
 need(not o.parent and not o.constraints and not o.modifiers and not o.animation_data and not o.data.animation_data,'Camera transform drivers/parent changed')
 need(o.delta_location.length<1e-8 and max(abs(x) for x in o.delta_rotation_euler)<1e-8 and max(abs(x-1) for x in o.delta_scale)<1e-8,'Camera delta transform changed')
 need(max(abs(o.matrix_world[i][j]-v['matrix'][i][j]) for i in range(4) for j in range(4))<1e-5,'Camera pose changed; no silent reset')
 for k,value in v['data'].items():
  actual=getattr(o.data,k);need(abs(actual-value)<1e-5 if isinstance(value,(int,float)) else actual==value,'Camera gate changed: '+k)
 need(not o.data.dof.use_dof,'Camera depth of field changed')
 return o,v

def select_bookmark(key,context=None):
 context=context or bpy.context;need(context.scene==bpy.context.scene and context.view_layer==bpy.context.view_layer,'Foreign scene/view-layer context rejected');verify();o,v=_checked_camera(key);context.scene.camera=o
 for screen in bpy.data.screens:
  for area in screen.areas:
   if area.type=='VIEW_3D':
    space=area.spaces.active;space.camera=o;space.use_local_camera=False;space.region_3d.view_perspective='CAMERA'
 return {'camera':o.name,'reference_resolution':v['reference_resolution'],'guidance':'Render aspect/quality unchanged. For exact historical framing set reference aspect manually in this copy.'}

class CASTLE23_INSPECTION_OT_bookmark(bpy.types.Operator):
 bl_idname='castle23_inspection.bookmark';bl_label='检查视角 / Inspection bookmark'
 view_id:bpy.props.StringProperty()
 def execute(self,context):
  try:
   result=select_bookmark(self.view_id,context);self.report({'INFO'},'Reference %s; current render settings unchanged'%result['reference_resolution']);return {'FINISHED'}
  except Exception as exc:self.report({'ERROR'},str(exc));return {'CANCELLED'}
class CASTLE23_PT_bookmarks(bpy.types.Panel):
 bl_label='城堡检查 / Castle inspection';bl_idname='CASTLE23_PT_bookmarks';bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='Castle检查'
 def draw(self,context):
  layout=self.layout
  try:verify()
  except Exception as exc:layout.label(text=str(exc),icon='ERROR');return
  layout.label(text='派生副本 / Derived inspection copy')
  layout.label(text='Quality and aspect stay unchanged')
  for key,v in CONFIG['views'].items():
   row=layout.row();row.operator(CASTLE23_INSPECTION_OT_bookmark.bl_idname,text=v['label']).view_id=key
  layout.label(text='Z: Solid / Material Preview / Rendered')
  layout.label(text='Manual quality edits: this copy only')
  layout.label(text='Provenance is not edit certification')

def register():
 verify();classes=(CASTLE23_INSPECTION_OT_bookmark,CASTLE23_PT_bookmarks);old=sys.modules.get(REGISTRY)
 if old is not None:
  need(getattr(old,'owner',None)==OWNER and getattr(old,'catalog_sha256',None)==CONFIG['catalog_sha256'],'Registry collision')
  need(all(getattr(bpy.types,c.__name__,None) is c for c in old.classes),'Registered class ownership changed')
  return False
 need(all(getattr(bpy.types,n,None) is None for n in CLASS_NAMES),'Sidebar/operator class name collision')
 registered=[]
 try:
  for cls in classes:bpy.utils.register_class(cls);registered.append(cls)
 except BaseException:
  for cls in reversed(registered):bpy.utils.unregister_class(cls)
  raise
 module=types.ModuleType(REGISTRY);module.owner=OWNER;module.catalog_sha256=CONFIG['catalog_sha256'];module.classes=classes;sys.modules[REGISTRY]=module;return True

def unregister():
 old=sys.modules.get(REGISTRY)
 if old is None:return False
 need(getattr(old,'owner',None)==OWNER and getattr(old,'catalog_sha256',None)==CONFIG['catalog_sha256'],'Registry collision')
 need(all(getattr(bpy.types,c.__name__,None) is c for c in old.classes),'Cannot unregister foreign classes')
 for cls in reversed(old.classes):bpy.utils.unregister_class(cls)
 del sys.modules[REGISTRY];return True

if __name__=='__main__':register()
