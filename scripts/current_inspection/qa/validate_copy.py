"""Independent no-save original-state/reopen/manual-API acceptance check."""
import argparse,bpy,sys,json,hashlib,copy,types,importlib.util
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P));import snapshot_support as ss
if sys.flags.optimize:raise RuntimeError('Assertions required')
p=argparse.ArgumentParser()
for k in ['source','viewer','receipt','tool','report']:p.add_argument('--'+k,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);paths={k:Path(getattr(a,k)).resolve()for k in ['source','viewer','receipt','tool','report']};sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert not paths['report'].exists();hashes={k:sha(paths[k])for k in ['source','viewer','receipt']};assert hashes['source']=='89f9f6a8a57103d99100935b96624469ddf1fd52b9703e0d9177a352e735c856';receipt=json.loads(paths['receipt'].read_text());assert receipt['output_sha256']==hashes['viewer']and receipt['source_sha256']==hashes['source'];runtime={n:sha(paths['tool']/n)for n in receipt['runtime_sha256']};assert runtime==receipt['runtime_sha256'];catalog=json.loads((paths['tool']/'catalog.json').read_text());owned=[v['camera_name']for v in catalog['views'].values()if not v['existing']];config={k:catalog[k]for k in ['collection','text','marker','views','source_sha256']};config['catalog_sha256']=sha(paths['tool']/'catalog.json');template=(paths['tool']/'ui_template.py').read_text();expectedcode=template.replace('CONFIG = None  # Exporter replaces this assignment with literal reviewed config.','CONFIG = '+repr(config));ui=types.ModuleType('independent_inspection_ui');exec(compile(expectedcode,'owned-manual-ui','exec'),ui.__dict__)
def load(path):bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=True,use_scripts=False)
def visibility():
 r={}
 def layer(n):return {'name':n.name,'exclude':n.exclude,'hide_viewport':n.hide_viewport,'collection':n.collection.name,'children':[layer(c)for c in n.children]}
 for vl in bpy.context.scene.view_layers:r[vl.name]={'objects':{o.name:{'hide_get':o.hide_get(view_layer=vl),'select_get':o.select_get(view_layer=vl)}for o in vl.objects},'active':vl.objects.active.name if vl.objects.active else None,'layer':layer(vl.layer_collection)}
 return r
def snapshot():
 r=ss.snap();r['collections']=ss.collections_snapshot();r['scene_custom']=dict(bpy.context.scene.items());r['visibility']=visibility()
 for n in ['Traveler | full length ivory skirt','Traveler | purple-red shoulder cape','Traveler | white tunic']:r['visible_evaluated'][n],_=ss.render_semantic_with_ui_report(r['visible_evaluated'][n])
 return r
def reject(label,fn):
 before=bpy.context.scene.camera
 try:fn()
 except (RuntimeError,ValueError,KeyError):assert bpy.context.scene.camera==before;negatives.append(label);return
 raise AssertionError('Expected rejection: '+label)
negatives=[];load(paths['source']);canonical=snapshot();reject('canonical untagged refuses UI',ui.verify);assert not any(hasattr(bpy.types,n)for n in ui.CLASS_NAMES)
# Canonical-source export collision guards refuse all foreign/partial owned names.
sys.path.insert(0,str(paths['tool']));es=importlib.util.spec_from_file_location('independent_exporter',paths['tool']/'export_inspection.py');exporter=importlib.util.module_from_spec(es);es.loader.exec_module(exporter);exporter.collision_check(catalog)
bpy.context.scene[catalog['marker']]='foreign';reject('export marker collision',lambda:exporter.collision_check(catalog));del bpy.context.scene[catalog['marker']]
cc=bpy.data.collections.new(catalog['collection']);reject('export collection collision',lambda:exporter.collision_check(catalog));bpy.data.collections.remove(cc)
tt=bpy.data.texts.new(catalog['text']);reject('export Text collision',lambda:exporter.collision_check(catalog));bpy.data.texts.remove(tt)
oo=bpy.data.objects.new(owned[0],None);reject('export camera object collision',lambda:exporter.collision_check(catalog));bpy.data.objects.remove(oo)
dd=bpy.data.cameras.new(owned[0]+' data');reject('export orphan camera data collision',lambda:exporter.collision_check(catalog));bpy.data.cameras.remove(dd)
assert snapshot()==canonical,'Collision fixtures changed canonical state'
load(paths['viewer']);assert bpy.context.scene.camera.name==catalog['views']['hero']['camera_name'];text=bpy.data.texts[catalog['text']];assert text.as_string()==expectedcode and not text.use_module;assert not any(hasattr(bpy.types,n)for n in ui.CLASS_NAMES),'Auto-registration on disabled reopen';ui.verify();viewer=snapshot();norm=copy.deepcopy(viewer)
assert set(norm['objects'])-set(canonical['objects'])==set(owned);assert set(norm['cameras'])-set(canonical['cameras'])=={n+' data'for n in owned}
for n in owned:norm['objects'].pop(n);norm['cameras'].pop(n+' data')
norm['texts']=[x for x in norm['texts']if x[0]!=catalog['text']];norm['scene_custom'].pop(catalog['marker']);norm['collections']['collections'].pop(catalog['collection']);norm['collections']['root_children'].remove(catalog['collection'])
for vl in norm['visibility'].values():
 for n in owned:vl['objects'].pop(n)
 vl['layer']['children']=[n for n in vl['layer']['children']if n['collection']!=catalog['collection']]
