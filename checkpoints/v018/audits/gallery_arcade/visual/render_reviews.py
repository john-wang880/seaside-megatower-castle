"""Read-only two-view actual gallery review; explicit preflight before rendering."""
import argparse, hashlib, itertools, json, sys, time, resource
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
from preservation_support import primitive, tree_snapshot, digest
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--output-dir',required=True);p.add_argument('--render',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
src=Path(a.source).resolve();out=Path(a.output_dir).resolve();out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd'
assert sha(src)==expected
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
assert s.cycles.samples==80 and s.cycles.max_bounces==8 and s.render.engine=='CYCLES'
quality=primitive(s.cycles);view=primitive(s.view_settings);world=digest(tree_snapshot(s.world.node_tree));lights={l.name:digest({'properties':primitive(l),'nodes':tree_snapshot(l.node_tree)}) for l in bpy.data.lights}
s.render.resolution_x=1200;s.render.resolution_y=866;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=8;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.use_stamp=False
recipes={
'west_cornice':{'location':[-108,55,144],'target':[-128,86,137.5],'lens':55,'bounds':[[-130,81,133],[-117,87,139]]},
'main_gallery':{'location':[82,-40,82],'target':[35,22,65],'lens':55,'bounds':[[10,8,48],[65,35,80]]}}
prepared=[]
for name,r in recipes.items():
 target=Vector(r['target']);initial=Vector(r['location']);corners=[Vector(v) for v in itertools.product(*zip(*r['bounds']))]
 c=bpy.data.objects.new('READONLY gallery '+name,bpy.data.cameras.new('READONLY gallery '+name));s.collection.objects.link(c);c.data.lens=r['lens'];c.data.clip_start=.1;c.data.clip_end=3000;s.camera=c
 for k in range(21):
  scale=1+k*.05;c.location=target+(initial-target)*scale;c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();projected=[world_to_camera_view(s,c,v) for v in corners]
  if all(.06<=v.x<=.94 and .06<=v.y<=.94 and v.z>0 for v in projected):break
 else:raise RuntimeError('Cannot fit bounded gallery region')
 direction=(target-c.location).normalized();hit,point,normal,face,obj,matrix=s.ray_cast(bpy.context.evaluated_depsgraph_get(),c.location,direction,distance=(target-c.location).length+.5)
 rec={'view':name,'initial_recipe':r,'distance_scale':scale,'location':list(c.location),'target':list(target),'lens':c.data.lens,'matrix':[list(v) for v in c.matrix_world],'target_region_projection':[list(v) for v in projected],'center_ray':{'hit':hit,'object':obj.name if obj else None,'point':list(point) if hit else None,'distance':(point-c.location).length if hit else None,'target_distance':(target-c.location).length},'bounds_scope':'Selected bounded gallery/cornice region only; not whole tower or every connected component.'}
 prepared.append((name,c,rec))
preflight={'source_sha256':expected,'recipes':[r for _,_,r in prepared]}
prepath=out/'preflight.json'
if not a.render:
 assert not prepath.exists();prepath.write_text(json.dumps(preflight,indent=2)+'\n');print(json.dumps(preflight,indent=2))
else:
 assert json.loads(prepath.read_text())==preflight,'Preflight changed; owner review required'
 for name,c,rec in prepared:
  image=out/(name+'.png');receipt=out/(name+'.json');assert not image.exists() and not receipt.exists()
  s.camera=c;s.render.filepath=str(image);bpy.context.view_layer.update()
  settings={'render':primitive(s.render),'cycles':quality,'view':view,'world_hash':world,'light_hashes':lights,'camera':rec}
  start=time.perf_counter();bpy.ops.render.render(write_still=True);elapsed=time.perf_counter()-start
  assert primitive(s.cycles)==quality and primitive(s.view_settings)==view and digest(tree_snapshot(s.world.node_tree))==world
  assert {l.name:digest({'properties':primitive(l),'nodes':tree_snapshot(l.node_tree)}) for l in bpy.data.lights}==lights and sha(src)==expected
  receipt.write_text(json.dumps({'source_sha256_before':expected,'source_sha256_after':sha(src),'source_saved':False,'actual_lighting':True,'settings':settings,'elapsed_render_seconds':elapsed,'peak_rss_linux_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'image_sha256':sha(image)},indent=2)+'\n');print('RENDER PASS',name,elapsed,flush=True)
assert sha(src)==expected
