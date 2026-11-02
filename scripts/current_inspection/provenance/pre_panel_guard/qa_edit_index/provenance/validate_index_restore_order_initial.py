"""Independent native index selection transactions and exact non-selection preservation."""
import sys,json,hashlib,argparse,types,copy
from pathlib import Path
sys.dont_write_bytecode=True
if sys.flags.optimize:raise RuntimeError('Optimization refused')
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent));import snapshot_support as ss;import compare_support as cs
p=argparse.ArgumentParser()
for k in ['tool','default','off','high','low','modes-report','report']:p.add_argument('--'+k,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);paths={k:Path(v).resolve() for k,v in vars(a).items()};sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();need=cs.require;need(not paths['report'].exists(),'Output exists');base=json.loads(paths['modes_report'].read_text());need(base['pass'],'Prior modes gate false');runtime={n:sha(paths['tool']/n) for n in base['runtime_sha256']};need(runtime==base['runtime_sha256'],'Tool drift');catalog=json.loads((paths['tool']/'catalog.json').read_text());index=json.loads((paths['tool']/'edit_index.json').read_text());pins={str(paths[m]):sha(paths[m]) for m in ('default','off','high','low')};need(all(pins[str(paths[m])]==base['input_sha256'][m] for m in ('default','off','high','low')),'Viewer identity mismatch')
evidence={'modes':{},'negatives':[],'source_fingerprints_independently_validated_by':sha(paths['modes_report'])}
def load(mode):
 bpy.ops.wm.open_mainfile(filepath=str(paths[mode]),load_ui=True,use_scripts=False);text=bpy.data.texts[catalog['text']];need(not text.use_module,'Autoexec Text');ui=types.ModuleType('qa_index_'+mode);exec(compile(text.as_string(),'manual-index-text','exec'),ui.__dict__);ui.verify();return ui

def selections():return {vl.name:{'selected':sorted(o.name for o in vl.objects if o.select_get(view_layer=vl)),'active':vl.objects.active.name if vl.objects.active else None} for vl in bpy.context.scene.view_layers}
def restore_selection(state):
 for vl in bpy.context.scene.view_layers:
  row=state[vl.name]
  for o in vl.objects:o.select_set(o.name in row['selected'],view_layer=vl)
  vl.objects.active=vl.objects.get(row['active']) if row['active'] else None

def visibility():
 def layer(n):return {'name':n.name,'exclude':n.exclude,'hide_viewport':n.hide_viewport,'collection':n.collection.name,'children':[layer(c) for c in n.children]}
 return {vl.name:{'objects':{o.name:{'hide_get':o.hide_get(view_layer=vl),'select_get':o.select_get(view_layer=vl)} for o in vl.objects},'active':vl.objects.active.name if vl.objects.active else None,'layer':layer(vl.layer_collection)} for vl in bpy.context.scene.view_layers}
def camera_state():return {'scene_camera':bpy.context.scene.camera.name,'camera_data':{c.name:cs.digest(ss.primitive(c)) for c in bpy.data.cameras},'views':[(s.name,i,ar.spaces.active.camera.name if ar.spaces.active.camera else None,ar.spaces.active.use_local_camera,ar.spaces.active.region_3d.view_perspective) for s in bpy.data.screens for i,ar in enumerate(s.areas) if ar.type=='VIEW_3D']}
def restore_camera_ui(state):
 bpy.context.scene.camera=bpy.data.objects[state['scene_camera']]
 for screen,i,camera,local,perspective in state['views']:
  space=bpy.data.screens[screen].areas[i].spaces.active;space.camera=bpy.data.objects.get(camera) if camera else None;space.use_local_camera=local;space.region_3d.view_perspective=perspective
def snap():
 bpy.context.view_layer.update();x=ss.snap();x.update(collections=ss.collections_snapshot(),scene_custom=dict(bpy.context.scene.items()),visibility=visibility())
 for name in ('Traveler | full length ivory skirt','Traveler | purple-red shoulder cape','Traveler | white tunic'):x['visible_evaluated'][name],_=ss.render_semantic_with_ui_report(x['visible_evaluated'][name])
 return x
