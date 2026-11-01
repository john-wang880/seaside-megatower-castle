"""Synthetic fixtures only: never invoke Blender or render model."""
import copy,json,tempfile
from pathlib import Path
from PIL import Image
from orbit_common import sha,validate_frame
from runtime_guards import identity
root=Path(__file__).resolve().parent;planpath=root/'final_plan.json';plan=json.loads(planpath.read_text());worker_sha=sha(root/'render_final_frame.py')
# Construct a synthetic receipt and mathematical look-at pose; no production assets needed.
import math
recipe=plan['frames'][0]['recipe'];forward=[recipe['target'][i]-recipe['location'][i] for i in range(3)]
def norm(v):
 length=math.sqrt(sum(x*x for x in v));return [x/length for x in v]
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
forward=norm(forward);right=norm(cross(forward,[0,0,1]));up=cross(right,forward)
mat=[[right[i],up[i],-forward[i],recipe['location'][i]] for i in range(3)]+[[0,0,0,1]]
base={'lighting_state_sha256_before':plan['expected_lighting_state_sha256'],'lighting_state_sha256_after':plan['expected_lighting_state_sha256'],'runtime_identity_before':identity(),'runtime_identity_after':identity(),'index':1,'recipe':recipe,'manifest_sha256_at_start':sha(planpath),'worker_sha256':worker_sha,'source_sha256_before':plan['source_sha256'],'source_sha256_after':plan['source_sha256'],'saved_model':False,'blender_version':plan['expected_blender_version'],'threads':8,'elapsed_render_seconds':0,'effective_settings':{'cycles':plan['expected_cycles'],'render':dict(plan['expected_render_except_filepath'],filepath='synthetic'),'view_settings':plan['expected_view_settings'],'image_settings':plan['expected_image_settings'],'frame':1,'camera':{'matrix_world':mat,'use_dof':False,'data':dict({k:v for k,v in plan['expected_camera_projection'].items()if k!='use_dof'},**{k:recipe[k]for k in ('lens','clip_start','clip_end')})}}}
results=[]
with tempfile.TemporaryDirectory(prefix='resume_fixture_') as tmp:
 folder=Path(tmp)
 Image.new('RGB',(960,694),(10,20,30)).save(folder/'image.png')
 base['png_file_sha256']=sha(folder/'image.png')
 def check(name,receipt,expected):
  (folder/'metadata.json').write_text(json.dumps(receipt))
  result=validate_frame(folder,1,plan,sha(planpath),worker_sha)
  assert result['valid']==expected,(name,result)
  results.append({'test':name,'passed':True})
 check('valid fixture accepted',base,True)
 for name,change in [('wrong source',lambda d:d.update(source_sha256_after='bad')),('wrong recipe hash',lambda d:d.update(manifest_sha256_at_start='bad')),('wrong worker hash',lambda d:d.update(worker_sha256='bad')),('wrong runner identity',lambda d:d['runtime_identity_after']['runtime_sha256'].update({'run_final_orbit.py':'bad'})),('wrong sample quality',lambda d:d['effective_settings']['cycles'].update(samples=16)),('late NaN basis',lambda d:d['effective_settings']['camera']['matrix_world'][2].__setitem__(1,float('nan'))),('NaN elapsed',lambda d:d.update(elapsed_render_seconds=float('nan'))),('negative elapsed',lambda d:d.update(elapsed_render_seconds=-1)),('wrong camera roll',lambda d:d['effective_settings']['camera']['matrix_world'][0].__setitem__(0,0)),('wrong sensor width',lambda d:d['effective_settings']['camera']['data'].update(sensor_width=35)),('wrong camera shift',lambda d:d['effective_settings']['camera']['data'].update(shift_x=.1)),('wrong DOF',lambda d:d['effective_settings']['camera'].update(use_dof=True)),('wrong scene frame',lambda d:d['effective_settings'].update(frame=2)),('wrong camera location',lambda d:d['effective_settings']['camera']['matrix_world'][0].__setitem__(3,0))]:
  d=copy.deepcopy(base);change(d);check(name,d,False)
 (folder/'image.png').write_bytes(b'corrupted');check('corrupt PNG rejected',base,False)
 Image.new('RGB',(10,10)).save(folder/'image.png');d=copy.deepcopy(base);d['png_file_sha256']=sha(folder/'image.png');check('wrong dimensions despite matching hash rejected',d,False)
 (folder/'metadata.json').unlink();assert not validate_frame(folder,1,plan,sha(planpath),worker_sha)['valid'];results.append({'test':'incomplete frame rejected','passed':True})
(root/'resume_validation_tests.json').write_text(json.dumps({'synthetic_only':True,'tests':results,'all_passed':True},indent=2)+'\n');print('PASS',len(results),'synthetic validation tests; no model renders')
