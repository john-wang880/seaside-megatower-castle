"""Read-only final sequence/encoding QA; no Blender or image modifications."""
import json,subprocess,hashlib,statistics
from pathlib import Path
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parent/'final';video=root/'castle_v016_partial_orbit.mp4';size=960*694*3
proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(video),'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
rows=[];previous=None;hashes=[];brightness=[]
for i in range(1,97):
 chunks=[];remaining=size
 while remaining:
  b=proc.stdout.read(remaining)
  if not b:raise RuntimeError('Truncated decoded frame'+str(i))
  chunks.append(b);remaining-=len(b)
 decoded=np.frombuffer(b''.join(chunks),dtype=np.uint8).reshape(694,960,3)
 with Image.open(root/'frames'/f'frame_{i:04d}'/'image.png') as im:original=np.asarray(im,dtype=np.int16)
 error=np.abs(decoded.astype(np.int16)-original)
 row={'index':i,'encoding_mae_8bit':float(error.mean()),'encoding_max_difference_8bit':int(error.max()),'original_mean_8bit':float(original.mean())}
 if previous is not None:row['previous_frame_mae_8bit']=float(np.abs(original-previous).mean())
 previous=original;rows.append(row);brightness.append(row['original_mean_8bit']);hashes.append(hashlib.sha256(original.tobytes()).hexdigest())
assert proc.stdout.read(1)==b'','Unexpected extra decoded frame'
err=proc.stderr.read().decode();assert proc.wait()==0 and not err,err
frames=json.loads((root/'frames_complete.json').read_text())['frames'];video_receipt=json.loads((root/'video.json').read_text());journal=[json.loads(line) for line in (root/'journal.jsonl').read_text().splitlines()]
from datetime import datetime
start=datetime.fromisoformat(next(e['utc'] for e in journal if e['event']=='run_start'));end=datetime.fromisoformat(journal[-1]['utc'])
report={'video_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'all96_frames_decoded_without_errors':True,'encoded_frame_count':96,'unique_original_frames':len(set(hashes)),'mean_encoding_absolute_channel_difference_8bit':statistics.mean(x['encoding_mae_8bit'] for x in rows),'maximum_mean_brightness_step_8bit':max(abs(a-b) for a,b in zip(brightness,brightness[1:])),'adjacent_frame_mae_range_8bit':[min(x['previous_frame_mae_8bit'] for x in rows[1:]),max(x['previous_frame_mae_8bit'] for x in rows[1:])],'total_render_seconds':sum(f['elapsed_render_seconds'] for f in frames),'run_wall_seconds':(end-start).total_seconds(),'source_sha256_after':json.loads((root/'frames_complete.json').read_text())['source_sha256_after'],'sampled_visual_frames':[1,25,32,49,73,96],'visual_findings':['Both tower roofs and principal coastal rock remain framed in inspected final images.','No cloud/tree occlusion of tower silhouettes in sampled images.','Marker naturally emerges from behind headland; meadow extends offleft,as scoped.','Encoding complete and correct order verified against each corresponding original frame.'],'limits':'No real-time GUI playback tool used. Frame inspection, every-frame decode/source comparison and numeric continuity checks are not a guarantee against subtle temporal denoising shimmer. H264 yuv420p encoding is intentionally lossy.','frames':rows}
(root/'final_qa.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='frames'},indent=2))