checks={k:norm[k]==canonical[k]for k in canonical};differences={k:[n for n in canonical[k]if canonical[k][n]!=norm[k].get(n)]for k in canonical if isinstance(canonical[k],dict)and not checks[k]};assert all(checks.values()),differences
# Manual registration and complete bookmark roundtrip; no original settings/visibility edits.
assert ui.register()is True and ui.register()is False
for key in catalog['views']:
 result=ui.select_bookmark(key);assert bpy.context.scene.camera.name==catalog['views'][key]['camera_name'];assert ui.select_bookmark(key)==result
 assert bpy.ops.castle24_inspection.bookmark(view_id=key)=={'FINISHED'}
ui.select_bookmark('hero');assert snapshot()==viewer,'Bookmark roundtrip changed non-viewport data'
assert ui.unregister()is True and ui.unregister()is False;assert not any(hasattr(bpy.types,n)for n in ui.CLASS_NAMES)
# Guard fixtures are in-memory and restored; a different chosen key must not bypass ownership.
col=bpy.data.collections[catalog['collection']];cam=bpy.data.objects[owned[0]];oldtag=cam[ui.TAG]
cam[ui.TAG]='foreign';reject('foreign unselected camera owner',lambda:ui.select_bookmark('hero'));cam[ui.TAG]=oldtag
old=cam.data[ui.TAG];cam.data[ui.TAG]='foreign';reject('foreign camera-data owner',lambda:ui.select_bookmark('hero'));cam.data[ui.TAG]=old
col.objects.unlink(cam);reject('partial inventory',lambda:ui.select_bookmark('hero'));col.objects.link(cam)
old=cam.data.lens;cam.data.lens+=1;reject('changed unselected lens',lambda:ui.select_bookmark('hero'));cam.data.lens=old
cam.data.dof.use_dof=True;reject('changed DOF',lambda:ui.select_bookmark('hero'));cam.data.dof.use_dof=False
cam.delta_location.x=.1;reject('changed delta transform',lambda:ui.select_bookmark('hero'));cam.delta_location.x=0
col.hide_render=True;reject('owned parent hidden render',lambda:ui.select_bookmark('hero'));col.hide_render=False
lc=next(c for c in bpy.context.view_layer.layer_collection.children if c.collection==col);lc.exclude=True;reject('owned layer excluded',lambda:ui.select_bookmark('hero'));lc.exclude=False
text.use_module=True;reject('autoexec Text flag',lambda:ui.select_bookmark('hero'));text.use_module=False
reject('unknown bookmark',lambda:ui.select_bookmark('not-a-view'))
foreign=bpy.data.scenes.new('QA foreign scene');reject('foreign context scene',lambda:ui.select_bookmark('hero',types.SimpleNamespace(scene=foreign,view_layer=bpy.context.view_layer)));bpy.data.scenes.remove(foreign)
# Hero's original parent collection visibility must also fail closed.
hero=bpy.data.objects[catalog['views']['hero']['camera_name']];hcols=list(hero.users_collection);saved=[(c,c.hide_render)for c in hcols]
for c,_ in saved:c.hide_render=True
reject('original hero parent render hidden',lambda:ui.select_bookmark('hero'))
for c,v in saved:c.hide_render=v
foreign_registry=types.ModuleType(ui.REGISTRY);foreign_registry.owner='foreign';foreign_registry.catalog_sha256=config['catalog_sha256'];sys.modules[ui.REGISTRY]=foreign_registry
reject('foreign registration registry',ui.register);reject('foreign unregister registry',ui.unregister);del sys.modules[ui.REGISTRY]
ui.verify();assert snapshot()==viewer,'Negative fixture restoration drift'
# Reopen again with scripts disabled; immutable manual copy remains reusable.
load(paths['viewer']);ui.verify();assert snapshot()==viewer
assert all(sha(paths[k])==v for k,v in hashes.items());assert runtime=={n:sha(paths['tool']/n)for n in runtime}
result={'pass':True,'input_sha256':hashes,'runtime_sha256':runtime,'full_source_category_checks':checks,'negative_cases':negatives,'manual_bookmarks_tested':12,'paired_register_unregister_idempotent':True,'reopened_no_auto_registration':True,'source_existing_camera_data_exact':True,'source_visibility_selection_quality_exact':True,'all_inputs_unchanged':True,'scope':'Actual Linux background export/reopen/manualPython and operator API validation, not native Windows or desktop button clicking. UI marker records provenance, not post-edit certification.'};paths['report'].write_text(json.dumps(result,indent=2));print('INDEPENDENT INSPECTION COPY PASS')
