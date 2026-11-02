"""Literal embedded optional v028 tree controls; no auto-registration/save/render."""
TARGET='V010 | woodland boughs with gate exit clearance'
GROUP='V019 candidate | reversible left tree foliage'
MASK='V019 candidate | original foliage rollback mask'
NEW=('V019 candidate | articulated conifer foliage','V019 candidate | connected conifer boughs')
COUNTS=((415590,332472),(50265,40668))
SELECTED=set(range(90395,90693))
def tree_require(ok,message):
 if not ok:raise RuntimeError(message)
def expected_flags(mode):
 tree_require(mode in ('HIGH','LOW'),'Unknown quality mode')
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
 tree_require(len(paths)==1,'Expected exactly one collection path; missing or multiple memberships unsupported')
 for node in paths[0]:
  tree_require(not node.exclude and not node.hide_viewport,'Ancestor LayerCollection hidden/excluded')
  tree_require(not node.collection.hide_viewport and not node.collection.hide_render,'Ancestor Collection hidden in viewport/render')
 return True

def tree_find(scene):
 import bpy
 verify()
 tree_require(scene is bpy.context.scene,'Quality context scene mismatch')
 marker=json.loads(scene[CONFIG['marker']]);tag=marker.get('tree_quality')
 tree_require(CONFIG.get('tree_quality_enabled') is True and isinstance(tag,dict),'Tree controls not opted in')
 tree_require(tag.get('schema')=='castle-inspection-v030-tree-v1' and tag.get('mode') in ('HIGH','LOW'),'Invalid quality state')
 tree_require(TARGET in scene.objects and all(n in scene.objects for n in NEW),'Expected scene objects missing')
 target=scene.objects[TARGET];objects=[scene.objects[n] for n in NEW]
 for layer in scene.view_layers:
  for obj in [target,*objects]:visible_collection_paths(layer.layer_collection,obj.name)
 # Conservatively reject collection instances containing the target hierarchy.
 def contains(col,name):
  return name in col.objects or any(contains(child,name) for child in col.children)
 for inst in bpy.data.objects:
  if inst.instance_type=='COLLECTION' and inst.instance_collection:
   tree_require(not any(contains(inst.instance_collection,o.name) for o in [target,*objects]),'Tree collection instances unsupported')
 tree_require(target.type=='MESH' and len(target.data.vertices)==204154,'Unexpected source foliage')
 tree_require(not target.hide_viewport and not target.hide_render,'Original foliage object must remain visible')
 for layer in scene.view_layers:
  tree_require(target.name in layer.objects and not target.hide_get(view_layer=layer),'Original foliage excluded or locally hidden')
 tree_require(len(target.vertex_groups)==1 and target.vertex_groups[0].name==GROUP,'Unexpected vertex groups')
 group=target.vertex_groups[0];weights={v.index:tuple((w.group,w.weight) for w in v.groups) for v in target.data.vertices if v.groups}
 tree_require(set(weights)==SELECTED and all(v==((group.index,1.0),) for v in weights.values()),'Owned 298 weights changed')
 tree_require(len(target.modifiers)==1 and target.modifiers[0].name==MASK,'Unexpected modifier stack')
 mod=target.modifiers[0]
 tree_require(mod.type=='MASK' and mod.mode=='VERTEX_GROUP' and mod.armature is None and mod.vertex_group==GROUP and mod.invert_vertex_group and mod.threshold==.5 and not mod.use_smooth,'Owned Mask configuration changed')
 for obj,counts in zip(objects,COUNTS):
  tree_require(obj.type=='MESH' and (len(obj.data.vertices),len(obj.data.polygons))==counts and not obj.modifiers,'Unexpected authored tree object')
  tree_require(obj.data.users==1,'Unexpected shared authored mesh')
  tree_require(not obj.parent and not obj.constraints and not obj.animation_data,'Unexpected authored object transform dependencies')
  tree_require(all(abs(obj.matrix_world[i][j]-(i==j))<1e-9 for i in range(4) for j in range(4)),'Authored transform changed')
  for layer in scene.view_layers:
   tree_require(obj.name in layer.objects,'Authored object excluded from a view layer')
   tree_require(not obj.hide_get(view_layer=layer),'Local eye-icon hiding is unsupported; clear it first')
 flags={'mask_viewport':mod.show_viewport,'mask_render':mod.show_render,'objects':[[o.hide_viewport,o.hide_render] for o in objects]}
 mode=classify_flags(flags);tree_require(tag['mode']==mode,'Marker/flag mode mismatch')
 return target,mod,objects,tag,mode

def tree_set_mode(scene,mode):
 flags=expected_flags(mode);target,mod,objects,tag,oldmode=tree_find(scene)
 if mode==oldmode:return {'mode':mode,'changed':False}
 old=expected_flags(oldmode);oldtag=scene[CONFIG['marker']]
 try:
  mod.show_viewport=flags['mask_viewport'];mod.show_render=flags['mask_render']
  for o,pair in zip(objects,flags['objects']):o.hide_viewport,o.hide_render=pair
  tag['mode']=mode;marker=json.loads(scene[CONFIG['marker']]);marker['tree_quality']=tag;scene[CONFIG['marker']]=json.dumps(marker,sort_keys=True)
  tree_find(scene)
 except BaseException:
  mod.show_viewport=old['mask_viewport'];mod.show_render=old['mask_render']
  for o,pair in zip(objects,old['objects']):o.hide_viewport,o.hide_render=pair
  scene[CONFIG['marker']]=oldtag
  raise
 return {'mode':mode,'changed':True}


def tree_display_mode(scene):
 """Cheap label only. Action/export still run the complete ownership/weight guard."""
 import bpy
 marker=json.loads(scene[CONFIG['marker']]);tag=marker.get('tree_quality',{})
 tree_require(CONFIG.get('tree_quality_enabled') is True,'Tree controls not opted in')
 target=scene.objects.get(TARGET);tree_require(target is not None,'Tree target missing')
 mod=target.modifiers.get(MASK);tree_require(mod is not None,'Tree Mask missing')
 objects=[scene.objects.get(n) for n in NEW];tree_require(all(o is not None for o in objects),'Tree objects missing')
 mode=classify_flags({'mask_viewport':mod.show_viewport,'mask_render':mod.show_render,'objects':[[o.hide_viewport,o.hide_render] for o in objects]})
 tree_require(tag.get('mode')==mode,'Mode marker/paired flags mismatch')
 return mode
