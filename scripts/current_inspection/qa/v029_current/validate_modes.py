"""Independent actual no-save inspection/quality mode QA; native execution needs owner slot."""
import argparse,copy,hashlib,json,sys,types
from pathlib import Path
if sys.flags.optimize:raise RuntimeError('Optimized Python unsupported')
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
import snapshot_support as ss
import compare_support as cs
p=argparse.ArgumentParser()
for k in ('source','baseline','tool','default','off','high','low','default-receipt','off-receipt','high-receipt','low-receipt','report'):p.add_argument('--'+k,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);paths={k:Path(v).resolve() for k,v in vars(a).items()};sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
cs.require(not paths['report'].exists(),'Report exists');inputs={k:sha(v) for k,v in paths.items() if k not in ('tool','report')};cs.require(inputs['source']==cs.SOURCE_SHA and inputs['baseline']==cs.BASE_SHA,'Input source identity')
cs.require(sha(paths['tool']/'catalog.json')=='b10ecd91f93b59c71523663e8336b07bf9d7bda6c28950ac643a1ac8100c8424','Frozen 20-camera catalog changed');catalog=json.loads((paths['tool']/'catalog.json').read_text());cs.require(len(catalog['views'])==20,'Expected frozen 20-view catalog');runtime={n:sha(paths['tool']/n) for n in ('export_inspection.py','preflight.py','catalog.json','ui_template.py','tree_quality_template.py','edit_index_template.py','edit_index.json')};evidence={'modes':{},'negatives':[],'derived_ui':[]}
def load(key):
 global guard_objects
 bpy.ops.wm.open_mainfile(filepath=str(paths[key]),load_ui=True,use_scripts=False)
 guard_objects=[bpy.data.objects.get(n) for n in cs.NEW]
def visibility():
 def layer(n):return {'name':n.name,'exclude':n.exclude,'hide_viewport':n.hide_viewport,'collection':n.collection.name,'children':[layer(c) for c in n.children]}
 return {vl.name:{'objects':{o.name:{'hide_get':o.hide_get(view_layer=vl),'select_get':o.select_get(view_layer=vl)} for o in vl.objects},'active':vl.objects.active.name if vl.objects.active else None,'layer':layer(vl.layer_collection)} for vl in bpy.context.scene.view_layers}
def snap():
 bpy.context.view_layer.update();x=ss.snap();x.update(collections=ss.collections_snapshot(),scene_custom=dict(bpy.context.scene.items()),visibility=visibility())
 for name in ('Traveler | full length ivory skirt','Traveler | purple-red shoulder cape','Traveler | white tunic'):
  before=x['visible_evaluated'][name];x['visible_evaluated'][name],ui=ss.render_semantic_with_ui_report(before);evidence['derived_ui'].append({'object':name,'selection':ui})
 return x
def camera_state():
 return {'scene_camera':bpy.context.scene.camera.name,'camera_data':{c.name:cs.digest(ss.primitive(c)) for c in bpy.data.cameras},'views':[(s.name,ai,ar.spaces.active.camera.name if ar.spaces.active.camera else None,ar.spaces.active.use_local_camera,ar.spaces.active.region_3d.view_perspective) for s in bpy.data.screens for ai,ar in enumerate(s.areas) if ar.type=='VIEW_3D']}
def flags():
 m=bpy.data.objects[cs.TARGET].modifiers[cs.MASK]
 return [m.show_viewport,m.show_render,*[value for obj in guard_objects for value in (obj.hide_viewport,obj.hide_render)]]
def guarded_state():return (flags(),bpy.context.scene.get(catalog['marker']),camera_state())
def reject(label,fn):
 before=guarded_state()
 try:fn()
 except (RuntimeError,ValueError,KeyError):pass
 else:raise RuntimeError('Expected rejection: '+label)
 cs.require(guarded_state()==before,'Rejected operation changed state: '+label);evidence['negatives'].append(label)
def source_fingerprint(obj):
 import struct,array
 h=hashlib.sha256();a=array.array('f',[0.])*(len(obj.data.vertices)*3);obj.data.vertices.foreach_get('co',a);h.update(struct.pack('<%sf'%len(a),*a))
 for poly in obj.data.polygons:
  h.update(struct.pack('<III?',len(poly.vertices),poly.material_index,poly.loop_start,poly.use_smooth));h.update(struct.pack('<%sI'%len(poly.vertices),*poly.vertices))
 h.update(repr([[float(x) for x in row] for row in obj.matrix_world]).encode());return h.hexdigest()
