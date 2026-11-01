"""Resumable336-frame interior actual-camera sequence with mandatory25frame pilot gate. Dry-run never starts Blender."""
import argparse,datetime,fcntl,json,os,shutil,subprocess,time,uuid
from pathlib import Path
from orbit_common import sha,validate_frame

def write_json(path,value):
 tmp=path.with_name(path.name+'.tmp');tmp.write_text(json.dumps(value,indent=2)+'\n');os.replace(tmp,path)

def no_other_blender():
 active=[]
 for p in Path('/proc').iterdir():
  if p.name.isdigit():
   try:
    if (p/'exe').resolve(strict=True).name.lower().startswith('blender'):active.append(int(p.name))
   except (FileNotFoundError,PermissionError,ProcessLookupError):pass
 if active:raise RuntimeError(f'Other Blender processes present: {active}; refusing overlap')

def main():
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--blender',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--stage',choices=('pilot','full'),required=True);p.add_argument('--approval-file',type=Path);p.add_argument('--dry-run',action='store_true');p.add_argument('--skip-encode',action='store_true');a=p.parse_args()
 root=Path(__file__).resolve().parent;worker=root/'render_final_frame.py';planpath=root/'final_plan.json';plan=json.loads(planpath.read_text());plan_sha=sha(planpath);worker_sha=sha(worker);source=a.source.resolve();out=a.output_dir.resolve()
 assert source.is_file() and sha(source)==plan['source_sha256'];assert a.blender.is_file()
 assert [f['index'] for f in plan['frames']]==list(range(1,337)) and plan['frame_count']==336 and plan['fps']==12 and plan['resolution']==[960,694]
 assert out!=source and source not in out.parents
 identity={'source_sha256':plan['source_sha256'],'plan_sha256':plan_sha,'worker_sha256':worker_sha,'motion_sha256':sha(root/'final_motion.py'),'runner_sha256':sha(Path(__file__)),'validator_sha256':sha(root/'orbit_common.py')}
 if (out/'run_identity.json').exists():assert json.loads((out/'run_identity.json').read_text())==identity,'Existing output belongs to different source/recipe/code; use fresh output'
 indices=plan['pilot_indices'] if a.stage=='pilot' else list(range(1,337))
 assert len(plan['pilot_indices'])==25 and len(set(plan['pilot_indices']))==25
 if a.stage=='full':
  assert a.approval_file and a.approval_file.is_file(),'Full stage needs explicit owner pilot approval receipt'
  approval=json.loads(a.approval_file.read_text())
  assert approval.get('approved') is True and approval.get('identity')==identity,'Pilot approval does not match exact immutable source/plan/code identity'
  assert approval.get('approved_indices')==plan['pilot_indices'],'Approval pose subset mismatch'
  assert (out/'pilot_complete.json').is_file(),'Run pilot first'
  prior=json.loads((out/'pilot_complete.json').read_text());assert prior['identity']==identity
  assert approval.get('pilot_complete_sha256')==sha(out/'pilot_complete.json'),'Pilot approval receipt hash mismatch'
  assert all(validate_frame(out/'frames'/f'frame_{i:04d}',i,plan,plan_sha,worker_sha)['valid'] for i in plan['pilot_indices']),'Pilot frames no longer valid'
 statuses=[validate_frame(out/'frames'/f'frame_{i:04d}',i,plan,plan_sha,worker_sha) for i in indices]
 if a.dry_run:
  print(json.dumps({'dry_run':True,'valid_completed':sum(s['valid'] for s in statuses),'pending':sum(not s['valid'] for s in statuses),'identity':identity,'output_exists':out.exists()},indent=2));return
 assert len(os.sched_getaffinity(0))==9
 out.mkdir(parents=True,exist_ok=True)
 with (out/'runner.lock').open('a') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise RuntimeError('Another runner owns this output')
  no_other_blender()
  if not (out/'run_identity.json').exists():write_json(out/'run_identity.json',identity)
  for name in ('frames','attempts','quarantine'): (out/name).mkdir(exist_ok=True)
  def journal(event,**data):
   with (out/'journal.jsonl').open('a') as f:
    f.write(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'event':event,**data})+'\n');f.flush();os.fsync(f.fileno())
  journal('run_start',identity=identity)
  for i in indices:
   dest=out/'frames'/f'frame_{i:04d}';status=validate_frame(dest,i,plan,plan_sha,worker_sha)
   if status['valid']:journal('skip_verified',**status);continue
   no_other_blender()
   if dest.exists():
    quarantined=out/'quarantine'/f'frame_{i:04d}_{uuid.uuid4().hex}';os.rename(dest,quarantined);journal('quarantined_invalid',index=i,path=str(quarantined),reason=status['reason'])
   attempt=out/'attempts'/f'frame_{i:04d}_{uuid.uuid4().hex}';logpath=attempt.with_suffix('.log')
   cmd=[str(a.blender.resolve()),'-b','--disable-autoexec',str(source),'--python',str(worker),'--','--output-dir',str(attempt),'--index',str(i),'--manifest',str(planpath),'--source-sha',plan['source_sha256']]
   journal('frame_start',index=i,attempt=str(attempt));start=time.perf_counter()
   with logpath.open('w') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
   status=validate_frame(attempt,i,plan,plan_sha,worker_sha)
   if r.returncode or not status['valid']:
    journal('frame_failed',index=i,returncode=r.returncode,validation=status);raise RuntimeError(f'Frame{i} failed; retain attempt, safely retry on resume')
   os.rename(attempt,dest);journal('frame_complete',**status,process_wall_seconds=time.perf_counter()-start)
   print(f'Frame {i}/336 validated: {status["elapsed_render_seconds"]:.2f}s',flush=True)
  if a.stage=='pilot':
   verified=[validate_frame(out/'frames'/f'frame_{i:04d}',i,plan,plan_sha,worker_sha) for i in indices]
   assert all(v['valid'] for v in verified) and sha(source)==plan['source_sha256']
   write_json(out/'pilot_complete.json',{'identity':identity,'frames':verified,'source_sha256_after':sha(source),'stage':'pilot','owner_review_required':True})
   journal('pilot_paused_for_owner_review');print('25 pilot frames verified; STOPPED for owner review. No remaining frames or finalvideo rendered.',flush=True);return
  verified=[validate_frame(out/'frames'/f'frame_{i:04d}',i,plan,plan_sha,worker_sha) for i in range(1,337)]
  assert all(v['valid'] for v in verified);assert sha(source)==plan['source_sha256']
  write_json(out/'frames_complete.json',{'identity':identity,'frames':verified,'source_sha256_after':sha(source),'source_saved':False})
  if not a.skip_encode:
   ffmpeg=shutil.which('ffmpeg');ffprobe=shutil.which('ffprobe');assert ffmpeg and ffprobe
   video=out/'castle_v018_interior_route.mp4';receipt=out/'video.json';frame_set_sha=sha(out/'frames_complete.json')
   valid_video=False
   if video.exists() and receipt.exists():
    old=json.loads(receipt.read_text());valid_video=old.get('video_sha256')==sha(video) and old.get('frames_manifest_sha256')==frame_set_sha
   if not valid_video:
    temp=out/('encode_'+uuid.uuid4().hex+'.mp4')
    cmd=[ffmpeg,'-nostdin','-n','-framerate','12','-start_number','1','-i',str(out/'frames'/'frame_%04d'/'image.png'),'-frames:v','336','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-an','-movflags','+faststart',str(temp)]
    with (out/'encode.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
    probe=json.loads(subprocess.check_output([ffprobe,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(temp)]));streams=probe['streams'];assert len(streams)==1
    v=streams[0];assert v['codec_name']=='h264' and v['pix_fmt']=='yuv420p' and [v['width'],v['height']]==[960,694] and int(v['nb_read_frames'])==336 and v['avg_frame_rate']=='12/1' and abs(float(probe['format']['duration'])-28)<.01
    if video.exists():os.rename(video,out/'quarantine'/('prior_video_'+uuid.uuid4().hex+'.mp4'))
    os.rename(temp,video);write_json(receipt,{'video_sha256':sha(video),'frames_manifest_sha256':frame_set_sha,'probe':probe,'encoding_command':cmd,'no_interpolated_frames':True,'audio':False,'label':'Bounded entrance-to-terrace V018 interior camera route; human-height camera proxy, not articulated human/full-castle accessibility proof'})
   journal('video_verified',video_sha256=sha(video))
  journal('run_complete',source_sha256_after=sha(source));print('All336frames verified; source unchanged.',flush=True)
if __name__=='__main__':main()
