"""Read-only independent viewer comparison and in-memory operator/negative tests."""
import argparse,bpy,copy,hashlib,importlib.util,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import snapshot_support as ss
p=argparse.ArgumentParser()
for k in ['source','baseline','high','low','controls','report']:p.add_argument('--'+k,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();paths={k:Path(getattr(a,k)).resolve() for k in ['source','baseline','high','low','controls']};hashes={k:sha(v) for k,v in paths.items()};assert hashes['source']=='e71778349c4c65eafbda3eb0a3d0753cd11e1b368a3456c4de1db2f4c0f8647a' and hashes['baseline']=='c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd';assert not Path(a.report).exists()
spec=importlib.util.spec_from_file_location('independent_quality_controls',paths['controls']);q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
def load(k):bpy.ops.wm.open_mainfile(filepath=str(paths[k]),use_scripts=False,load_ui=True)
def snapshot():
 x=ss.snap();x['collections']=ss.collections_snapshot();x['scene_custom']=dict(bpy.context.scene.items());return x
load('baseline');base=snapshot();load('source');canonical=snapshot();checks={};ui=[]
def expect_reject(label,fn):
 try:fn()
 except (RuntimeError,AssertionError):checks[label]=True;return
 raise AssertionError(('Expected rejection',label))
expect_reject('untagged canonical operator refusal',lambda:q.set_mode(bpy.context.scene,'LOW'));assert q.MARKER not in bpy.context.scene
UI={'Traveler | full length ivory skirt','Traveler | purple-red shoulder cape','Traveler | white tunic'}
def evaluated_equal(x,y,label,low_target=False):
 assert set(x)==set(y),(label,'evaluated object set')
 for name in x:
  left,right=copy.deepcopy(x[name]),copy.deepcopy(y[name])
  if name in UI:
   left,lui=ss.render_semantic_with_ui_report(left);right,rui=ss.render_semantic_with_ui_report(right);ui.append({'stage':label,'object':name,'before':lui,'after':rui})
  elif low_target and name==q.TARGET:
   assert left['matrix']==right['matrix'];left=left['mesh']['debug_payload'];right=right['mesh']['debug_payload'];weights=right['weights'];expected=[(i,[(0,1.0)]) for i in sorted(q.SELECTED)]
   assert weights in ([],expected),('Unexpected evaluated deform weights',weights[:2]);checks['low_evaluated_owned_weights_count']=len(weights);right['weights']=[];assert left['weights']==[]
  assert left==right,(label,'evaluated difference',name)
checks['mode_checks']={}
for kind in ['high','low']:
 load(kind);mode=kind.upper();target,mod,objects,tag,actual=q.find(bpy.context.scene);assert actual==mode
 assert set(tag)=={'schema','source_sha256','mode'};assert set(bpy.context.scene.keys())==set(canonical['scene_custom'])|{q.MARKER}
 assert bpy.data.texts[q.TEXT_NAME].as_string()==paths['controls'].read_text() and not bpy.data.texts[q.TEXT_NAME].use_module
 actual_snap=snapshot();normalized=copy.deepcopy(actual_snap)
 normalized['scene_custom'].pop(q.MARKER);normalized['texts']=[row for row in normalized['texts'] if row[0]!=q.TEXT_NAME]
 for name in q.NEW:
  for record in [normalized['objects'][name],normalized['objects'][name]['properties']]:
   for key in ['hide_render','hide_viewport']:record[key]=canonical['objects'][name][key]
 for bucket in [normalized['objects'][q.TARGET]['modifiers'],normalized['objects'][q.TARGET]['properties'].get('modifiers',[])]:
  for m in bucket:
   assert m.get('name')==q.MASK
   for key in ['show_render','show_viewport']:m[key]=True
 expected_persist={k:v for k,v in canonical.items() if k!='visible_evaluated'};actual_persist={k:v for k,v in normalized.items() if k!='visible_evaluated'}
 assert expected_persist==actual_persist,('Persisted original state changed',kind,[k for k in expected_persist if expected_persist[k]!=actual_persist[k]])
 if mode=='HIGH':evaluated_equal(canonical['visible_evaluated'],actual_snap['visible_evaluated'],mode)
 else:
  exp=copy.deepcopy(canonical['visible_evaluated'])
  for name in q.NEW:exp.pop(name)
  exp[q.TARGET]=base['visible_evaluated'][q.TARGET];evaluated_equal(exp,actual_snap['visible_evaluated'],mode,True)
 checks['mode_checks'][mode]={'persisted_source_exact_except_owned_flags_marker_text':True,'evaluated_geometry_equivalence':True}
 before_flags=q.find(bpy.context.scene)[4];assert q.set_mode(bpy.context.scene,mode)['changed']==False
 for desired in ['HIGH','LOW','HIGH',mode]:q.set_mode(bpy.context.scene,desired);assert q.find(bpy.context.scene)[4]==desired;assert q.set_mode(bpy.context.scene,desired)['changed']==False
 q.register();q.register();assert bpy.ops.castle_v019.tree_quality(mode='HIGH')=={'FINISHED'};assert bpy.ops.castle_v019.tree_quality(mode='LOW')=={'FINISHED'};q.unregister();q.unregister();assert not hasattr(bpy.types,'CASTLE_V019_OT_tree_quality') and not hasattr(bpy.types,'CASTLE_V019_PT_tree_quality');checks['registration_operator_'+mode]=True
 # Return original mode and prove repeated controls created no unexpected objects/data.
 q.set_mode(bpy.context.scene,mode);after=snapshot();assert after==actual_snap,('Repeated operations drift',mode)
# In-memory guards on tagged high copy; rejected operations must not alter paired flags/marker.
load('high')
def guard(label,mutate,restore):
 scene=bpy.context.scene;mod=scene.objects[q.TARGET].modifiers[q.MASK];objects=[scene.objects[n] for n in q.NEW];mutate();before=(mod.show_viewport,mod.show_render,[(o.hide_viewport,o.hide_render) for o in objects],scene[q.MARKER]);expect_reject(label,lambda:q.set_mode(scene,'LOW'));after=(mod.show_viewport,mod.show_render,[(o.hide_viewport,o.hide_render) for o in objects],scene[q.MARKER]);assert before==after;restore()
target=bpy.data.objects[q.TARGET];mod=target.modifiers[q.MASK];o=bpy.data.objects[q.NEW[0]]
guard('wrong weights',lambda:target.vertex_groups[q.GROUP].add([0],1,'REPLACE'),lambda:target.vertex_groups[q.GROUP].remove([0]))
guard('mixed flags',lambda:setattr(o,'hide_render',True),lambda:setattr(o,'hide_render',False))
old=o.name;guard('wrong name',lambda:setattr(o,'name','QA wrong name'),lambda:setattr(o,'name',old))
guard('wrong mask mode',lambda:setattr(mod,'mode','ARMATURE'),lambda:setattr(mod,'mode','VERTEX_GROUP'))
guard('hidden original target',lambda:setattr(target,'hide_render',True),lambda:setattr(target,'hide_render',False))
guard('local hidden original target',lambda:target.hide_set(True),lambda:target.hide_set(False))
collection=o.users_collection[0]
guard('hidden parent collection render',lambda:setattr(collection,'hide_render',True),lambda:setattr(collection,'hide_render',False))
guard('hidden parent collection viewport',lambda:setattr(collection,'hide_viewport',True),lambda:setattr(collection,'hide_viewport',False))
def find_layer(node):
 if node.collection==collection:return node
 for child in node.children:
  found=find_layer(child)
  if found:return found
layer_node=find_layer(bpy.context.view_layer.layer_collection);assert layer_node is not None
guard('local hidden parent collection',lambda:setattr(layer_node,'hide_viewport',True),lambda:setattr(layer_node,'hide_viewport',False))
guard('excluded parent collection',lambda:setattr(layer_node,'exclude',True),lambda:setattr(layer_node,'exclude',False))
assert all(sha(paths[k])==v for k,v in hashes.items());r={'pass':True,'validator_sha256':sha(__file__),'snapshot_helper_sha256':sha(Path(__file__).with_name('snapshot_support.py')),'input_sha256':hashes,'checks':checks,'derived_traveler_ui_edges':ui,'all_input_files_unchanged':True,'model_saved':False,'scope':'Background Python/operator and reopened exported-file validation, not actual desktop button interaction. LOW evaluated original canopy equals v018 except explicitly verified owned deform weights; all persisted source fields remain exact. No file-size saving claim.'};Path(a.report).write_text(json.dumps(r,indent=2));print('INDEPENDENT VIEWER QA PASS')
