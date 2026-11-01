"""Manual-run Castle sidebar for a tagged v019 viewer copy; never saves files.
Run this text explicitly in Blender's Text Editor to register the two buttons.
"""
import json
SOURCE_SHA='e71778349c4c65eafbda3eb0a3d0753cd11e1b368a3456c4de1db2f4c0f8647a'
MARKER='castle_v019_quality_viewer'
TEXT_NAME='CASTLE | v019 tree quality controls (manual)'
TARGET='V010 | woodland boughs with gate exit clearance'
GROUP='V019 candidate | reversible left tree foliage'
MASK='V019 candidate | original foliage rollback mask'
NEW=('V019 candidate | articulated conifer foliage','V019 candidate | connected conifer boughs')
COUNTS=((415590,332472),(50265,40668))
SELECTED=set(range(90395,90693))
def require(ok,message):
 if not ok:raise RuntimeError(message)
def expected_flags(mode):
 require(mode in ('HIGH','LOW'),'Unknown quality mode')
 low=mode=='LOW'
 return {'mask_viewport':not low,'mask_render':not low,'objects':[[low,low],[low,low]]}
def classify_flags(flags):
 for mode in ('HIGH','LOW'):
  if flags==expected_flags(mode):return mode
 raise RuntimeError('Mixed visibility state: restore the paired flags manually before using this tool')
def visible_collection_paths(root,object_name):
 """Pure duck-typed layer tree check; return only paths with all ancestors enabled.
 Multiple collection memberships/instances are deliberately unsupported: the tool
 must not silently infer which hidden/visible path the user intended.
 """
 paths=[]
 def walk(node,path):
  chain=path+[node]
  if object_name in node.collection.objects:paths.append(chain)
  for child in node.children:walk(child,chain)
 walk(root,[])
 require(len(paths)==1,'Expected exactly one collection path; missing or multiple memberships unsupported')
 for node in paths[0]:
  require(not node.exclude and not node.hide_viewport,'Ancestor LayerCollection hidden/excluded')
  require(not node.collection.hide_viewport and not node.collection.hide_render,'Ancestor Collection hidden in viewport/render')
 return True

def find(scene):
 import bpy
 require(MARKER in scene,'Not a tagged v019 viewer copy')
 try:tag=json.loads(scene[MARKER])
 except Exception as e:raise RuntimeError('Invalid viewer marker') from e
 require(tag.get('schema')=='castle-v019-quality-v1' and tag.get('source_sha256')==SOURCE_SHA,'Unrecognized viewer marker')
 require(tag.get('mode') in ('HIGH','LOW'),'Invalid saved viewer mode')
 require(TEXT_NAME in bpy.data.texts and not bpy.data.texts[TEXT_NAME].use_module,'Missing manual-only controls Text')
 require(TARGET in scene.objects and all(n in scene.objects for n in NEW),'Expected scene objects missing')
 target=scene.objects[TARGET];objects=[scene.objects[n] for n in NEW]
 for layer in scene.view_layers:
  for obj in [target,*objects]:visible_collection_paths(layer.layer_collection,obj.name)
 require(target.type=='MESH' and len(target.data.vertices)==204154,'Unexpected source foliage')
 require(not target.hide_viewport and not target.hide_render,'Original foliage object must remain visible')
 for layer in scene.view_layers:
  require(target.name in layer.objects and not target.hide_get(view_layer=layer),'Original foliage excluded or locally hidden')
 require(len(target.vertex_groups)==1 and target.vertex_groups[0].name==GROUP,'Unexpected vertex groups')
 group=target.vertex_groups[0];weights={v.index:tuple((w.group,w.weight) for w in v.groups) for v in target.data.vertices if v.groups}
 require(set(weights)==SELECTED and all(v==((group.index,1.0),) for v in weights.values()),'Owned 298 weights changed')
 require(len(target.modifiers)==1 and target.modifiers[0].name==MASK,'Unexpected modifier stack')
 mod=target.modifiers[0]
 require(mod.type=='MASK' and mod.mode=='VERTEX_GROUP' and mod.armature is None and mod.vertex_group==GROUP and mod.invert_vertex_group and mod.threshold==.5 and not mod.use_smooth,'Owned Mask configuration changed')
 for obj,counts in zip(objects,COUNTS):
  require(obj.type=='MESH' and (len(obj.data.vertices),len(obj.data.polygons))==counts and not obj.modifiers,'Unexpected authored tree object')
  require(obj.data.users==1,'Unexpected shared authored mesh')
  require(not obj.parent and not obj.constraints and not obj.animation_data,'Unexpected authored object transform dependencies')
  require(all(abs(obj.matrix_world[i][j]-(i==j))<1e-9 for i in range(4) for j in range(4)),'Authored transform changed')
  for layer in scene.view_layers:
   require(obj.name in layer.objects,'Authored object excluded from a view layer')
   require(not obj.hide_get(view_layer=layer),'Local eye-icon hiding is unsupported; clear it first')
 flags={'mask_viewport':mod.show_viewport,'mask_render':mod.show_render,'objects':[[o.hide_viewport,o.hide_render] for o in objects]}
 mode=classify_flags(flags);require(tag['mode']==mode,'Marker/flag mode mismatch')
 return target,mod,objects,tag,mode

