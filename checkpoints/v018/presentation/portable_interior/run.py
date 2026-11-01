"""Opt-in portable interior renderer: new identity, mandatory fresh 25-frame pilot."""
import argparse
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid
from common import (ROOT, FROZEN, require, sha, read_json, make_identity, guard_output,
                    owned_path, atomic_json, load_validator, validate_frame, authorize_full)
from platform_runtime import require_normal_python, exclusive_lock, execution_lock_path

def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'blender', 'output-dir'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--stage', choices=('pilot', 'full'), required=True)
    p.add_argument('--approval-file', type=Path)
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--max-new-frames', type=int, help='Stop after this many new valid frames; never bypass pilot completion')
    p.add_argument('--encode', action='store_true', help='Explicitly encode only after full validation; otherwise keep PNGs')
    p.add_argument('--ffmpeg', type=Path)
    p.add_argument('--ffprobe', type=Path)
    a = p.parse_args(argv)
    if a.max_new_frames is not None and a.max_new_frames < 1:
        p.error('--max-new-frames must be positive')
    if a.encode and a.stage != 'full':
        p.error('--encode requires full stage and pilot approval')
    return a

def tool_path(explicit, name):
    candidate = str(explicit.resolve()) if explicit else shutil.which(name)
    require(candidate is not None and Path(candidate).is_file(), name + ' unavailable; no auto-install')
    return candidate

def check_existing(out, identity):
    p = owned_path(out, out / 'run_identity.json')
    if p.exists():
        require(read_json(p) == identity, 'Output belongs to different identity; use a fresh directory')

def worker_command(a, attempt, out):
    command = [str(a.blender.resolve()), '--background', '--factory-startup', '--disable-autoexec',
            '--python-exit-code', '1', '--python', str(ROOT / 'worker.py'), '--',
            '--source', str(a.source.resolve()), '--output-dir', str(attempt),
            '--index', str(a.current_index), '--identity-file', str(out / 'run_identity.json'),
            '--identity-sha', sha(out / 'run_identity.json'), '--stage', a.stage]
    if a.approval_file is not None:
        command += ['--approval-file', str(a.approval_file.resolve())]
    return command

def check_boundary(a, out, identity, plan, validator):
    guard_output(a.source, out, a.approval_file)
    current, current_plan = make_identity(a.source, a.blender)
    require(current == identity and current_plan == plan, 'Source/code/runtime changed during run; stop')
    check_existing(out, identity)
    if a.stage == 'full':
        authorize_full(out, a.approval_file, identity, plan, validator)

def validate_video_probe(probe, frame_probe):
    require(len(probe['streams']) == 1, 'Unexpected video/audio streams')
    v = probe['streams'][0]
    require(v.get('codec_type') == 'video' and v['codec_name'] == 'h264' and v['pix_fmt'] == 'yuv420p' and
            [v['width'], v['height']] == [960, 694] and int(v['nb_read_frames']) == 336 and
            v['avg_frame_rate'] == '12/1' and abs(float(probe['format']['duration']) - 28) < .01,
            'Encoded video does not match plan')
    pts = [float(f['best_effort_timestamp_time']) for f in frame_probe['frames']]
    require(len(pts) == 336 and all(abs(t - i / 12) <= 1e-6 for i, t in enumerate(pts)),
            'Encoded frame timestamp sequence mismatch')
    return pts

def encode(a, out, frames_path, journal):
    ffmpeg, ffprobe = tool_path(a.ffmpeg, 'ffmpeg'), tool_path(a.ffprobe, 'ffprobe')
    with exclusive_lock(execution_lock_path()):
        video = owned_path(out, out / 'castle_v018_portable_interior.mp4')
        receipt = owned_path(out, out / 'video.json')
        frame_sha = sha(frames_path)
        if video.exists() and receipt.exists():
            prior = read_json(receipt)
            if prior.get('video_sha256') == sha(video) and prior.get('frames_manifest_sha256') == frame_sha:
                journal('skip_verified_video', video_sha256=sha(video)); return
        temp = owned_path(out, out / ('encode_' + uuid.uuid4().hex + '.mp4'))
        command = [ffmpeg, '-nostdin', '-n', '-framerate', '12', '-start_number', '1', '-i',
                   str(out / 'frames/frame_%04d/image.png'), '-frames:v', '336', '-c:v', 'libx264',
                   '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-an', '-movflags', '+faststart', str(temp)]
        logpath = owned_path(out, out / ('encode_' + uuid.uuid4().hex + '.log'))
        with logpath.open('x') as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
        probe = json.loads(subprocess.check_output([ffprobe, '-v', 'error', '-count_frames', '-show_streams',
                                                   '-show_format', '-of', 'json', str(temp)], text=True))
        frame_probe = json.loads(subprocess.check_output([ffprobe, '-v', 'error', '-select_streams', 'v:0',
                    '-show_frames', '-show_entries', 'frame=best_effort_timestamp_time', '-of', 'json', str(temp)], text=True))
        pts = validate_video_probe(probe, frame_probe)
        subprocess.run([ffmpeg, '-v', 'error', '-xerror', '-err_detect', 'explode', '-i', str(temp), '-f', 'null', '-'], check=True)
        if video.exists():
            os.rename(video, owned_path(out, out / 'quarantine' / ('prior_video_' + uuid.uuid4().hex + '.mp4')))
        os.rename(temp, video)
        atomic_json(out, receipt, {'video_sha256': sha(video), 'frames_manifest_sha256': frame_sha,
                                  'probe': probe, 'frame_pts_seconds': pts, 'encoding_command': command,
                                  'ffmpeg_version': subprocess.check_output([ffmpeg, '-version'], text=True).splitlines()[0],
                                  'ffprobe_version': subprocess.check_output([ffprobe, '-version'], text=True).splitlines()[0],
                                  'decode_passed': True, 'no_interpolated_frames': True, 'audio': False})
        journal('video_verified', video_sha256=sha(video))

