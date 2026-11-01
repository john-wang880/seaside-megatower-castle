from pathlib import Path
import json,hashlib,collections,math
import numpy as np
from PIL import Image
P=Path('work/contact_significance_v025');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rows=[];checks=[];inputs={}
for ver in ['024','025']:
 cp=Path(f'work/coplanar_method_recheck/v{ver}.json');vp=Path(f'work/coplanar_method_recheck/v{ver}_visibility.json');C=json.loads(cp.read_text());V=json.loads(vp.read_text());inputs[str(cp)]=sha(cp);inputs[str(vp)]=sha(vp);selected=[]
 for r in C['results']:
  groups=collections.defaultdict(list)
  for c in r['contacts']:groups[(c['object'],tuple(round(v,4)for v in c['normal']),round(c['plane_offset'],4),c['same_facing'])].append(c)
  selected.extend((r['union'],c)for g in groups.values()for c in sorted(g,key=lambda x:x['area'],reverse=True)[:2])
 receipts=list(dict.fromkeys(x['receipt']for x in V['samples']));N=len(receipts);assert N==(2 if ver=='024' else 3)
 blocks=[]
 for i,r in enumerate(V['samples']):
  if r['sample_index']==0 and r['receipt']==receipts[0]:blocks.append([])
  blocks[-1].append(r)
 assert len(blocks)==len(selected)
 for idx,((u,c),block) in enumerate(zip(selected,blocks)):
  assert all(r['union']==u and r['neighbor']==c['object']and r['neighbor_polygon']==c['neighbor_polygon']for r in block)
  base=[r for r in block if r['receipt']==receipts[0]];assert [r['sample_index']for r in base]==list(range(len(base)))
  center=np.array(base[0]['sample']);vertices=np.array([2*np.array(r['sample'])-center for r in base[1:]])
  area=np.linalg.norm(sum((np.cross(a,b)for a,b in zip(vertices,np.roll(vertices,-1,axis=0))),np.zeros(3)))/2
  err=abs(area-c['area']);assert err<max(1e-7,c['area']*1e-8),(idx,err,area,c['area']);checks.append({'version':ver,'selection_index':idx,'contact_area':c['area'],'reconstructed_area':float(area),'absolute_error':float(err)})
  for receipt in receipts:
   rs=[r for r in block if r['receipt']==receipt];R=json.loads(Path(receipt).read_text());inputs[receipt]=sha(receipt);cd=R['settings']['camera']['data'];render=R['settings']['render'];W=render['resolution_x'];H=render['resolution_y'];assert render['resolution_percentage']==100 and render['pixel_aspect_x']==render['pixel_aspect_y']==1;assert cd['sensor_fit']in ['AUTO','HORIZONTAL']and cd['shift_x']==cd['shift_y']==0 and W>H
   inv=np.linalg.inv(np.array(R['settings']['camera']['matrix_world']));tx=cd['sensor_width']/(2*cd['lens']);ty=tx*H/W
   def project(x):
    q=inv@np.append(x,1);assert q[2]<0
    return np.array([(0.5+q[0]/(-q[2])/(2*tx))*W,(0.5-q[1]/(-q[2])/(2*ty))*H])
   poly=np.array([project(v)for v in vertices]);bbox=[poly.min(axis=0).tolist(),poly.max(axis=0).tolist()];pa=abs(sum(a[0]*b[1]-a[1]*b[0]for a,b in zip(poly,np.roll(poly,-1,axis=0))))/2
   image=Path('work/lateral_coverage_v025/actual/image.png')if 'lateral_coverage' in receipt else Path(f'checkpoints/v{ver}/previews/'+('hero_after.png'if 'hero' in receipt else 'rear_after.png'));inputs[str(image)]=sha(image);im=Image.open(image);assert im.size==(W,H)
   samples=[]
   for r in rs:
    if not(r['contact_at_first_surface']and r['inside_camera_frame']and r['outward_front_facing']):continue
    xy=project(r['sample']);px=[int(math.floor(z))for z in xy]
    samples.append({'sample_index':r['sample_index'],'world':r['sample'],'projected_pixel':xy.tolist(),'pixel_cell':px,'RGB':list(im.getpixel(tuple(px)))if 0<=px[0]<W and 0<=px[1]<H else None,'nearest_hit':r['nearest_hit']})
   rows.append({'version':ver,'selection_index':idx,'union':u,'neighbor':c['object'],'union_triangle':c['union_triangle'],'neighbor_triangle':c['neighbor_triangle'],'neighbor_polygon':c['neighbor_polygon'],'normal':c['normal'],'plane_offset':c['plane_offset'],'same_facing':c['same_facing'],'strict_coplanar_at_1e_7':c['strict_coplanar_at_1e_7'],'max_plane_distance':c['max_plane_distance'],'contact_pair_area':c['area'],'reconstructed_polygon':vertices.tolist(),'receipt':receipt,'image':str(image),'potential_projected_bbox':bbox,'potential_projected_area_pixels2':float(pa),'subpixel_area':bool(pa<1),'first_surface_samples':samples,'all_sample_count':len(rs)})
ranked=sorted([r for r in rows if r['same_facing']and r['first_surface_samples']],key=lambda r:r['potential_projected_area_pixels2'],reverse=True)
report={'inputs_sha256':inputs,'reconstruction_checks':checks,'all_projected_records':rows,'ranked_same_facing_reachable':ranked,'limits':'Potential projected pair-polygon footprint, NOT visible area. Pair polygons may overlap; do not sum. Finite first-surface samples do not prove all pixels visible or their exact shader contribution. RGB reads existing filtered/denoised image pixel cell, not an independent render. No model/Blender/render/crop.'};(P/'ranked.json').write_text(json.dumps(report,indent=2));print('RECONSTRUCTED',len(checks),'RANKED',len(ranked));
for r in ranked[:20]:print(r['version'],r['selection_index'],Path(r['receipt']).name,round(r['potential_projected_area_pixels2'],3),r['potential_projected_bbox'],len(r['first_surface_samples']),r['strict_coplanar_at_1e_7'])