def guard_state():return {'selection':selections(),'camera':camera_state(),'visibility':visibility(),'marker':bpy.context.scene.get(catalog['marker']),'flags':{o.name:(o.hide_render,o.hide_viewport,o.hide_select) for o in bpy.data.objects},'objects':sorted(bpy.data.objects.keys()),'collections':ss.collections_snapshot()}
def reject(name,fn):
 before=guard_state()
 try:fn()
 except (RuntimeError,ValueError,KeyError):pass
 else:raise RuntimeError('Expected rejection '+name)
 need(guard_state()==before,'Rejected action mutation '+name);evidence['negatives'].append(name)
modules={}
for mode in ('default','off','high','low'):
 ui=load(mode);modules[mode]=ui;initial=snap();selection=selections();cam=camera_state();need(ui.register() is True and ui.register() is False,'Register idempotence');again=types.ModuleType('qa_manual_reexecute');exec(compile(bpy.data.texts[catalog['text']].as_string(),'manual-reexecute','exec'),again.__dict__);need(again.register() is False,'Manual reexecution not idempotent')
 if mode=='default':
  need(not hasattr(ui,'select_index') and 'CASTLE28_PT_edit_index' not in ui.CLASS_NAMES,'Default must have no index')
 else:
  actions=[]
  for j,view in enumerate(catalog['views']):
   ui.select_bookmark(view);before_camera=camera_state();key=list(index['groups'])[j%4]
   if mode in ('high','low'):
    for desired in ('LOW','HIGH',mode.upper()):
     ui.tree_set_mode(bpy.context.scene,desired);need(camera_state()==before_camera,'Tree camera drift')
     if desired=='LOW':reject(mode+' LOW near tree '+str(j),lambda:ui.select_index('near_tree_high'))
   if mode=='low' and key=='near_tree_high':reject('LOW hidden index '+str(j),lambda k=key:ui.select_index(k));continue
   expected=[o['name'] for o in index['groups'][key]['objects']];result=ui.select_index(key);need(result['selected']==expected,'Wrong selected names');after=selections();vl=bpy.context.view_layer.name;need(after[vl]=={'selected':sorted(expected),'active':expected[0]},'Wrong selected set/active');need(camera_state()==before_camera,'Index changed cameras/views');ui.select_index(key);need(selections()==after,'Index not idempotent');need(bpy.ops.castle28_inspection.edit_index(index_id=key)=={'FINISHED'},'Native index operator failed');need(selections()==after and camera_state()==before_camera,'Native operator state drift');actions.append({'bookmark':view,'index':key,'selection_count':len(expected)})
  for key in index['groups']:
   if mode=='low' and key=='near_tree_high':continue
   ui.select_index(key)
  restore_camera_ui(cam);restore_selection(selection);need(camera_state()==cam,'Final camera/view drift')
 need(snap()==initial,'Full non-selection source state drift '+mode);need(ui.unregister() is True and ui.unregister() is False,'Unregister idempotence');ui=load(mode);need(snap()==initial,'Reopen changed saved state');evidence['modes'][mode]={'exact_full_snapshot_after_restore':True,'reopen':True,'manual_reexecute':True,'actions':actions if mode!='default' else []}
# Index OFF vs ON has different runtime ownership even with tree OFF.
ui=load('off');reject('stale default module register on index ON',modules['default'].register);ui.register();reject('stale default unregister against index ON',modules['default'].unregister);ui.unregister()
ui=load('default');reject('stale index ON module register on default',modules['off'].register)
ui=load('high');initial=snap();original_selection=selections();target=bpy.data.objects['V028 | local receiving chamber shell'];key='receiving_shell'
def fixture(name,change,restore):
 change();bpy.context.view_layer.update()
 try:reject(name,lambda:ui.select_index(key))
 finally:restore();bpy.context.view_layer.update()
