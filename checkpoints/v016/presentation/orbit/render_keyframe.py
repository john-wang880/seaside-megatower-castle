"""Read-only Blender render benchmark worker. Invoked only by run_abba.py."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time
import bpy

p = argparse.ArgumentParser()
p.add_argument('--output-dir', required=True)
p.add_argument('--view', required=True)
p.add_argument('--manifest', required=True)
p.add_argument('--source-sha', required=True)
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
source = Path(bpy.data.filepath).resolve()
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(source) == a.source_sha, 'Unexpected source SHA'
out = Path(a.output_dir).resolve()
assert not out.exists(), 'Refusing reused case output directory'
assert source != out and source not in out.parents
out.mkdir(parents=False)
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
assert manifest['source_sha256'] == a.source_sha
recipe = manifest['views'][a.view]
if 'existing_camera' in recipe:
    c = bpy.data.objects[recipe['existing_camera']]
    assert c.type == 'CAMERA'
else:
    c = bpy.data.objects.new('Contact sheet ' + a.view, bpy.data.cameras.new('Contact sheet ' + a.view))
    s.collection.objects.link(c)
    c.location = recipe['location']
    c.rotation_euler = (Vector(recipe['target']) - c.location).to_track_quat('-Z', 'Y').to_euler()
    c.data.lens = recipe['lens']
    c.data.clip_start = recipe['clip_start']
    c.data.clip_end = recipe['clip_end']
s.camera = c
bpy.context.view_layer.update()
s.render.resolution_x = 640
s.render.resolution_y = 462
s.render.resolution_percentage = 100
s.render.threads_mode = 'FIXED'
s.render.threads = 8
s.render.filepath = str(out / 'image.png')
s.render.image_settings.file_format = 'PNG'
s.render.image_settings.color_mode = 'RGB'
s.render.image_settings.color_depth = '8'
s.render.image_settings.compression = 15
s.render.use_stamp = False
s.cycles.samples = 16  # Explicit low-resolution preview quality only.
quality = properties(s.cycles)
expected_quality = dict(original['cycles']); expected_quality['samples'] = 16
assert quality == expected_quality
camera = {'name': s.camera.name, 'matrix_world': [list(row) for row in s.camera.matrix_world],
          'data': properties(s.camera.data)}
effective = {'cycles': quality, 'render': properties(s.render),
             'image_settings': properties(s.render.image_settings),
             'view_settings': properties(s.view_settings), 'camera': camera,
             'world': s.world.name if s.world else None, 'frame': s.frame_current}
usage_before = resource.getrusage(resource.RUSAGE_SELF)
start = time.perf_counter()
bpy.ops.render.render(write_still=True)
elapsed = time.perf_counter() - start
usage_after = resource.getrusage(resource.RUSAGE_SELF)
assert sha(source) == a.source_sha, 'Source modified'
assert properties(s.cycles) == quality, 'Quality changed'
assert s.render.use_persistent_data == original['render']['use_persistent_data']
report = {'quality_label': '640x462,16-sample feasibility preview; not final quality', 'view': a.view, 'recipe': recipe, 'manifest_sha256_at_start': manifest_sha, 'source': str(source), 'source_sha256_before': a.source_sha,
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
