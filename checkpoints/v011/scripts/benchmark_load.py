"""Observed warm-cache load metrics; not a general speed guarantee."""
import argparse,bpy,json,resource,sys,time,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);src=Path(a.model).resolve();start=time.perf_counter();bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);elapsed=time.perf_counter()-start;rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
hash_state=hashlib.sha256()
with src.open('rb') as file:
 for chunk in iter(lambda:file.read(1048576),b''):hash_state.update(chunk)
r={'model':src.name,'sha256':hash_state.hexdigest(),'bytes':src.stat().st_size,'load_seconds':elapsed,'process_peak_rss_kib':rss,'objects':len(bpy.data.objects),'meshes':len(bpy.data.meshes),'visible_polygons':sum(len(o.data.polygons) for o in bpy.data.objects if o.type=='MESH' and not o.hide_render),'hidden_polygons':sum(len(o.data.polygons) for o in bpy.data.objects if o.type=='MESH' and o.hide_render),'runtime':bpy.app.version_string,'scope':'One isolated Blender process, warm filesystem cache; peak captured immediately after load before streaming hash, includes process startup. Concurrent render can affect timing. No render-performance claim.'};Path(a.report).write_text(json.dumps(r,indent=2));print(json.dumps(r))
