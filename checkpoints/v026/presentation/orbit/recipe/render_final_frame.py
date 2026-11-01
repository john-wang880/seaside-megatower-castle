"""One actual orbit frame in a fresh Blender process; never saves source."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from runtime_guards import environment,identity,recheck,check_source,check_output,clean,need,execution_lease_path
environment()
import fcntl
import bpy

p = argparse.ArgumentParser()
p.add_argument('--output-dir', required=True)
p.add_argument('--index', type=int, required=True)
p.add_argument('--manifest', required=True)
p.add_argument('--source-sha', required=True)
p.add_argument('--source',required=True)
p.add_argument('--identity-file',required=True)
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
identity_file=clean(a.identity_file);need(identity_file.name=='run_identity.json','Wrong identity filename')
runroot=identity_file.parent;source=check_source(a.source);check_output(source,runroot)
expected=json.loads(identity_file.read_text());need(expected==identity(),'Wrong run identity')
manifest_path=clean(a.manifest);need(manifest_path==Path(__file__).resolve().parent/'final_plan.json','Wrong manifest path')
out=clean(a.output_dir);need(out.parent==runroot/'attempts'and not out.exists(),'Worker output must be a fresh owned attempt')
# Stable per-user configured-cache lease survives coordinator death and covers
# cooperating output roots, not unrelated manual Blender/different cache namespaces.
lease=execution_lease_path();need(lease.parent.parent.is_dir(),'Configured cache directory must exist');lease.parent.mkdir(exist_ok=True);clean(lease)
execution_lock=lease.open('a')
try:fcntl.flock(execution_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError:raise RuntimeError('Another cooperating frame worker owns the configured per-user execution lease')
recheck(source,expected)
need(not bpy.data.filepath,'Factory-empty startup required before source open')
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
need(a.source_sha==expected['source_sha256'],'Unexpected --source-sha')
out.mkdir(parents=False)
from lighting_snapshot import primitive,tree_snapshot,digest
def lightstate():
 s=bpy.context.scene
 return {'world':{'name':s.world.name,'properties':primitive(s.world),'nodes':tree_snapshot(s.world.node_tree)},'lights':{o.name:{'object':primitive(o),'matrix':[list(r)for r in o.matrix_world],'data':primitive(o.data),'nodes':tree_snapshot(o.data.node_tree)if o.data.use_nodes else None}for o in s.objects if o.type=='LIGHT'}}
lighting_before=digest(lightstate())
s = bpy.context.scene
assert s.render.engine == 'CYCLES' and s.cycles.device == 'CPU'
assert (s.cycles.samples, s.cycles.adaptive_min_samples, s.cycles.max_bounces) == (80, 12, 8)
assert s.render.threads_mode == 'FIXED' and s.render.threads == 3
assert abs(s.cycles.adaptive_threshold - 0.035) < 1e-7
assert s.cycles.use_adaptive_sampling and s.cycles.use_denoising
assert s.camera is not None

def properties(obj):
    result = {}
    for prop in obj.bl_rna.properties:
        if prop.identifier == 'rna_type':
            continue
        if prop.type in {'BOOLEAN', 'INT', 'FLOAT', 'STRING', 'ENUM'}:
            value = getattr(obj, prop.identifier)
            if getattr(prop, 'is_array', False):
                value = list(value)
            elif isinstance(value, set):
                value = sorted(value)
            result[prop.identifier] = value
    return result

original = {'cycles': properties(s.cycles), 'render': properties(s.render),
            'image_settings': properties(s.render.image_settings)}
# Camera-only review. Quality, cache, seed, world, lights and exposure unchanged.
from mathutils import Vector
manifest_bytes = Path(a.manifest).read_bytes()
manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
manifest = json.loads(manifest_bytes)
assert bpy.app.version_string == manifest['expected_blender_version']
assert manifest['source_sha256'] == a.source_sha
need(lighting_before==manifest['expected_lighting_state_sha256'],'Original world/light signature mismatch')
assert s.frame_current == manifest['source_scene_frame'] == 1
recipe = manifest['frames'][a.index-1]['recipe']
assert manifest['frames'][a.index-1]['index'] == a.index
assert original['cycles'] == manifest['expected_cycles']
if 'existing_camera' in recipe:
    c = bpy.data.objects[recipe['existing_camera']]
    assert c.type == 'CAMERA'
else:
    c = bpy.data.objects.new('Orbit frame camera', bpy.data.cameras.new('Orbit frame camera'))
    s.collection.objects.link(c)
    c.location = recipe['location']
    c.rotation_euler = (Vector(recipe['target']) - c.location).to_track_quat('-Z', 'Y').to_euler()
    c.data.lens = recipe['lens']
    c.data.clip_start = recipe['clip_start']
    c.data.clip_end = recipe['clip_end']
s.camera = c
bpy.context.view_layer.update()
s.render.resolution_x = 960
s.render.resolution_y = 694
s.render.resolution_percentage = 100
s.render.threads_mode = 'FIXED'
s.render.threads = 8
s.render.filepath = str(out / 'image.png')
s.render.image_settings.file_format = 'PNG'
s.render.image_settings.color_mode = 'RGB'
s.render.image_settings.color_depth = '8'
s.render.image_settings.compression = 15
s.render.use_stamp = False
quality = properties(s.cycles)
assert quality == original['cycles']
camera = {'name': s.camera.name, 'matrix_world': [list(row) for row in s.camera.matrix_world],
          'data': properties(s.camera.data),'use_dof':s.camera.data.dof.use_dof}
projection={k:(camera['use_dof']if k=='use_dof'else camera['data'][k])for k in manifest['expected_camera_projection']}
need(projection==manifest['expected_camera_projection'],'Camera projection/DOF changed')
effective = {'cycles': quality, 'render': properties(s.render),
             'image_settings': properties(s.render.image_settings),
             'view_settings': properties(s.view_settings), 'camera': camera,
             'world': s.world.name if s.world else None, 'frame': s.frame_current}
assert effective['view_settings'] == manifest['expected_view_settings']
assert effective['image_settings'] == manifest['expected_image_settings']
render_without_path = dict(effective['render']); render_without_path.pop('filepath')
assert render_without_path == manifest['expected_render_except_filepath']
recheck(source,expected)
usage_before = resource.getrusage(resource.RUSAGE_SELF)
start = time.perf_counter()
bpy.ops.render.render(write_still=True)
elapsed = time.perf_counter() - start
usage_after = resource.getrusage(resource.RUSAGE_SELF)
assert sha(source) == a.source_sha, 'Source modified'
assert properties(s.cycles) == quality, 'Quality changed'
assert s.render.use_persistent_data == original['render']['use_persistent_data']
recheck(source,expected)
need(json.loads(identity_file.read_text())==expected,'Run identity changed during frame')
lighting_after=digest(lightstate());need(lighting_after==lighting_before,'World/light state changed during frame')
need(properties(s.view_settings)==effective['view_settings']and properties(s.render)==effective['render']and properties(s.render.image_settings)==effective['image_settings'],'Exposure/render settings changed during frame')
need({'name':s.camera.name,'matrix_world':[list(row)for row in s.camera.matrix_world],'data':properties(s.camera.data),'use_dof':s.camera.data.dof.use_dof}==camera,'Camera changed during frame')
report = {'lighting_state_sha256_before':lighting_before,'lighting_state_sha256_after':lighting_after,'runtime_identity_before':expected,'runtime_identity_after':identity(),'index': a.index, 'worker_sha256': sha(Path(__file__)), 'recipe': recipe, 'manifest_sha256_at_start': manifest_sha, 'source': str(source), 'source_sha256_before': a.source_sha,
          'source_sha256_after': sha(source), 'saved_model': False,
          'blender_version': bpy.app.version_string, 'threads': 8,
          'affinity_logical_cpus': sorted(os.sched_getaffinity(0)),
          'elapsed_render_seconds': elapsed,
          'process_cpu_seconds': (usage_after.ru_utime + usage_after.ru_stime -
                                  usage_before.ru_utime - usage_before.ru_stime),
          'peak_rss_linux_kib': usage_after.ru_maxrss,
          'original_settings': original, 'effective_settings': effective,
          'png_file_sha256': sha(out / 'image.png')}
(out / 'metadata.json').write_text(json.dumps(report, indent=2) + '\n')
