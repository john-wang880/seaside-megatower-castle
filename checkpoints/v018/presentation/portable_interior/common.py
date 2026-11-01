"""Import-safe portable run identity, path and receipt validation."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import uuid
from platform_runtime import require_normal_python, execution_lock_path

ROOT = Path(__file__).resolve().parent
FROZEN = ROOT.parent / 'interior_route'
REPO = ROOT.parents[3]
RUNTIME_FILES = ('run.py', 'worker.py', 'common.py', 'platform_runtime.py', 'frozen_bindings.json')

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def verify_frozen():
    require_normal_python()
    bindings = read_json(ROOT / 'frozen_bindings.json')
    manifest = FROZEN / 'archive_checksums.json'
    require(sha(manifest) == bindings['archive_manifest_sha256'], 'Frozen manifest hash mismatch')
    hashes = read_json(manifest)
    require(len(hashes) == bindings['archive_payload_count'] == 51, 'Frozen payload count mismatch')
    for name, expected in hashes.items():
        path = FROZEN / name
        require(path.resolve().is_relative_to(FROZEN.resolve()), 'Unsafe frozen manifest path')
        require(sha(path) == expected, 'Frozen payload changed: ' + name)
    return bindings

def load_validator():
    # No import-time Pillow or bpy side effects; fail before rendering if missing.
    require_normal_python()
    try:
        import PIL.Image
    except ImportError as exc:
        raise RuntimeError('Pillow is required for PNG validation; install separately, not automatically') from exc
    spec = importlib.util.spec_from_file_location('portable_frozen_validator', FROZEN / 'orbit_common.py')
    module = importlib.util.module_from_spec(spec)
    old = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = old
    return module

def make_identity(source, blender):
    bindings = verify_frozen()
    source, blender = Path(source).resolve(), Path(blender).resolve()
    require(source.is_file() and sha(source) == bindings['source_sha256'], 'Source SHA mismatch')
    require(blender.is_file(), 'Blender executable not found')
    plan = read_json(FROZEN / 'final_plan.json')
    require(plan['frame_count'] == 336 and plan['fps'] == 12 and plan['resolution'] == [960, 694], 'Unexpected plan')
    require([f['index'] for f in plan['frames']] == list(range(1, 337)), 'Frame order mismatch')
    require(len(plan['pilot_indices']) == len(set(plan['pilot_indices'])) == 25, 'Pilot subset mismatch')
    identity = {'schema': 'portable-interior-v1', 'source_sha256': bindings['source_sha256'],
                'plan_sha256': sha(FROZEN / 'final_plan.json'),
                'motion_sha256': sha(FROZEN / 'final_motion.py'),
                'validator_sha256': sha(FROZEN / 'orbit_common.py'),
                'frozen_manifest_sha256': bindings['archive_manifest_sha256'],
                'runtime_sha256': {n: sha(ROOT / n) for n in RUNTIME_FILES},
                'blender_executable_sha256': sha(blender), 'blender_executable': str(blender),
                'expected_blender_version': plan['expected_blender_version'],
                'platform': sys.platform, 'execution_lock': str(execution_lock_path().resolve()),
                'threads': 8}
    return identity, plan

def guard_output(source, output, approval=None):
    source, output = Path(source).resolve(), Path(output).resolve()
    require(not str(output).startswith(('\\\\', '//')), 'UNC/network outputs unsupported')
    require(output != source and not source.is_relative_to(output) and not output.is_relative_to(source),
            'Output must not equal, contain, or be contained in source')
    protected = [ROOT.parent, REPO / 'work/interior_preview_v018/final',
                 REPO / 'work/interior_preview_v018/final_v2', REPO / 'work/orbit_v016/final']
    if approval is not None:
        require(not Path(approval).resolve().is_relative_to(output), 'Approval must be outside output')
    for p in protected:
        p = p.resolve()
        require(not output.is_relative_to(p) and not p.is_relative_to(output), 'Output overlaps protected code/history')
    require(not output.exists() or output.is_dir(), 'Output is not a directory')
    if output.exists() and not (output / 'run_identity.json').is_file():
        require(all(p.name == 'runner.lock' and p.is_file() and not p.is_symlink() for p in output.iterdir()),
                'Refusing nonempty output without recognized run identity')
    return output

def owned_path(output, path):
    output, path = Path(output).resolve(), Path(path)
    require(path.resolve().is_relative_to(output) and path.resolve() != output, 'Path escapes owned output')
    current = path
    while current != output:
        require(not current.is_symlink() and not (hasattr(current, 'is_junction') and current.is_junction()),
                'Redirected output path refused')
        if current.parent == current:
            raise RuntimeError('Output path ancestry mismatch')
        current = current.parent
    return path

def atomic_json(output, path, value):
    path = owned_path(output, path)
    temp = owned_path(output, path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp'))
    with temp.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    os.replace(temp, path)

def validate_frame(output, folder, index, plan, identity, validator):
    try:
        for p in (folder, folder / 'metadata.json', folder / 'image.png'):
            owned_path(output, p)
        receipt = read_json(folder / 'metadata.json')
        require(receipt.get('portable_identity') == identity, 'Frame belongs to another run generation')
        return validator.validate_frame(folder, index, plan, identity['plan_sha256'], identity['runtime_sha256']['worker.py'])
    except (OSError, ValueError, KeyError, RuntimeError, TypeError) as exc:
        return {'valid': False, 'index': index, 'reason': type(exc).__name__ + ': ' + str(exc)}

def check_approval_envelope(output, approval_path, identity, plan):
    require(approval_path is not None and Path(approval_path).is_file(), 'Full stage requires explicit new pilot approval')
    approval = read_json(approval_path)
    require(approval.get('approved') is True and approval.get('identity') == identity, 'Approval identity mismatch')
    require(approval.get('approved_indices') == plan['pilot_indices'], 'Approval pilot subset mismatch')
    complete_path = owned_path(output, output / 'pilot_complete.json')
    complete = read_json(complete_path)
    require(complete.get('identity') == identity, 'Pilot generation mismatch')
    require(approval.get('pilot_complete_sha256') == sha(complete_path), 'Pilot receipt hash mismatch')
    frames = complete.get('frames', [])
    require([f.get('index') for f in frames] == plan['pilot_indices'], 'Pilot receipt indices mismatch')
    for frame in frames:
        require(frame.get('valid') is True, 'Unvalidated pilot receipt entry')
        folder = owned_path(output, output / 'frames' / f"frame_{frame['index']:04d}")
        png = owned_path(output, folder / 'image.png')
        metadata = owned_path(output, folder / 'metadata.json')
        require(sha(png) == frame['png_sha256'] and sha(metadata) == frame['metadata_sha256'],
                'Approved pilot bytes changed')


def authorize_full(output, approval_path, identity, plan, validator):
    check_approval_envelope(output, approval_path, identity, plan)
    require(all(validate_frame(output, output / 'frames' / f'frame_{i:04d}', i, plan, identity, validator)['valid']
                for i in plan['pilot_indices']), 'Pilot frames no longer validate')