def set_mode(scene,mode):
 flags=expected_flags(mode);target,mod,objects,tag,oldmode=find(scene)
 if mode==oldmode:return {'mode':mode,'changed':False}
 old=expected_flags(oldmode);oldtag=scene[MARKER]
 try:
  mod.show_viewport=flags['mask_viewport'];mod.show_render=flags['mask_render']
  for o,pair in zip(objects,flags['objects']):o.hide_viewport,o.hide_render=pair
  tag['mode']=mode;scene[MARKER]=json.dumps(tag,sort_keys=True)
  find(scene)
 except BaseException:
  mod.show_viewport=old['mask_viewport'];mod.show_render=old['mask_render']
  for o,pair in zip(objects,old['objects']):o.hide_viewport,o.hide_render=pair
  scene[MARKER]=oldtag
  raise
 return {'mode':mode,'changed':True}

def register():
 import bpy
 # Only this module's identifiers are replaced; unrelated registered classes are never touched.
 unregister()
 class CASTLE_V019_OT_tree_quality(bpy.types.Operator):
  bl_idname='castle_v019.tree_quality';bl_label='Castle Tree Quality';bl_options={'REGISTER','UNDO'}
  mode: bpy.props.EnumProperty(items=[('HIGH','HIGH','Detailed single-tree canopy'),('LOW','LOW','Original low-detail canopy')])
  def execute(self,context):
   try:set_mode(context.scene,self.mode)
   except Exception as e:self.report({'ERROR'},str(e));return {'CANCELLED'}
   return {'FINISHED'}
 class CASTLE_V019_PT_tree_quality(bpy.types.Panel):
  bl_idname='CASTLE_V019_PT_tree_quality';bl_label='Foreground Tree Quality';bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='Castle'
  def draw(self,context):
   layout=self.layout
   try:
    scene=context.scene;require(MARKER in scene,'Not a tagged viewer');tag=json.loads(scene[MARKER]);require(tag.get('source_sha256')==SOURCE_SHA and tag.get('schema')=='castle-v019-quality-v1','Invalid marker');mod=scene.objects[TARGET].modifiers[MASK];obs=[scene.objects[n] for n in NEW];mode=classify_flags({'mask_viewport':mod.show_viewport,'mask_render':mod.show_render,'objects':[[o.hide_viewport,o.hide_render] for o in obs]});require(tag.get('mode')==mode,'Marker/flag mismatch')
    target=scene.objects[TARGET];require(not target.hide_viewport and not target.hide_render,'Original foliage hidden')
    for layer in scene.view_layers:
     for obj in [target,*obs]:
      visible_collection_paths(layer.layer_collection,obj.name);require(obj.name in layer.objects and not obj.hide_get(view_layer=layer),'Object locally hidden/excluded')
    layout.label(text='Current: '+mode);row=layout.row(align=True);row.operator('castle_v019.tree_quality',text='HIGH').mode='HIGH';row.operator('castle_v019.tree_quality',text='LOW').mode='LOW'
   except Exception as e:layout.label(text='Viewer guard: '+str(e),icon='ERROR')
   layout.label(text='One tree only; no file saving')
 for cls in (CASTLE_V019_OT_tree_quality,CASTLE_V019_PT_tree_quality):
  cls._castle_v019_quality_owned=True;bpy.utils.register_class(cls)

def unregister():
 import bpy
 classes=[getattr(bpy.types,name,None) for name in ['CASTLE_V019_PT_tree_quality','CASTLE_V019_OT_tree_quality']]
 for cls in classes:
  if cls is not None:require(getattr(cls,'_castle_v019_quality_owned',False),'Unrelated registered class name collision')
 for cls in classes:
  if cls is not None:bpy.utils.unregister_class(cls)
if __name__=='__main__':register()