def main(argv=None):
    require_normal_python()
    a = parse_args(argv)
    out = guard_output(a.source, a.output_dir, a.approval_file)
    identity, plan = make_identity(a.source, a.blender)
    validator = load_validator()
    check_existing(out, identity)
    if a.encode:
        tool_path(a.ffmpeg, 'ffmpeg'); tool_path(a.ffprobe, 'ffprobe')
    if a.stage == 'full':
        authorize_full(out, a.approval_file, identity, plan, validator)
    indices = plan['pilot_indices'] if a.stage == 'pilot' else list(range(1, 337))
    if a.dry_run:
        statuses = [validate_frame(out, out / 'frames' / f'frame_{i:04d}', i, plan, identity, validator) for i in indices]
        print(json.dumps({'dry_run': True, 'identity': identity, 'valid_completed': sum(s['valid'] for s in statuses),
                          'pending': sum(not s['valid'] for s in statuses), 'max_new_frames': a.max_new_frames}, indent=2))
        return
    out.mkdir(parents=True, exist_ok=True)
    with exclusive_lock(owned_path(out, out / 'runner.lock')):
        # Authoritative revalidation AFTER lease; earlier checks are advisory.
        check_boundary(a, out, identity, plan, validator)
        # Refuse an orphan/cooperating worker already busy, without disturbing attempts.
        with exclusive_lock(execution_lock_path()):
            pass
        if not (out / 'run_identity.json').exists():
            atomic_json(out, out / 'run_identity.json', identity)
        for name in ('frames', 'attempts', 'quarantine'):
            owned_path(out, out / name).mkdir(exist_ok=True)
        def journal(event, **data):
            with owned_path(out, out / 'journal.jsonl').open('a', encoding='utf-8') as f:
                f.write(json.dumps({'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                    'event': event, **data}) + '\n'); f.flush(); os.fsync(f.fileno())
        journal('run_start', stage=a.stage, identity=identity, max_new_frames=a.max_new_frames)
        newly_completed = 0
        for index in indices:
            check_boundary(a, out, identity, plan, validator)
            dest = owned_path(out, out / 'frames' / f'frame_{index:04d}')
            status = validate_frame(out, dest, index, plan, identity, validator)
            if status['valid']:
                journal('skip_verified', **status); continue
            if a.max_new_frames is not None and newly_completed >= a.max_new_frames:
                journal('frame_budget_paused', newly_completed=newly_completed)
                print('Frame budget reached; partial pilot/full run retained, no new completion receipt.', flush=True)
                return
            with exclusive_lock(execution_lock_path()):
                pass
            if dest.exists():
                quarantine = owned_path(out, out / 'quarantine' / (f'frame_{index:04d}_' + uuid.uuid4().hex))
                os.rename(dest, quarantine)
                journal('quarantined_invalid', index=index, path=str(quarantine), reason=status['reason'])
            attempt = owned_path(out, out / 'attempts' / (f'frame_{index:04d}_' + uuid.uuid4().hex))
            logpath = owned_path(out, attempt.with_suffix('.log'))
            a.current_index = index
            command = worker_command(a, attempt, out)
            journal('frame_start', index=index, attempt=str(attempt), command=command)
            with logpath.open('x') as log:
                child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
                try:
                    code = child.wait()
                except BaseException:
                    # Only our own direct child; do not terminate unrelated Blender.
                    child.terminate(); child.wait(); raise
            status = validate_frame(out, attempt, index, plan, identity, validator)
            check_boundary(a, out, identity, plan, validator)
            if code or not status['valid']:
                journal('frame_failed', index=index, returncode=code, validation=status)
                raise RuntimeError('Frame failed; attempt/log preserved for inspection')
            require(not dest.exists(), 'Destination appeared unexpectedly; refusing overwrite')
            os.rename(attempt, dest)
            newly_completed += 1
            journal('frame_complete', **status)
            print(f'Frame {index}/336 validated', flush=True)
        check_boundary(a, out, identity, plan, validator)
        verified = [validate_frame(out, out / 'frames' / f'frame_{i:04d}', i, plan, identity, validator) for i in indices]
        require(all(s['valid'] for s in verified), 'Final frame verification failed')
        result = {'identity': identity, 'frames': verified, 'source_sha256_after': sha(a.source), 'source_saved': False}
        if a.stage == 'pilot':
            result.update(stage='pilot', owner_review_required=True)
            atomic_json(out, out / 'pilot_complete.json', result)
            journal('pilot_paused_for_owner_review')
            print('All 25 pilot frames verified; STOP for new owner approval.', flush=True)
            return
        frames_path = out / 'frames_complete.json'
        atomic_json(out, frames_path, result)
        if a.encode:
            encode(a, out, frames_path, journal)
        check_boundary(a, out, identity, plan, validator)
        journal('run_complete', source_sha256_after=sha(a.source), encoded=a.encode)
        print('All 336 frames verified; source unchanged.', flush=True)

if __name__ == '__main__':
    main()