old=target.name;fixture('renamed/missing target',lambda:setattr(target,'name','QA changed target'),lambda:setattr(target,'name',old))
old=target.data.name;fixture('wrong data name',lambda:setattr(target.data,'name','QA changed data'),lambda:setattr(target.data,'name',old))
old=target.data.vertices[0].co.copy();fixture('edited target vertex',lambda:setattr(target.data.vertices[0],'co',old+__import__('mathutils').Vector((.01,0,0))),lambda:setattr(target.data.vertices[0],'co',old))
old=target.location.copy();fixture('edited target transform',lambda:setattr(target,'location',old+__import__('mathutils').Vector((.01,0,0))),lambda:setattr(target,'location',old))
face=target.data.polygons[0];old=face.use_smooth;fixture('edited smoothing',lambda:setattr(face,'use_smooth',not old),lambda:setattr(face,'use_smooth',old));old=face.material_index;fixture('edited material index',lambda:setattr(face,'material_index',old+1),lambda:setattr(face,'material_index',old))
old=target.data.materials[0];different=next(m for m in bpy.data.materials if m!=old);fixture('changed material binding',lambda:target.data.materials.__setitem__(0,different),lambda:target.data.materials.__setitem__(0,old))
for attr in ('hide_render','hide_viewport','hide_select'):fixture('target '+attr,lambda f=attr:setattr(target,f,True),lambda f=attr:setattr(target,f,False))
fixture('local eye hidden',lambda:target.hide_set(True),lambda:target.hide_set(False))
col=target.users_collection[0]
for attr in ('hide_render','hide_viewport','hide_select'):fixture('ancestor '+attr,lambda f=attr:setattr(col,f,True),lambda f=attr:setattr(col,f,False))
def find(node):
 if node.collection==col:return node
 for c in node.children:
  x=find(c)
  if x:return x
node=find(bpy.context.view_layer.layer_collection)
for attr in ('exclude','hide_viewport'):fixture('layer '+attr,lambda f=attr:setattr(node,f,True),lambda f=attr:setattr(node,f,False))
secondary=bpy.context.scene.view_layers.new('QA secondary');othernode=find(secondary.layer_collection);fixture('non-active layer exclusion',lambda:setattr(othernode,'exclude',True),lambda:setattr(othernode,'exclude',False));bpy.context.scene.view_layers.remove(secondary)
extra=bpy.data.collections.new('QA extra collection');bpy.context.scene.collection.children.link(extra);fixture('multiple memberships',lambda:extra.objects.link(target),lambda:extra.objects.unlink(target));bpy.data.collections.remove(extra)
inst=bpy.data.objects.new('QA instance',None);bpy.context.scene.collection.objects.link(inst);inst.instance_type='COLLECTION';fixture('collection instance',lambda:setattr(inst,'instance_collection',col),lambda:setattr(inst,'instance_collection',None));bpy.data.objects.remove(inst,do_unlink=True)
shared=bpy.data.objects.new('QA linked data',target.data);bpy.context.scene.collection.objects.link(shared);reject('shared target data',lambda:ui.select_index(key));bpy.data.objects.remove(shared,do_unlink=True)
# Same-name/count substitution must fail the independently bound geometry digest.
original=target.data;oldname=original.name;replacement=original.copy();original.name='QA retained original data';replacement.name=oldname;replacement.vertices[0].co.x+=.01;target.data=replacement
try:reject('same-name/count foreign mesh replacement',lambda:ui.select_index(key))
finally:target.data=original;bpy.data.meshes.remove(replacement);original.name=oldname
mod=target.modifiers.new('QA unexpected modifier','BEVEL');reject('unexpected modifier',lambda:ui.select_index(key));target.modifiers.remove(mod)
constraint=target.constraints.new('COPY_LOCATION');reject('unexpected constraint',lambda:ui.select_index(key));target.constraints.remove(constraint)
foreign=bpy.data.scenes.new('QA foreign scene');reject('actual foreign scene',lambda:ui.select_index(key,types.SimpleNamespace(scene=foreign,view_layer=bpy.context.view_layer,mode='OBJECT')));bpy.data.scenes.remove(foreign)
secondary=bpy.context.scene.view_layers.new('QA foreign layer');reject('actual foreign view layer',lambda:ui.select_index(key,types.SimpleNamespace(scene=bpy.context.scene,view_layer=secondary,mode='OBJECT')));bpy.context.scene.view_layers.remove(secondary)
# Enter actual Edit Mode; runtime must not exit or commit edits automatically.
restore_selection({bpy.context.view_layer.name:{'selected':[target.name],'active':target.name}});bpy.ops.object.mode_set(mode='EDIT')
try:
 reject('actual Edit Mode',lambda:ui.select_index(key));reject('spoofed OBJECT wrapper during actual Edit Mode',lambda:ui.select_index(key,types.SimpleNamespace(scene=bpy.context.scene,view_layer=bpy.context.view_layer,mode='OBJECT')))
