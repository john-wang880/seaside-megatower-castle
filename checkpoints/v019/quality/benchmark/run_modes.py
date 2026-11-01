"""Two fresh HIGH/LOW actual renders; explicit validated viewer hashes required."""
import argparse,hashlib,json,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('high','high-sha','low','low-sha','blender','output-dir','high-reference','low-reference'):p.add_argument('--'+n,required=True)
 p.add_argument('--dry-run',action='store_true');a=p.parse_args();out=Path(a.output_dir).resolve();blender=Path(a.blender).resolve();cases=[('HIGH',Path(a.high).resolve(),a.high_sha,Path(a.high_reference).resolve()),('LOW',Path(a.low).resolve(),a.low_sha,Path(a.low_reference).resolve())]
 assert not out.exists() and blender.is_file()
 for name,source,h,reference in cases:assert sha(source)==h and reference.is_file() and out!=source and not source.is_relative_to(out)
 plan=ROOT/'views.json';worker=ROOT/'render_one.py';helper=ROOT/'preservation_support.py';identity={'manifest_sha256':sha(plan),'worker_sha256':sha(worker),'helper_sha256':sha(helper),'runner_sha256':sha(__file__),'sources':{n:h for n,_,h,_ in cases},'reference_png_sha256':{n:sha(p) for n,_,_,p in cases}}
 if a.dry_run:print(json.dumps({'dry_run':True,'identity':identity},indent=2));return
 from PIL import Image,ImageChops,ImageStat
 out.mkdir(parents=True,exist_ok=False);(out/'identity.json').write_text(json.dumps(identity,indent=2)+'\n');results=[]
 for name,source,h,reference in cases:
  assert sha(plan)==identity['manifest_sha256'] and sha(worker)==identity['worker_sha256'] and sha(helper)==identity['helper_sha256'] and sha(__file__)==identity['runner_sha256']
  cmd=[str(blender),'--background','--factory-startup','--disable-autoexec','--python-exit-code','1','--python',str(worker),'--','--source',str(source),'--source-sha',h,'--manifest',str(plan),'--view','approach','--output-dir',str(out/name)]
  start=time.perf_counter()
  with (out/(name+'.log')).open('x') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
  wall=time.perf_counter()-start;r=json.loads((out/name/'receipt.json').read_text());assert sha(source)==h and sha(out/name/'image.png')==r['image_sha256'] and sha(reference)==identity['reference_png_sha256'][name]
  with Image.open(reference) as b,Image.open(out/name/'image.png') as c:
   b.load();c.load();assert b.mode==c.mode=='RGB' and b.size==c.size==(1200,866)
   exact=b.tobytes()==c.tobytes();difference=ImageChops.difference(b,c);extrema=difference.getextrema();maxdiff=max(v[1] for v in extrema);mean_difference=sum(ImageStat.Stat(difference).mean)/3
   pixelsha=hashlib.sha256(c.tobytes()).hexdigest()
  results.append({'mode':name,'source_sha256':h,'process_wall_seconds':wall,'receipt':r,'reference_image':str(reference),'decoded_pixels_exact':exact,'maximum_channel_difference':maxdiff,'mean_absolute_channel_difference':mean_difference,'decoded_pixels_sha256':pixelsha});(out/'progress.json').write_text(json.dumps(results,indent=2)+'\n');print('COMPLETE',name,'pixels_exact',exact,'seconds',wall,flush=True)
 # Record mismatches as evidence, not silent acceptance or automatic rerender.
 b=json.loads(json.dumps(results[0]['receipt']['settings']));c=json.loads(json.dumps(results[1]['receipt']['settings']));b['render'].pop('filepath');c['render'].pop('filepath');assert b==c,'Mode rendering settings differ'
 (out/'comparison.json').write_text(json.dumps({'identity':identity,'results':results,'mode_settings_equal_except_output':True,'all_reference_pixels_exact':all(r['decoded_pixels_exact'] for r in results),'limits':'One fresh process per mode, HIGH then LOW; observations not randomized benchmark. HIGH data remains stored in viewer, so no file-size or guaranteed scene-load savings claim.'},indent=2)+'\n')
if __name__=='__main__':main()
