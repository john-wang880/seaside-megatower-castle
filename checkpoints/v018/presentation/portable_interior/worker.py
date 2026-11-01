"""Portable single-frame worker. Execution lease precedes source loading; never saves source."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (require, sha, make_identity, owned_path, atomic_json, read_json, FROZEN, check_approval_envelope, guard_output)
from platform_runtime import require_normal_python, exclusive_lock, execution_lock_path, optional_metrics

def main(argv=None):
    require_normal_python()
    if argv is None:
        argv = sys.argv[sys.argv.index('--') + 1:]
    p = argparse.ArgumentParser()
    for name in ('source', 'output-dir', 'identity-file', 'identity-sha'):
        p.add_argument('--' + name, required=True)
    p.add_argument('--index', type=int, required=True)
    p.add_argument('--stage', choices=('pilot', 'full'), required=True)
    p.add_argument('--approval-file', type=Path)
    a = p.parse_args(argv)
    # Blender starts with factory defaults, not the model. Own this lease even
    # if the coordinator dies; a replacement worker cannot overlap source load.
    with exclusive_lock(execution_lock_path()):
        import bpy
        source = Path(a.source).resolve()
        identity_path = Path(a.identity_file).resolve()
        require(sha(identity_path) == a.identity_sha, 'Run identity changed before worker start')
        identity = read_json(identity_path)
        actual, manifest = make_identity(source, bpy.app.binary_path)
        require(identity == actual, 'Worker source/code/executable identity mismatch')
        require(1 <= a.index <= 336, 'Invalid frame index')
        run_root = guard_output(source, identity_path.parent, a.approval_file)
        require(identity_path.name == 'run_identity.json', 'Unexpected run identity filename')
        owned_path(run_root, identity_path)
        if a.stage == 'pilot':
            require(a.index in manifest['pilot_indices'], 'Non-pilot frame refused in pilot stage')
        else:
            check_approval_envelope(run_root, a.approval_file, identity, manifest)
        out = owned_path(run_root, Path(a.output_dir).resolve())
        require(out.parent == run_root / 'attempts', 'Worker output must be a unique owned attempt')
        require(not out.exists(), 'Attempt output already exists')
        out.mkdir()
        a.source_sha = identity['source_sha256']
        a.manifest = str(FROZEN / 'final_plan.json')
        bpy.ops.wm.open_mainfile(filepath=str(source), use_scripts=False)
        render_one(bpy, a, source, out, run_root, identity)

def render_one(bpy, a, source, out, run_root, identity):
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
    c.data.sensor_width = manifest['sensor_width_mm']
    c.data.sensor_fit = manifest['sensor_fit']
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
              'data': properties(s.camera.data)}
    effective = {'cycles': quality, 'render': properties(s.render),
                 'image_settings': properties(s.render.image_settings),
                 'view_settings': properties(s.view_settings), 'camera': camera,
                 'world': s.world.name if s.world else None, 'frame': s.frame_current}
    assert effective['view_settings'] == manifest['expected_view_settings']
    assert effective['image_settings'] == manifest['expected_image_settings']
    render_without_path = dict(effective['render']); render_without_path.pop('filepath')
    assert render_without_path == manifest['expected_render_except_filepath']
    near_radius = max((v * (c.data.clip_start / abs(v.z))).length for v in c.data.view_frame(scene=s))
    assert near_radius < manifest['camera_proxy_radius_m']
    cpu_before = time.process_time()
    start = time.perf_counter()
    bpy.ops.render.render(write_still=True)
    elapsed = time.perf_counter() - start
    cpu_after = time.process_time()
    assert sha(source) == a.source_sha, 'Source modified'
    assert properties(s.cycles) == quality, 'Quality changed'
    assert s.render.use_persistent_data == original['render']['use_persistent_data']
    report = {'near_plane_corner_radius_m': near_radius, 'source_scene_frame': s.frame_current, 'index': a.index, 'worker_sha256': sha(Path(__file__)), 'recipe': recipe, 'manifest_sha256_at_start': manifest_sha, 'source': str(source), 'source_sha256_before': a.source_sha,
              'source_sha256_after': sha(source), 'saved_model': False,
              'blender_version': bpy.app.version_string, 'threads': 8,
              **optional_metrics(),
              'elapsed_render_seconds': elapsed,
              'process_cpu_seconds': cpu_after - cpu_before,
              'process_cpu_metric': 'time.process_time delta seconds',
              'portable_identity': identity,
              'original_settings': original, 'effective_settings': effective,
              'png_file_sha256': sha(out / 'image.png')}
    require(make_identity(source, bpy.app.binary_path)[0] == identity, 'Source/code/runtime changed during worker render')
    if a.stage == 'full':
        check_approval_envelope(run_root, a.approval_file, identity, manifest)
    atomic_json(run_root, out / 'metadata.json', report)

if __name__ == '__main__':
    main()
