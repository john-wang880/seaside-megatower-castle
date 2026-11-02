"""Sequential fixed v028-view regressions, no model saves or concurrent renders."""
import pathlib,subprocess,os,sys,json,hashlib,time
r=pathlib.Path(__file__).resolve().parent
repo=r.parents[2]
blender=repo.parent/'tools/blender-5.2.3-linux-x64/blender'
source=r.parent/'candidate.blend';sha='4f838529d32cbf6a0314cc0a23b3dd1703b73d80c5db146fb4d323697b882df5'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if digest(source)!=sha:raise RuntimeError('Wrong source')
for view in ['doorway','frame_0001','frame_0076','hero']:
 out=r/view;manifest=r/(view+'_views.json');receipt=out/'receipt.json'
 if out.exists():
  if not receipt.is_file():raise RuntimeError('Incomplete existing output '+view)
  d=json.loads(receipt.read_text())
  if d['source_sha256_after']!=sha or d['manifest_sha256']!=digest(manifest) or d['image_sha256']!=digest(out/'image.png'):raise RuntimeError('Stale output '+view)
  print('VERIFIED_SKIP',view,flush=True);continue
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',XDG_CACHE_HOME=str(r.parent/'cache'))
 cmd=[str(blender),'-b','--factory-startup','--disable-autoexec','--python-exit-code','1','--python',str(r/'render_one.py'),'--','--source',str(source),'--source-sha',sha,'--manifest',str(manifest),'--output-dir',str(out),'--view',view]
 print('START',view,flush=True);start=time.monotonic()
 with (r/(view+'.log')).open('w') as log:subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 print('DONE',view,time.monotonic()-start,flush=True)
print('ALL_REGRESSIONS_COMPLETE',flush=True)
