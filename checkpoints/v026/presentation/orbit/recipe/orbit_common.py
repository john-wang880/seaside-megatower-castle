"""Read-only frame validation used by runner and fixture tests."""
import hashlib,json,math,sys
if sys.flags.optimize:raise RuntimeError("Optimized Python refused")
from runtime_guards import identity,clean
from pathlib import Path
from PIL import Image

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def validate_frame(folder,index,plan,plan_sha,worker_sha):
 try:
  folder=clean(folder);clean(folder/'metadata.json');clean(folder/'image.png');r=json.loads((folder/'metadata.json').read_text());e=r['effective_settings'];recipe=plan['frames'][index-1]['recipe']
  assert r['runtime_identity_before']==r['runtime_identity_after']==identity()
  assert r['lighting_state_sha256_before']==r['lighting_state_sha256_after']==plan['expected_lighting_state_sha256']
  assert r['index']==index and r['recipe']==recipe
  assert r['blender_version']==plan['expected_blender_version']
  assert r['manifest_sha256_at_start']==plan_sha and r['worker_sha256']==worker_sha
  assert r['source_sha256_before']==r['source_sha256_after']==plan['source_sha256'] and r['saved_model'] is False
  assert e['cycles']==plan['expected_cycles'];assert e['view_settings']==plan['expected_view_settings'];assert e['image_settings']==plan['expected_image_settings']
  render=dict(e['render']);render.pop('filepath');assert render==plan['expected_render_except_filepath']
  assert e['frame']==plan['source_scene_frame']==1 and r['threads']==8
  c=e['camera'];m=c['matrix_world'];assert isinstance(m,list)and len(m)==4 and all(isinstance(row,list)and len(row)==4 for row in m)
  assert all(type(x)in(int,float)and math.isfinite(x)for row in m for x in row)
  assert type(r['elapsed_render_seconds'])in(int,float)and math.isfinite(r['elapsed_render_seconds'])and r['elapsed_render_seconds']>=0
  d=[recipe['target'][i]-recipe['location'][i] for i in range(3)];length=math.sqrt(sum(v*v for v in d))
  assert max(abs(m[i][3]-recipe['location'][i]) for i in range(3))<1e-4
  assert max(abs(-m[i][2]-d[i]/length) for i in range(3))<1e-5
  f=[v/length for v in d];right=[f[1],-f[0],0.0];rn=math.sqrt(sum(x*x for x in right));right=[x/rn for x in right];up=[right[1]*f[2]-right[2]*f[1],right[2]*f[0]-right[0]*f[2],right[0]*f[1]-right[1]*f[0]]
  assert max(abs(m[i][j]-[right,up,[-x for x in f]][j][i])for i in range(3)for j in range(3))<1e-5
  assert m[3]==[0.0,0.0,0.0,1.0]
  assert {k:(c['use_dof']if k=='use_dof'else c['data'][k])for k in plan['expected_camera_projection']}==plan['expected_camera_projection']
  for k in ('lens','clip_start','clip_end'):assert abs(c['data'][k]-recipe[k])<1e-5
  assert sha(folder/'image.png')==r['png_file_sha256']
  with Image.open(folder/'image.png') as im:
   im.load();assert im.mode=='RGB' and list(im.size)==plan['resolution']
   pixels=hashlib.sha256(im.tobytes()).hexdigest()
  return {'valid':True,'index':index,'png_sha256':r['png_file_sha256'],'metadata_sha256':sha(folder/'metadata.json'),'decoded_pixels_sha256':pixels,'elapsed_render_seconds':r['elapsed_render_seconds']}
 except (OSError,ValueError,KeyError,AssertionError,TypeError,IndexError,RuntimeError) as exc:
  return {'valid':False,'index':index,'reason':type(exc).__name__+': '+str(exc)}
