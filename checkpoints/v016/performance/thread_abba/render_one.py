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
p.add_argument('--threads', type=int, choices=(3, 8), required=True)
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
# No camera, quality, seed, adaptive, device, world, lights or exposure changes.
s.render.resolution_x = 720
s.render.resolution_y = 520
s.render.resolution_percentage = 100
s.render.threads_mode = 'FIXED'
s.render.threads = a.threads
s.render.filepath = str(out / 'image.png')
s.render.image_settings.file_format = 'PNG'
s.render.image_settings.color_mode = 'RGB'
s.render.image_settings.color_depth = '8'
s.render.image_settings.compression = 15
s.render.use_stamp = False
quality = properties(s.cycles)
assert quality == original['cycles']
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
report = {'source': str(source), 'source_sha256_before': a.source_sha,
          'source_sha256_after': sha(source), 'saved_model': False,
          'blender_version': bpy.app.version_string, 'threads': a.threads,
          'affinity_logical_cpus': sorted(os.sched_getaffinity(0)),
          'elapsed_render_seconds': elapsed,
          'process_cpu_seconds': (usage_after.ru_utime + usage_after.ru_stime -
                                  usage_before.ru_utime - usage_before.ru_stime),
          'peak_rss_linux_kib': usage_after.ru_maxrss,
          'original_settings': original, 'effective_settings': effective,
          'png_file_sha256': sha(out / 'image.png')}
(out / 'metadata.json').write_text(json.dumps(report, indent=2) + '\n')
