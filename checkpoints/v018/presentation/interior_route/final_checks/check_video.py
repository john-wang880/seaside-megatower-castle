"""Decode existing approved video read-only; never encode. Full run required."""
import argparse,hashlib,json,subprocess,math
from pathlib import Path
from fractions import Fraction
import numpy as np
from PIL import Image
from qa_utils import validate_timestamps,compression_acceptable,classify_duplicate
p=argparse.ArgumentParser()
for k in ['output','video','frames-report','report']:p.add_argument('--'+k,required=True)
a=p.parse_args();out=Path(a.output);video=Path(a.video);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
f=json.loads(Path(a.frames_report).read_text());assert f['pass'] and len(f['frames'])==336
assert f['frames_complete_sha256']==sha(out/'frames_complete.json')
r=json.loads((out/'video.json').read_text());assert r['video_sha256']==sha(video) and r['frames_manifest_sha256']==f['frames_complete_sha256'] and r['audio'] is False
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-show_frames','-of','json',str(video)]));assert len(probe['streams'])==1
v=probe['streams'][0];assert v['codec_type']=='video' and v['codec_name']=='h264' and v['pix_fmt']=='yuv420p' and [v['width'],v['height']]==[960,694]
assert int(v['nb_read_frames'])==336 and Fraction(v['avg_frame_rate'])==Fraction(v['r_frame_rate'])==12 and abs(float(probe['format']['duration'])-28)<.01
frames=probe['frames'];assert len(frames)==336 and all(x['media_type']=='video' for x in frames)
validate_timestamps([float(x['best_effort_timestamp_time']) for x in frames],336,12)
cmd=['ffmpeg','-nostdin','-v','error','-xerror','-err_detect','explode','-i',str(video),'-map','0:v:0','-vsync','0','-f','rawvideo','-pix_fmt','rgb24','pipe:1']
proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE);rows=[];decoded_hashes={};size=960*694*3
try:
 for i in range(1,337):
  chunks=[];n=0
  while n<size:
   x=proc.stdout.read(size-n)
   if not x:break
   chunks.append(x);n+=len(x)
  data=b''.join(chunks);assert len(data)==size,('Early video EOF',i,n)
  arr=np.frombuffer(data,dtype=np.uint8).reshape((694,960,3));decoded_hashes.setdefault(hashlib.sha256(data).hexdigest(),[]).append(i);path=out/'frames'/f'frame_{i:04d}'/'image.png';assert sha(path)==f['frames'][i-1]['png_sha256']
  with Image.open(path) as im:original=np.array(im)
  assert hashlib.sha256(original.tobytes()).hexdigest()==f['frames'][i-1]['pixels_sha256']
  delta=arr.astype(float)-original.astype(float);mae=float(abs(delta).mean());rmse=float(np.sqrt((delta**2).mean()));bias=delta.mean(axis=(0,1)).tolist()
  # Conservative lossy-codec screening bounds, not visual/color certification.
  assert compression_acceptable(mae,bias),('Compression mismatch',i,mae,bias)
  rows.append({'index':i,'encoding_mae_8bit':mae,'encoding_rmse_8bit':rmse,'channel_bias_8bit':bias,'maximum_channel_error':int(abs(delta).max()),'decoded_sha256':hashlib.sha256(data).hexdigest()})
 assert not proc.stdout.read(1),'Unexpected extra decoded frames'
 stderr=proc.stderr.read().decode();assert proc.wait()==0,stderr
finally:
 if proc.poll() is None:proc.kill();proc.wait()
duplicates=[]
for group in decoded_hashes.values():
 if len(group)<2:continue
 hashes={i:f['frames'][i-1]['pixels_sha256'] for i in group};errors={i:rows[i-1]['encoding_mae_8bit'] for i in group};pairs={}
 with Image.open(out/'frames'/f'frame_{group[0]:04d}'/'image.png') as im:first=np.array(im).astype(float)
 for i in group[1:]:
  with Image.open(out/'frames'/f'frame_{i:04d}'/'image.png') as im:pairs[(group[0],i)]=float(abs(first-np.array(im).astype(float)).mean())
 duplicates.append(classify_duplicate(group,hashes,errors,pairs))
report={'pass':True,'video_sha256':sha(video),'frames_report_sha256':sha(a.frames_report),'frame_count':336,'fps':12,'duration_seconds':float(probe['format']['duration']),'resolution':[960,694],'codec':'h264','pixel_format':'yuv420p','audio':False,'full_decode_no_errors':True,'unique_decoded_frames':len(decoded_hashes),'decoded_duplicate_groups':duplicates,'exact_PTS_sequence':True,'mean_encoding_mae_8bit':sum(x['encoding_mae_8bit'] for x in rows)/336,'max_frame_encoding_mae_8bit':max(x['encoding_mae_8bit'] for x in rows),'frames':rows,'limits':'Every decoded frame compared to its corresponding verified actual PNG; lossy H264/yuv420p differences bounded numerically. This is not real-time visual playback or proof against subtle temporal denoising shimmer. No encoding, source modification or publication performed.'}
Path(a.report).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='frames'},indent=2))
