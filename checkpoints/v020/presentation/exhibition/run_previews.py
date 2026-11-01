"""Exactly four sequential fresh actual preview renders, no model save."""
import argparse,hashlib,json,subprocess,time
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--blender',required=True);p.add_argument('--output-dir',required=True);a=p.parse_args();root=Path(__file__).resolve().parent;source=Path(a.source).resolve();out=Path(a.output_dir).resolve();manifest=root/'views.json';plan=json.loads(manifest.read_text());expected='673dbbadca22d3dd45dc2f2eb5bde4a9e66851c1ca137da5c2570efc67c77614'
 assert plan['source_sha256']==expected and sha(source)==expected and not source.is_relative_to(out)
 assert list(plan['views'])==['A_monument','B_approach','C_sunlit','D_water'];out.mkdir(exist_ok=True);results=[];start=time.perf_counter();identities={p.name:sha(p) for p in [manifest,root/'render_preview.py',root/'preservation_support.py']}
 for view in plan['views']:
  assert all(sha(root/name)==h for name,h in identities.items())
  if (out/view).exists():
   r=json.loads((out/view/'receipt.json').read_text())
   assert r['source_sha256_after']==expected and r['source_sha256_before']==expected and r['manifest_sha256']==identities['views.json'] and r['script_sha256']==identities['render_preview.py'] and r['view']==view and sha(out/view/'image.png')==r['image_sha256']
   assert r['settings']['cycles']['samples']==16
   results.append({'view':view,'resumed_valid_receipt':True,'receipt_sha256':sha(out/view/'receipt.json'),'image_sha256':r['image_sha256']});continue
  cmd=[str(Path(a.blender).resolve()),'--background','--factory-startup','--disable-autoexec','--python-exit-code','1','--python',str(root/'render_preview.py'),'--','--source',str(source),'--source-sha',expected,'--manifest',str(manifest),'--view',view,'--output-dir',str(out/view)]
  t=time.perf_counter()
  with (out/(view+'.log')).open('x') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
  r=json.loads((out/view/'receipt.json').read_text());assert sha(out/view/'image.png')==r['image_sha256'] and sha(source)==expected
  results.append({'view':view,'process_wall_seconds':time.perf_counter()-t,'receipt_sha256':sha(out/view/'receipt.json'),'image_sha256':r['image_sha256']});print(json.dumps(results[-1]),flush=True)
 (out/'complete.json').write_text(json.dumps({'source_sha256':expected,'code_and_plan_sha256':identities,'cases':results,'total_wall_seconds':time.perf_counter()-start,'scope':'Four16samplecompositionpreviews; original world/light/view unchanged; no source saved'},indent=2)+'\n')
if __name__=='__main__':main()
