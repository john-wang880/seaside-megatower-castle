"""Read completed actual Blender camera receipts, no Blender process or writes to model."""
import argparse,hashlib,json,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--keyframes',required=True);p.add_argument('--render-root',required=True);p.add_argument('--continuous-proof',required=True);p.add_argument('--report',required=True);a=p.parse_args();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();P=json.load(open(a.plan));K=json.load(open(a.keyframes));C=json.load(open(a.continuous_proof));assert C['pass'] and C['plan_sha256']==sha(a.plan) and P['source_sha256']==K['source_sha256'];rows=[]
for name,recipe in K['views'].items():
 folder=Path(a.render_root)/name;r=json.load(open(folder/'metadata.json'));e=r['effective_settings'];camera=e['camera'];data=camera['data'];render=e['render'];matrix=camera['matrix_world']
 assert r['view']==name and r['recipe']==recipe and r['manifest_sha256_at_start']==sha(a.keyframes)
 assert r['source_sha256_before']==r['source_sha256_after']==P['source_sha256'] and r['saved_model'] is False and e['frame']==1
 location_error=max(abs(matrix[i][3]-recipe['location'][i]) for i in range(3));direction=[recipe['target'][i]-recipe['location'][i] for i in range(3)];length=math.sqrt(sum(x*x for x in direction));direction=[x/length for x in direction];direction_error=max(abs(-matrix[i][2]-direction[i]) for i in range(3));assert location_error<1e-5 and direction_error<1e-5
 assert data['type']=='PERSP' and data['sensor_fit']=='HORIZONTAL' and data['sensor_width']==36 and data['shift_x']==data['shift_y']==0
 assert abs(data['lens']-26)<1e-6 and abs(data['clip_start']-.05)<1e-7 and abs(data['clip_end']-3000)<1e-5
 aspect=render['resolution_x']*render['pixel_aspect_x']/(render['resolution_y']*render['pixel_aspect_y']);halfwidth=data['clip_start']*data['sensor_width']/(2*data['lens']);near=math.sqrt(data['clip_start']**2+halfwidth**2+(halfwidth/aspect)**2)
 assert abs(near-r['actual_near_plane_corner_radius_m'])<1e-7 and near<.12 and r['camera_proxy_radius_m']==.12
 assert [render['resolution_x'],render['resolution_y']]==P['camera']['preview_aspect'] and render['resolution_percentage']==100
 assert e['cycles']['samples']==16 and sha(folder/'image.png')==r['png_file_sha256']
 assert abs(math.degrees(math.asin(direction[2]))+5)<1e-7
 rows.append({'view':name,'metadata_sha256':sha(folder/'metadata.json'),'location_max_error':location_error,'forward_direction_max_error':direction_error,'actual_near_plane_corner_radius':r['actual_near_plane_corner_radius_m'],'independently_calculated_near_corner_radius':near,'proxy_radius_margin':.12-near,'source_unchanged':True,'scene_frame':1,'samples':16})
assert len(rows)==5
r={'pass':True,'source_sha256':P['source_sha256'],'plan_sha256':sha(a.plan),'continuous_proof_sha256':sha(a.continuous_proof),'keyframe_manifest_sha256':sha(a.keyframes),'views':rows,'scope':'Five actual rendered camera receipts match planned locations/view directions, source/frame, perspective lens/gate/clips and near-plane bounds. Each near plane fits the continuously certified head sphere. This closes the camera-gate assumption for these feasibility views, not a final temporal interpolation or human-body/gait certificate.','remaining':'Final monotone timeparameterization, turn yaw acceleration and frame readability require separate owner review; full-route8–12s is accelerated rather than normal walking.'}
Path(a.report).write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
