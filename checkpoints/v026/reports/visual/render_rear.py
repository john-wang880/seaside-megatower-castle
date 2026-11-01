"""One fresh-process rear composition discovery render. No model saves."""
import argparse,hashlib,json,os,sys,time
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--source-sha',required=True);p.add_argument('--manifest',required=True);p.add_argument('--output-dir',required=True);p.add_argument('--view',choices=('rear_landward',),required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
 import bpy
 from mathutils import Vector
 import resource
 sys.path.insert(0,str(Path(__file__).resolve().parent))
 from preservation_support import primitive,tree_snapshot,digest
 source=Path(a.source).resolve();out=Path(a.output_dir).resolve();manifest=Path(a.manifest).resolve();manifest_sha=sha(manifest);plan=json.loads(manifest.read_text());r=plan['views'][a.view]
 assert source.is_file() and sha(source)==a.source_sha and not out.exists() and source!=out and not source.is_relative_to(out)
 out.mkdir(parents=False)
 # Fresh empty Blender process; no candidate build or deep preservation snapshot.
 cpu0=time.process_time();start=time.perf_counter();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);load_seconds=time.perf_counter()-start;load_cpu=time.process_time()-cpu0;load_peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
 s=bpy.context.scene;assert s.render.engine=='CYCLES' and s.cycles.device=='CPU' and s.cycles.samples==80 and s.cycles.max_bounces==8 and s.frame_current==plan['source_scene_frame']
 assert s.cycles.use_adaptive_sampling and abs(s.cycles.adaptive_threshold-.035)<1e-7 and s.cycles.adaptive_min_samples==12 and s.cycles.use_denoising and not s.render.use_persistent_data
 original={'cycles':primitive(s.cycles),'view':primitive(s.view_settings),'world_hash':digest(tree_snapshot(s.world.node_tree)),'light_hashes':{l.name:digest({'properties':primitive(l),'nodes':tree_snapshot(l.node_tree)}) for l in bpy.data.lights}}
 if 'existing_camera' in r:
  c=bpy.data.objects[r['existing_camera']];assert c.type=='CAMERA'
 else:
  c=bpy.data.objects.new('READONLY rear discovery',bpy.data.cameras.new('READONLY rear discovery'));s.collection.objects.link(c);c.location=r['location'];c.rotation_euler=(Vector(r['target'])-c.location).to_track_quat('-Z','Y').to_euler()
  for key,value in r['camera_data'].items():setattr(c.data,key,value)
 s.camera=c;bpy.context.view_layer.update()
 assert max(abs(c.matrix_world[i][j]-r['reference_matrix'][i][j]) for i in range(4) for j in range(4))<1e-6
 assert all(getattr(c.data,k)==v for k,v in r['camera_data'].items())
 s.render.resolution_x,s.render.resolution_y=plan['resolution'];s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=8;s.render.filepath=str(out/'image.png');s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8';s.render.image_settings.compression=15;s.render.use_stamp=False
 effective={'render':primitive(s.render),'cycles':primitive(s.cycles),'view':primitive(s.view_settings),'world_hash':original['world_hash'],'light_hashes':original['light_hashes'],'camera':{'matrix_world':[list(v) for v in c.matrix_world],'data':{k:getattr(c.data,k) for k in r['camera_data']}}}
 assert effective['cycles']==original['cycles'] and effective['view']==original['view']
 cpu0=time.process_time();start=time.perf_counter();bpy.ops.render.render(write_still=True);render_seconds=time.perf_counter()-start;render_cpu=time.process_time()-cpu0;peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
 assert sha(source)==a.source_sha and sha(manifest)==manifest_sha and primitive(s.cycles)==original['cycles'] and primitive(s.view_settings)==original['view'] and digest(tree_snapshot(s.world.node_tree))==original['world_hash'] and {l.name:digest({'properties':primitive(l),'nodes':tree_snapshot(l.node_tree)}) for l in bpy.data.lights}==original['light_hashes']
 receipt={'source_filename':source.name,'source_sha256_before':a.source_sha,'source_sha256_after':sha(source),'source_saved':False,'manifest_sha256':manifest_sha,'script_sha256':sha(__file__),'view':a.view,'actual_lighting':True,'blender_version':bpy.app.version_string,'pid':os.getpid(),'settings':effective,'load_wall_seconds':load_seconds,'load_cpu_seconds':load_cpu,'peak_rss_after_load_linux_kib':load_peak,'render_wall_seconds':render_seconds,'render_cpu_seconds':render_cpu,'peak_rss_linux_kib':peak,'image_sha256':sha(out/'image.png'),'measurement_scope':'One fresh process per case; process peak includes scene loading and rendering, not candidate building or prior case. Load timing excludes Blender startup; outer process wall measured separately. Single discovery view, not controlled speed benchmark.'}
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ('view','load_wall_seconds','render_wall_seconds','peak_rss_linux_kib')},indent=2),flush=True)
if __name__=='__main__':main()
