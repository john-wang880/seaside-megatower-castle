import bpy,sys,json,hashlib,copy
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P));import snapshot_support as ss
from common import inputs,sha
a,s,c,report_path,plan=inputs();input_hashes={'source':sha(s),'candidate':sha(c)}
def ev():
 r=ss.snap()['visible_evaluated']
 for n in ['Traveler | full length ivory skirt','Traveler | purple-red shoulder cape','Traveler | white tunic']:r[n],_=ss.render_semantic_with_ui_report(r[n])
 return r
bpy.ops.wm.open_mainfile(filepath=str(s),use_scripts=False);baseline=ev()
bpy.ops.wm.open_mainfile(filepath=str(c),use_scripts=False);active=ev();non=copy.deepcopy(active)
mods=[]
for sp in plan['pairs']:
 non.pop(sp['union_object']);non.pop(sp['target']);baseline.pop(sp['target'])
 o=bpy.data.objects[sp['union_object']];assert not o.constraints and not o.parent and not o.animation_data and not o.data.shape_keys and not o.hide_get()
 m=bpy.data.objects[sp['target']].modifiers[0];props=ss.primitive(m)
 # Native control on temporary object, no persistent changes.
 me=bpy.data.meshes.new('qa control');ob=bpy.data.objects.new('qa control',me);ob.vertex_groups.new(name=sp['group']);ref=ob.modifiers.new(m.name,'MASK');ref.vertex_group=sp['group'];ref.invert_vertex_group=True;ref.threshold=.5;ref.use_smooth=False
 expected=ss.primitive(ref);diff={k:[props[k],expected.get(k)]for k in props if props[k]!=expected.get(k)}
 assert set(diff)<= {'persistent_uid','execution_time'},diff
 mods.append({'name':m.name,'properties':props,'native_control_runtime_differences':diff});bpy.data.objects.remove(ob);bpy.data.meshes.remove(me)
assert non==baseline,'Non-target active evaluator drift'
for _ in range(2):
 for enabled in [False,True]:
  for sp in plan['pairs']:
   m=bpy.data.objects[sp['target']].modifiers[0];m.show_viewport=m.show_render=enabled;o=bpy.data.objects[sp['union_object']];o.hide_viewport=o.hide_render=not enabled
  bpy.context.view_layer.update()
assert ev()==active,'Repeated HIGH/LOW/HIGH altered evaluation'
report_path.write_text(json.dumps({'pass':True,'candidate_sha256':hashlib.sha256(c.read_bytes()).hexdigest(),'active_non_target_evaluated_exact':True,'repeated_high_low_high_exact':True,'modifier_native_comparisons':mods},indent=2));print('STATE PASS')

assert sha(s)==input_hashes['source'] and sha(c)==input_hashes['candidate']
