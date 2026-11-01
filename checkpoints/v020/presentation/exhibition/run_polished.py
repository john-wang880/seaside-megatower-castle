import argparse,hashlib,json,subprocess,time
from pathlib import Path
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--blender',required=True);p.add_argument('--output-dir',required=True);a=p.parse_args();root=Path(__file__).resolve().parent;source=Path(a.source).resolve();out=Path(a.output_dir).resolve();manifest=root/'polished_views.json';plan=json.loads(manifest.read_text());h='673dbbadca22d3dd45dc2f2eb5bde4a9e66851c1ca137da5c2570efc67c77614';assert sha(source)==h and plan['source_sha256']==h and not out.exists() and not source.is_relative_to(out)
 identity={n:sha(root/n) for n in ['render_polished.py','preservation_support.py','polished_views.json','run_polished.py']}
 cmd=[str(Path(a.blender).resolve()),'--background','--factory-startup','--disable-autoexec','--python-exit-code','1','--python',str(root/'render_polished.py'),'--','--source',str(source),'--source-sha',h,'--manifest',str(manifest),'--view','A_monument','--output-dir',str(out)]
 t=time.perf_counter()
 with (out.parent/(out.name+'.log')).open('x') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
 assert sha(source)==h and all(sha(root/n)==v for n,v in identity.items());r=json.loads((out/'receipt.json').read_text());assert sha(out/'image.png')==r['image_sha256']
 (out/'run_receipt.json').write_text(json.dumps({'source_sha256':h,'runtime_sha256':identity,'command':cmd,'process_wall_seconds':time.perf_counter()-t,'receipt_sha256':sha(out/'receipt.json'),'image_sha256':r['image_sha256']},indent=2)+'\n');print(json.dumps({'done':str(out),'render_seconds':r['render_wall_seconds']}),flush=True)
if __name__=='__main__':main()
