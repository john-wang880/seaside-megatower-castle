"""Independent completed-run audit. No Blender, encoding, model or approval writes."""
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
from PIL import Image
from qa_utils import validate_indices
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--output',required=True);p.add_argument('--report',required=True);p.add_argument('--source',required=True);a=p.parse_args()
root=Path(a.archive);out=Path(a.output);plan=json.loads((root/'final_plan.json').read_text())
expected_source='c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd'
assert sha(a.source)==plan['source_sha256']==expected_source
assert sha(root/'final_plan.json')=='27141d08ce3316651051ef3f6e42365871e873a2c82e4286d8d83e59c867ca11'
identity={'source_sha256':expected_source,**{key:sha(root/name) for key,name in [('plan_sha256','final_plan.json'),('worker_sha256','render_final_frame.py'),('motion_sha256','final_motion.py'),('runner_sha256','run_final_orbit.py'),('validator_sha256','orbit_common.py')]}}
assert json.loads((out/'run_identity.json').read_text())==identity
assert plan['pilot_indices']==list(range(1,9))+list(range(54,62))+list(range(76,84))+[336]
indices=list(range(1,337));assert len(plan['frames'])==336
complete=json.loads((out/'frames_complete.json').read_text());assert complete['identity']==identity and complete['source_saved'] is False and complete['source_sha256_after']==expected_source
validate_indices([f['index'] for f in complete['frames']],336)
folders=sorted(int(f.name.removeprefix('frame_')) for f in (out/'frames').glob('frame_*'));assert folders==indices,('Unexpected/missing pilot folders',folders)
rows=[];pairs=[];previous_pixels=None;previous_matrix=None
for i in indices:
 folder=out/'frames'/f'frame_{i:04d}';r=json.loads((folder/'metadata.json').read_text());e=r['effective_settings'];c=e['camera'];d=c['data'];m=np.array(c['matrix_world']);recipe=plan['frames'][i-1]['recipe']
 assert r['index']==i and r['recipe']==recipe and r['worker_sha256']==identity['worker_sha256'] and r['manifest_sha256_at_start']==identity['plan_sha256']
 assert r['source_sha256_before']==r['source_sha256_after']==expected_source and r['saved_model'] is False
 assert r['blender_version']==plan['expected_blender_version'] and r['threads']==8 and e['frame']==r['source_scene_frame']==plan['source_scene_frame']==1
 for field,key in [('cycles','expected_cycles'),('view_settings','expected_view_settings'),('image_settings','expected_image_settings')]: assert e[field]==plan[key]
 render=dict(e['render']);render.pop('filepath');assert render==plan['expected_render_except_filepath']
 assert d['type']=='PERSP' and d['sensor_fit']=='HORIZONTAL' and d['sensor_width']==36 and d['shift_x']==d['shift_y']==0
 for k in ('lens','clip_start','clip_end'): assert abs(d[k]-recipe[k])<1e-5
 assert d['sensor_fit']==plan['sensor_fit'] and d['sensor_width']==plan['sensor_width_mm']
 loc=np.array(recipe['location']);fwd=np.array(recipe['target'])-loc;fwd/=np.linalg.norm(fwd)
 assert np.max(abs(m[:3,3]-loc))<1e-5 and np.max(abs(-m[:3,2]-fwd))<1e-5
 assert np.max(abs(m[:3,:3].T@m[:3,:3]-np.eye(3)))<1e-5 and abs(np.linalg.det(m[:3,:3])-1)<1e-5
 aspect=render['resolution_x']*render['pixel_aspect_x']/(render['resolution_y']*render['pixel_aspect_y']);half=d['clip_start']*d['sensor_width']/(2*d['lens']);near=math.sqrt(d['clip_start']**2+half**2+(half/aspect)**2)
 assert abs(near-r['near_plane_corner_radius_m'])<1e-7 and near<plan['camera_proxy_radius_m']==.12
 assert sha(folder/'image.png')==r['png_file_sha256']
 with Image.open(folder/'image.png') as im:
  im.load();assert im.mode=='RGB' and list(im.size)==plan['resolution']==[960,694];arr=np.array(im)
 pixelsha=hashlib.sha256(arr.tobytes()).hexdigest();record=next(f for f in complete['frames'] if f['index']==i)
 assert record['valid'] is True and record['png_sha256']==r['png_file_sha256'] and record['metadata_sha256']==sha(folder/'metadata.json') and record['decoded_pixels_sha256']==pixelsha
 if previous_pixels is not None:
  delta=np.abs(arr.astype(float)-previous_pixels.astype(float));step=float(np.linalg.norm(m[:3,3]-previous_matrix[:3,3]));angle=math.degrees(math.acos(float(np.clip((np.trace(previous_matrix[:3,:3].T@m[:3,:3])-1)/2,-1,1))))
  assert step>0 and step<=1.478/12+1e-5 and angle<=45/12+1e-3
  pairs.append({'frames':[i-1,i],'translation_m':step,'orientation_degrees':angle,'pixel_mae_8bit':float(delta.mean()),'brightness_step_8bit':float(arr.mean()-previous_pixels.mean())})
 previous_pixels=arr;previous_matrix=m
 rows.append({'index':i,'metadata_sha256':sha(folder/'metadata.json'),'png_sha256':r['png_file_sha256'],'pixels_sha256':pixelsha,'near_corner_radius_m':near,'mean_rgb_luminance':float(arr.mean()),'dark_fraction_rgb_max_below_12':float((arr.max(axis=2)<12).mean())})
assert len({r['pixels_sha256'] for r in rows})==336,'Identical decoded frames'
report={'pass':True,'scope':'Receipt/decoded-frame integrity and bounded temporal pose checks for 336 actual frames only. Image differences describe real rendered motion; they are not automatic flicker acceptance. No full-stage approval is created.','identity':identity,'frames_complete_sha256':sha(out/'frames_complete.json'),'frames':rows,'adjacent_frame_pairs':pairs,'source_unchanged':sha(a.source)==expected_source,'visual_review':'Pending independent representative image inspection; final video not encoded or assessed.'}
Path(a.report).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'pass':True,'frames':336,'report':a.report}))