def code_for(mode):
 enabled=mode!='default';tree=mode in ('high','low');cfg={k:catalog[k] for k in ('collection','text','marker','views','source_sha256')};cfg.update(catalog_sha256=runtime['catalog.json'],tree_quality_enabled=tree)
 cfg['runtime_identity']=hashlib.sha256(((paths['tool']/'ui_template.py').read_text()+(paths['tool']/'tree_quality_template.py').read_text()+runtime['catalog.json']+str(tree)+(paths['tool']/'edit_index_template.py').read_text()+(paths['tool']/'edit_index.json').read_text()+str(enabled)).encode()).hexdigest()
 cfg['edit_index_enabled']=enabled
 if enabled:
  index=json.loads((paths['tool']/'edit_index.json').read_text());cfg.update(edit_index=index,edit_index_sha256=hashlib.sha256(json.dumps(index,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest(),edit_index_fingerprints=source_fingerprints)
 code=(paths['tool']/'ui_template.py').read_text().replace('CONFIG = None  # Exporter replaces this assignment with literal reviewed config.','CONFIG = '+repr(cfg))
 return code.replace('# TREE_HELPER_LITERAL',(paths['tool']/'tree_quality_template.py').read_text() if tree else '').replace('# EDIT_INDEX_HELPER_LITERAL',(paths['tool']/'edit_index_template.py').read_text() if enabled else '')
def module(mode):
 code=code_for(mode);text=bpy.data.texts[catalog['text']];cs.require(text.as_string()==code and not text.use_module,'Embedded Text mismatch')
 ui=types.ModuleType('independent_tree_mode_'+mode);exec(compile(code,'owned-manual-ui','exec'),ui.__dict__);return ui
load('baseline');baseline=snap();load('source');canonical=snap();index=json.loads((paths['tool']/'edit_index.json').read_text());from expected_scope import validate_scope;validate_scope(catalog,index,paths['tool']);source_fingerprints={spec['name']:source_fingerprint(bpy.data.objects[spec['name']]) for group in index['groups'].values() for spec in group['objects']}
# Direct current raw mesh compared to c46, normalize only verified owned deform assignments.
target_data=canonical['objects'][cs.TARGET]['data'];old_data=baseline['objects'][cs.TARGET]['data'];normalized,weight_record=cs.normalize_owned_weights(canonical['meshes'][target_data]);cs.require(normalized==baseline['meshes'][old_data],'Raw original foliage lineage drift')
for key in ('matrix','slots'):cs.require(canonical['objects'][cs.TARGET][key]==baseline['objects'][cs.TARGET][key],'Foliage lineage '+key)
materials={name for _,name in canonical['objects'][cs.TARGET]['slots'] if name}
wood=['V010 | woodland trunks with gate exit clearance']
cs.require(wood,'No retained woodland wood identified')
for n in wood:
 co,bo=canonical['objects'][n],baseline['objects'][n]
 for key in ('matrix','slots'):cs.require(co[key]==bo[key],'Retained wood '+key)
 cs.require(canonical['meshes'][co['data']]==baseline['meshes'][bo['data']],'Retained wood raw lineage')
 cs.require(canonical['visible_evaluated'][n]==baseline['visible_evaluated'][n],'Retained wood evaluation lineage')
 materials.update(mat for _,mat in co['slots'] if mat)
for name in materials:cs.require(canonical['materials'][name]==baseline['materials'][name],'Lineage material '+name)
evidence['lineage']={'raw_target_except_exact_298_owned_weights':weight_record,'wood_objects':wood,'effective_materials':sorted(materials)}
modules={}
evidence['source_index_fingerprints']=source_fingerprints

for mode in ('default','off','high','low'):
 receipt=json.loads(paths[mode+'_receipt'].read_text());cs.require(receipt['output_sha256']==inputs[mode] and receipt['source_sha256']==inputs['source'] and receipt['runtime_sha256']==runtime,'Export receipt identity '+mode)
 load(mode);ui=module(mode);modules[mode]=ui;ui.verify();cs.require(not any(hasattr(bpy.types,n) for n in ui.CLASS_NAMES),'Auto-registration after reopen')
 cs.require(hasattr(ui,'select_index')==(mode!='default'),'Index opt-in behavior');state=snap();normalized=cs.strip_inspection(state,canonical,catalog);normalized=cs.normalize_display(normalized,canonical)
 expected=copy.deepcopy(canonical)
 if mode=='low':
  for name in cs.NEW:expected['visible_evaluated'].pop(name)
  expected['visible_evaluated'][cs.TARGET]=baseline['visible_evaluated'][cs.TARGET]
  record=normalized['visible_evaluated'][cs.TARGET];record['mesh'],evw=cs.normalize_owned_weights(record['mesh'],allow_empty=True);evidence['low_deform_normalization']=evw
 checks={k:normalized[k]==expected[k] for k in expected};cs.require(all(checks.values()),'Mode preservation mismatch '+mode+':'+str([k for k,v in checks.items() if not v]));evidence['modes'][mode]={'category_checks':checks,'category_count':len(checks)}
 marker=json.loads(bpy.context.scene[catalog['marker']]);cs.require(('tree_quality' in marker)==(mode in ('high','low')),'OFF marker behavior')
 if mode in ('high','low'):cs.require(ui.tree_find(bpy.context.scene)[-1]==mode.upper(),'Mode actual flags')
 else:
  cs.require(not hasattr(ui,'tree_set_mode'),'OFF embedded unexpected quality helper');cs.require(flags()==[True,True,False,False,False,False],'OFF must leave canonical HIGH flags unchanged')
 cs.require(ui.register() is True and ui.register() is False,'Registration idempotence')
 for key in catalog['views']:
  ui.select_bookmark(key);before_cam=camera_state()
  if mode in ('high','low'):
   for desired in ('LOW','HIGH',mode.upper()):
    ui.tree_set_mode(bpy.context.scene,desired);cs.require(camera_state()==before_cam,'Tree changes camera state')
    cs.require(ui.tree_set_mode(bpy.context.scene,desired)['changed'] is False,'Same mode not idempotent')
    before_flags=flags();bpy.ops.castle29_inspection.bookmark(view_id=key);cs.require(flags()==before_flags,'Bookmark changes tree state')
   cs.require(bpy.ops.castle29_inspection.tree_quality(mode=mode.upper())=={'FINISHED'},'Native quality operator failed')
 ui.select_bookmark('hero');cs.require(snap()==state,'Repeated mode/bookmark operations drift')
 cs.require(ui.unregister() is True and ui.unregister() is False,'Unregister idempotence')
 load(mode);module(mode).verify();cs.require(snap()==state,'Reopen differs');evidence['modes'][mode]['reopen_and_20_bookmark_interleaving']=True
# Stale OFF/ON runtime identities must refuse even without a registered module.
load('off');reject('stale ON module on OFF copy',modules['high'].register)
load('high');reject('stale OFF module on ON copy',modules['off'].register)
modules['high'].register();reject('stale OFF unregister against ON classes',modules['off'].unregister);modules['high'].unregister()
# Negative fixtures against opt-in HIGH, always restore memory; never save.
load('high');ui=module('high');initial=snap();target=bpy.data.objects[cs.TARGET];mod=target.modifiers[cs.MASK];obj=bpy.data.objects[cs.NEW[0]]
def fixture(label,mutate,restore):
 mutate()
 try:reject(label,lambda:ui.tree_set_mode(bpy.context.scene,'LOW'))
 finally:restore()
fixture('extra owned weight',lambda:target.vertex_groups[cs.GROUP].add([0],1,'REPLACE'),lambda:target.vertex_groups[cs.GROUP].remove([0]))
for field,bad in (('mode','ARMATURE'),('threshold',.25),('invert_vertex_group',False),('use_smooth',True)):
 old=getattr(mod,field);fixture('mask '+field,lambda f=field,b=bad:setattr(mod,f,b),lambda f=field,v=old:setattr(mod,f,v))
fixture('mixed flags',lambda:setattr(obj,'hide_render',True),lambda:setattr(obj,'hide_render',False))
fixture('target render hidden',lambda:setattr(target,'hide_render',True),lambda:setattr(target,'hide_render',False))
fixture('local tree hidden',lambda:obj.hide_set(True),lambda:obj.hide_set(False))
old=obj.name;fixture('wrong authored name',lambda:setattr(obj,'name','QA renamed tree'),lambda:setattr(obj,'name',old))
col=obj.users_collection[0]
for field in ('hide_viewport','hide_render'):
 fixture('ancestor '+field,lambda f=field:setattr(col,f,True),lambda f=field:setattr(col,f,False))
def find_layer(node):
 if node.collection==col:return node
 for child in node.children:
  got=find_layer(child)
  if got:return got
node=find_layer(bpy.context.view_layer.layer_collection)
for field in ('exclude','hide_viewport'):
 fixture('layer '+field,lambda f=field:setattr(node,f,True),lambda f=field:setattr(node,f,False))
# A non-active view layer must not silently defeat HIGH visibility.
secondary=bpy.context.scene.view_layers.new('QA secondary layer');secondary_node=find_layer(secondary.layer_collection)
fixture('non-active layer exclusion',lambda:setattr(secondary_node,'exclude',True),lambda:setattr(secondary_node,'exclude',False));bpy.context.scene.view_layers.remove(secondary)
extra=bpy.data.collections.new('QA multiple path');bpy.context.scene.collection.children.link(extra)
fixture('multiple collection membership',lambda:extra.objects.link(obj),lambda:extra.objects.unlink(obj));bpy.data.collections.remove(extra)
instance=bpy.data.objects.new('QA collection instance',None);bpy.context.scene.collection.objects.link(instance);instance.instance_type='COLLECTION'
fixture('collection instance ghost tree',lambda:setattr(instance,'instance_collection',col),lambda:setattr(instance,'instance_collection',None));bpy.data.objects.remove(instance,do_unlink=True)
# Post-write validation failure injects after flags and marker changed; actual setter must restore all.
original_find=ui.tree_find;calls=[0]
def fail_second(scene):
 calls[0]+=1
 if calls[0]==2:raise RuntimeError('Injected post-write failure')
 return original_find(scene)
ui.tree_find=fail_second
try:reject('post-write atomic rollback',lambda:ui.tree_set_mode(bpy.context.scene,'LOW'))
finally:ui.tree_find=original_find
reject('invalid mode',lambda:ui.tree_set_mode(bpy.context.scene,'NOPE'))
foreign=bpy.data.scenes.new('QA foreign scene');reject('foreign scene',lambda:ui.tree_set_mode(foreign,'LOW'));bpy.data.scenes.remove(foreign)
# Recovery is an ownership operation: invalid scene guards must not strand owned UI classes.
ui.register();obj.hide_set(True)
reject('hidden tree action while registered',lambda:ui.tree_set_mode(bpy.context.scene,'LOW'))
cs.require(ui.unregister() is True,'Owned unregister stranded by hidden tree');obj.hide_set(False)
ui.register();camera=bpy.data.objects[catalog['views']['hero']['camera_name']];old_lens=camera.data.lens;camera.data.lens=old_lens+1
reject('changed camera action while registered',lambda:ui.tree_set_mode(bpy.context.scene,'LOW'))
cs.require(ui.unregister() is True,'Owned unregister stranded by invalid camera');camera.data.lens=old_lens
foreign_registry=types.ModuleType(ui.REGISTRY);foreign_registry.owner='foreign';foreign_registry.catalog_sha256=runtime['catalog.json'];sys.modules[ui.REGISTRY]=foreign_registry
reject('foreign registry registration',ui.register);reject('foreign registry unregister',ui.unregister);del sys.modules[ui.REGISTRY]
cs.require(snap()==initial,'Negative fixture restoration drift')
# Canonical is not a quality-enabled viewer.
load('source');reject('canonical untagged',lambda:ui.tree_set_mode(bpy.context.scene,'LOW'))
cs.require(all(sha(paths[k])==v for k,v in inputs.items()),'Input changed');cs.require(runtime=={n:sha(paths['tool']/n) for n in runtime},'Runtime changed during QA')
evidence.update(pass_=True,input_sha256=inputs,runtime_sha256=runtime,source_saved=False,rendered=False,scope='Linux native background API, not GUI/Windows; single-tree LOW lineage only, not whole-v018 scene. All input files unchanged.')
evidence['pass']=evidence.pop('pass_');paths['report'].write_text(json.dumps(evidence,indent=2));print('INDEPENDENT CURRENT TREE QUALITY PASS')
