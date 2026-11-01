"""Read-only complete orbit QA. Never renders or encodes; requires terminal markers."""
import argparse,hashlib,json,os,sys,subprocess,math
from pathlib import Path
sys.dont_write_bytecode=True
if sys.flags.optimize: raise RuntimeError('Optimized execution refused')
import numpy as np
from PIL import Image

def need(ok,msg):
 if not ok: raise RuntimeError(msg)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def timing(pts): return len(pts)==96 and all(math.isfinite(t) and abs(t-i/12)<1e-5 for i,t in enumerate(pts))
def compression(maes): return len(maes)==96 and max(maes)<10 and sum(maes)/96<5

def main():
 p=argparse.ArgumentParser()
 for n in ['recipe','output-dir','source','cache','report']: p.add_argument('--'+n,required=True)
 a=p.parse_args(); recipe=Path(a.recipe).resolve();root=Path(a.output_dir).resolve();source=Path(a.source).resolve();report=Path(a.report).resolve()
 need(not report.exists(),'Report exists');os.environ['XDG_CACHE_HOME']=str(Path(a.cache).resolve());sys.path.insert(0,str(recipe))
 import runtime_guards as g
 from orbit_common import validate_frame
 before={str(x):sha(x) for x in recipe.iterdir() if x.is_file()};sourcehash=sha(source)
 identity=g.identity();g.check_source(source);g.check_existing(root,identity)
 plan=json.loads((recipe/'final_plan.json').read_text());complete=json.loads((root/'frames_complete.json').read_text());receipt=json.loads((root/'video.json').read_text());video=root/'castle_v026_partial_orbit.mp4'
 need(complete['identity']==identity and complete['source_sha256_after']==sourcehash and complete['source_saved'] is False,'Completion identity')
 need(sorted(x.name for x in (root/'frames').iterdir())==[f'frame_{i:04d}' for i in range(1,97)],'Exact frame inventory')
 frames=[validate_frame(root/f'frames/frame_{i:04d}',i,plan,g.PLAN_SHA,sha(recipe/'render_final_frame.py')) for i in range(1,97)]
 need(all(x['valid'] for x in frames),'Invalid actual frame');need(frames==complete['frames'],'Frame manifest differs')
 need(receipt['video_sha256']==sha(video) and receipt['frames_manifest_sha256']==sha(root/'frames_complete.json'),'Video binding')
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]));streams=probe['streams'];need(len(streams)==1,'Audio/extra stream');v=streams[0]
 need(v['codec_type']=='video' and v['codec_name']=='h264' and (v['width'],v['height'])==(960,694) and v['avg_frame_rate']=='12/1' and int(v['nb_read_frames'])==96 and abs(float(v['duration'])-8)<1e-6,'Video format')
 pts=[float(x['best_effort_timestamp_time']) for x in json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(video)]))['frames']];need(timing(pts),'PTS mismatch')
 originals=[]
 for i in range(1,97):
  with Image.open(root/f'frames/frame_{i:04d}/image.png') as im: originals.append(np.asarray(im.convert('RGB')).copy())
 n=960*694*3; rows=[]; hashes=[]; prev=None;adj=[]
 with subprocess.Popen(['ffmpeg','-nostdin','-v','error','-xerror','-err_detect','explode','-i',str(video),'-map','0:v:0','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE) as proc:
  for i in range(96):
   b=proc.stdout.read(n);need(len(b)==n,f'Short decode {i+1}');arr=np.frombuffer(b,np.uint8).reshape(694,960,3);hashes.append(hashlib.sha256(b).hexdigest());f=arr.astype(np.float32)
   errors={j+1:float(np.abs(f-originals[j]).mean()) for j in range(max(0,i-2),min(96,i+3))};same=errors[i+1]
   # Local ordering evidence, not an assertion that lossy frames must be unique.
   rows.append({'index':i+1,'same_index_mae_255':same,'local_source_maes':errors,'best_local_source':min(errors,key=errors.get),'p99_abs_error':float(np.percentile(np.abs(f-originals[i]),99))})
   if prev is not None: adj.append({'pair':[i,i+1],'decoded_mae_255':float(np.abs(f-prev).mean()),'source_mae_255':float(np.abs(originals[i].astype(np.float32)-originals[i-1]).mean()),'source_brightness_step':float(originals[i].mean()-originals[i-1].mean())})
   prev=f
  need(proc.stdout.read(1)==b'','Extra decoded frame');err=proc.stderr.read();need(proc.wait()==0,'Strict decode failure '+err.decode(errors='replace'))
 need(compression([r['same_index_mae_255'] for r in rows]),'Compression limit (mean<5,max<10 /255)')
 mismatches=[r for r in rows if r['best_local_source']!=r['index']];duplicates=[{'indices':[i+1,j+1],'source_same':frames[i]['decoded_pixels_sha256']==frames[j]['decoded_pixels_sha256'],'source_mae_255':float(np.abs(originals[i].astype(np.float32)-originals[j]).mean())}for i in range(96)for j in range(i+1,96)if hashes[i]==hashes[j]]
 need(not mismatches,'Local frame correspondence ambiguous: manual review required')
 need(sha(source)==sourcehash and before=={str(x):sha(x)for x in recipe.iterdir()if x.is_file()},'Inputs changed')
 result={'pass':True,'source_sha256':sourcehash,'identity':identity,'video_sha256':sha(video),'completion_sha256':sha(root/'frames_complete.json'),'video_receipt_sha256':sha(root/'video.json'),'probe':probe,'pts':pts,'frames':frames,'decode_rows':rows,'decoded_hashes':hashes,'decoded_duplicate_pairs':duplicates,'original_unique_count':len({x['decoded_pixels_sha256'] for x in frames}),'adjacent_metrics':adj,'largest_adjacent_source_pairs':sorted(adj,key=lambda x:x['source_mae_255'],reverse=True)[:5],'mean_compression_mae_255':sum(r['same_index_mae_255'] for r in rows)/96,'max_compression_mae_255':max(r['same_index_mae_255'] for r in rows),'input_inventory_unchanged':True,'limits':'Exact recipe/PNG/96 PTS provenance, strict full decode and same-index compression checks. Local +/-2 source correspondence tested. Lossy duplicates are reported, not equated with fabrication. Adjacent statistics flag review candidates, not temporal-flicker or global visual certification.'}
 report.write_text(json.dumps(result,indent=2));print(json.dumps({k:result[k] for k in ['pass','mean_compression_mae_255','max_compression_mae_255','original_unique_count','decoded_duplicate_pairs','largest_adjacent_source_pairs']}))
if __name__=='__main__': main()
