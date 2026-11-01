"""In-memory duplicate collection membership must fail closed without changing flags."""
import argparse,bpy,hashlib,importlib.util,json,sys
from pathlib import Path
p=argparse.ArgumentParser()
for k in ['viewer','controls','report']:p.add_argument('--'+k,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(a.viewer);spec=importlib.util.spec_from_file_location('quality',a.controls);q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q);bpy.ops.wm.open_mainfile(filepath=str(Path(a.viewer).resolve()),use_scripts=False);scene=bpy.context.scene;target,mod,objects,tag,mode=q.find(scene);beforeflags=(mod.show_viewport,mod.show_render,[(o.hide_viewport,o.hide_render) for o in objects],scene[q.MARKER]);coll=bpy.data.collections.new('QA temporary extra membership');scene.collection.children.link(coll);coll.objects.link(objects[0]);bpy.context.view_layer.update();rejected=False;message=None
try:q.set_mode(scene,'LOW')
except RuntimeError as exc:message=str(exc);rejected='exactly one collection path' in message
assert rejected;assert beforeflags==(mod.show_viewport,mod.show_render,[(o.hide_viewport,o.hide_render) for o in objects],scene[q.MARKER]);bpy.data.collections.remove(coll);bpy.context.view_layer.update();assert q.find(scene)[4]==mode;assert sha(a.viewer)==before;Path(a.report).write_text(json.dumps({'pass':True,'viewer_sha256':before,'controls_sha256':sha(a.controls),'expected_rejection':message,'source_unchanged':True,'temporary_collection_removed':True,'model_saved':False},indent=2))