finally:bpy.ops.object.mode_set(mode='OBJECT');restore_selection(original_selection)
oldhash=ui.CONFIG['edit_index_sha256'];ui.CONFIG['edit_index_sha256']='0'*64
try:reject('stale mapping hash',lambda:ui.select_index(key))
finally:ui.CONFIG['edit_index_sha256']=oldhash
oldfp=ui.CONFIG['edit_index_fingerprints'][target.name];ui.CONFIG['edit_index_fingerprints'][target.name]='0'*64
try:reject('stale geometry fingerprint',lambda:ui.select_index(key))
finally:ui.CONFIG['edit_index_fingerprints'][target.name]=oldfp
oldlabel=ui.CONFIG['edit_index']['groups'][key]['label'];ui.CONFIG['edit_index']['groups'][key]['label']='Unreviewed label'
try:reject('changed mapping content',lambda:ui.select_index(key))
finally:ui.CONFIG['edit_index']['groups'][key]['label']=oldlabel
reject('unknown group',lambda:ui.select_index('missing'))
# Partial setter failure after a real mutation; restore selected set and active, no undo.
ui.select_index('receiving_shell');setter=ui._index_select_set;calls=[0]
def fail_second(o,value,layer):
 calls[0]+=1
 if calls[0]==2:raise RuntimeError('Injected second selection setter')
 setter(o,value,layer)
ui._index_select_set=fail_second
try:reject('partial selection setter rollback',lambda:ui.select_index('room_lantern_meshes'));need(calls[0]==2,'Injection did not cross mutation')
finally:ui._index_select_set=setter
finder=ui.index_find;calls=[0]
def fail_validation(k,context=None):
 calls[0]+=1
 if calls[0]==2:raise RuntimeError('Injected post-active validation')
 return finder(k,context)
ui.index_find=fail_validation
try:reject('post-selection active-object rollback',lambda:ui.select_index('room_lantern_meshes'))
finally:ui.index_find=finder
# Ordinary edits invalidate selection but must not strand owned registered UI.
ui.register();old=target.data.vertices[0].co.copy();target.data.vertices[0].co.x+=.01
reject('edited action while registered',lambda:ui.select_index(key));need(ui.unregister() is True,'Owned unregister failed after edit');target.data.vertices[0].co=old
restore_selection(original_selection);need(snap()==initial,'Negative fixture full-state restoration drift')
need(all(sha(Path(p))==h for p,h in pins.items()) and runtime=={n:sha(paths['tool']/n) for n in runtime},'Input/runtime changed');evidence.update(pass_=True,viewer_sha256=pins,runtime_sha256=runtime,model_saved=False,rendered=False,limits='Linux background native API, not desktop UI or Windows. Fingerprints bind target geometry/transform and material slots, not shared material graph certification. Selection only; no automatic isolation or unhide.');evidence['pass']=evidence.pop('pass_');paths['report'].write_text(json.dumps(evidence,indent=2));print('INDEPENDENT EDITING INDEX PASS',len(evidence['negatives']))
