"""Resumable96-frame actual-camera sequence. Dry-run never starts Blender."""
import argparse,datetime,fcntl,json,os,shutil,subprocess,time,uuid,sys
from runtime_guards import environment,identity as current_identity,recheck,check_source,check_output,check_existing,clean,need
environment()
sys.dont_write_bytecode=True
from pathlib import Path
from orbit_common import sha,validate_frame

def write_json(path,value):
 tmp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(value,indent=2)+'\n');
 with tmp.open('rb')as f:os.fsync(f.fileno())
 os.replace(tmp,path)

def no_other_blender():
 active=[]
 for p in Path('/proc').iterdir():
  if p.name.isdigit():
   try:
    if (p/'exe').resolve(strict=True).name.lower().startswith('blender'):active.append(int(p.name))
   except (FileNotFoundError,PermissionError,ProcessLookupError):pass
 if active:raise RuntimeError(f'Other Blender processes present: {active}; refusing overlap')

def main():
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--blender',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);stage=p.add_mutually_exclusive_group(required=True);stage.add_argument('--pilot-frame',type=int,choices=[49]);stage.add_argument('--full',action='store_true');p.add_argument('--dry-run',action='store_true');p.add_argument('--skip-encode',action='store_true');a=p.parse_args()
 root=Path(__file__).resolve().parent;worker=root/'render_final_frame.py';planpath=root/'final_plan.json';plan=json.loads(planpath.read_text());plan_sha=sha(planpath);worker_sha=sha(worker)
 source=check_source(a.source);out=check_output(source,a.output_dir);blender=clean(a.blender);need(blender.is_file(),'Blender executable missing')
 identity=current_identity();check_existing(out,identity,allow_new_lock=True)
 need([f['index']for f in plan['frames']]==list(range(1,97))and plan['frame_count']==96 and plan['fps']==12 and plan['resolution']==[960,694],'Unexpected sequence')
 statuses=[validate_frame(out/'frames'/f'frame_{i:04d}',i,plan,plan_sha,worker_sha) for i in range(1,97)]
 if a.dry_run:
  print(json.dumps({'dry_run':True,'valid_completed':sum(s['valid'] for s in statuses),'pending':sum(not s['valid'] for s in statuses),'identity':identity,'output_exists':out.exists()},indent=2));return
 need(len(os.sched_getaffinity(0))==9,'Reviewed cloud affinity changed')
 if not a.pilot_frame and not a.skip_encode:need(shutil.which('ffmpeg')and shutil.which('ffprobe'),'Encoding dependencies missing')
 out.mkdir(parents=True,exist_ok=True)
 with (out/'runner.lock').open('a') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise RuntimeError('Another runner owns this output')
  recheck(source,identity);check_output(source,out);check_existing(out,identity,allow_new_lock=True)
  no_other_blender()
  if not (out/'run_identity.json').exists():write_json(out/'run_identity.json',identity)
  for name in ('frames','attempts','quarantine'): (out/name).mkdir(exist_ok=True)
  def journal(event,**data):
   with (out/'journal.jsonl').open('a') as f:
    f.write(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'event':event,**data})+'\n');f.flush();os.fsync(f.fileno())
  journal('run_start',identity=identity)
  selected=[49]if a.pilot_frame else list(range(1,97))
  for i in selected:
   recheck(source,identity);check_existing(out,identity);check_output(source,out)
   dest=out/'frames'/f'frame_{i:04d}';status=validate_frame(dest,i,plan,plan_sha,worker_sha)
   if status['valid']:journal('skip_verified',**status);continue
   no_other_blender()
   if dest.exists():
    quarantined=out/'quarantine'/f'frame_{i:04d}_{uuid.uuid4().hex}';os.rename(dest,quarantined);journal('quarantined_invalid',index=i,path=str(quarantined),reason=status['reason'])
   attempt=out/'attempts'/f'frame_{i:04d}_{uuid.uuid4().hex}';logpath=attempt.with_suffix('.log')
   cmd=[str(blender),'-b','--factory-startup','--disable-autoexec','--python-exit-code','1','--python-expr','import sys; sys.dont_write_bytecode=True','--python',str(worker),'--','--source',str(source),'--identity-file',str(out/'run_identity.json'),'--output-dir',str(attempt),'--index',str(i),'--manifest',str(planpath),'--source-sha',plan['source_sha256']]
   journal('frame_start',index=i,attempt=str(attempt));start=time.perf_counter()
   with logpath.open('w') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
   recheck(source,identity);check_existing(out,identity)
   status=validate_frame(attempt,i,plan,plan_sha,worker_sha)
   if r.returncode or not status['valid']:
    journal('frame_failed',index=i,returncode=r.returncode,validation=status);raise RuntimeError(f'Frame{i} failed; retain attempt, safely retry on resume')
   os.rename(attempt,dest);journal('frame_complete',**status,process_wall_seconds=time.perf_counter()-start)
   print(f'Frame {i}/96 validated: {status["elapsed_render_seconds"]:.2f}s',flush=True)
  if a.pilot_frame:
   recheck(source,identity);verified=validate_frame(out/'frames'/'frame_0049',49,plan,plan_sha,worker_sha);need(verified['valid'],'Pilot did not verify')
   write_json(out/'pilot_frame49.json',{'identity':identity,'frame':verified,'full_render_complete':False,'encoding_performed':False});journal('pilot_frame_verified',index=49);print('Pilot49 verified; stopped without full manifest or encoding.',flush=True);return
  verified=[validate_frame(out/'frames'/f'frame_{i:04d}',i,plan,plan_sha,worker_sha) for i in range(1,97)]
  assert all(v['valid'] for v in verified);assert sha(source)==plan['source_sha256']
  write_json(out/'frames_complete.json',{'identity':identity,'frames':verified,'source_sha256_after':sha(source),'source_saved':False})
  if not a.skip_encode:
   ffmpeg=shutil.which('ffmpeg');ffprobe=shutil.which('ffprobe');assert ffmpeg and ffprobe
   video=out/'castle_v026_partial_orbit.mp4';receipt=out/'video.json';frame_set_sha=sha(out/'frames_complete.json')
   valid_video=False
   if video.exists() and receipt.exists():
    old=json.loads(receipt.read_text());valid_video=old.get('video_sha256')==sha(video) and old.get('frames_manifest_sha256')==frame_set_sha
   if not valid_video:
    temp=out/('encode_'+uuid.uuid4().hex+'.mp4')
    cmd=[ffmpeg,'-nostdin','-n','-framerate','12','-start_number','1','-i',str(out/'frames'/'frame_%04d'/'image.png'),'-frames:v','96','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-an','-movflags','+faststart',str(temp)]
    with (out/'encode.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
    probe=json.loads(subprocess.check_output([ffprobe,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(temp)]));streams=probe['streams'];assert len(streams)==1
    v=streams[0];assert v['codec_name']=='h264' and v['pix_fmt']=='yuv420p' and [v['width'],v['height']]==[960,694] and int(v['nb_read_frames'])==96 and v['avg_frame_rate']=='12/1' and abs(float(probe['format']['duration'])-8)<.01
    pts=json.loads(subprocess.check_output([ffprobe,'-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(temp)]))['frames']
    need(len(pts)==96 and all(abs(float(f['best_effort_timestamp_time'])-i/12)<1e-5 for i,f in enumerate(pts)),'Encoded PTS sequence mismatch')
    need(v.get('codec_type')=='video','Unexpected stream type')
    subprocess.run([ffmpeg,'-nostdin','-v','error','-xerror','-err_detect','explode','-i',str(temp),'-f','null','-'],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    recheck(source,identity);check_existing(out,identity)
    if video.exists():os.rename(video,out/'quarantine'/('prior_video_'+uuid.uuid4().hex+'.mp4'))
    os.rename(temp,video);write_json(receipt,{'video_sha256':sha(video),'frames_manifest_sha256':frame_set_sha,'probe':probe,'encoding_command':cmd,'no_interpolated_frames':True,'audio':False,'strict_decode_passed':True,'exact_96_pts_at_12fps':True,'label':'40 degree partial exterior orbit; actual V026 Blender renders, not360 and not a walkthrough'})
   journal('video_verified',video_sha256=sha(video))
  recheck(source,identity);check_existing(out,identity)
  journal('run_complete',source_sha256_after=sha(source));print('All96frames verified; source unchanged.',flush=True)
if __name__=='__main__':main()
