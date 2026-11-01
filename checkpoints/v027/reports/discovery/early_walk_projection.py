import json,itertools
from pathlib import Path
import numpy as np
P=Path('work/interior_ceiling_v026');plan=json.loads(Path('checkpoints/v018/presentation/interior_route/final_plan.json').read_text());d=json.loads((P/'art_profile_review.json').read_text());W,H=plan['resolution'];rows=[]
for f in plan['frames'][:76]:
 r=f['recipe'];loc=np.array(r['location']);fw=np.array(r['target'])-loc;fw/=np.linalg.norm(fw);right=np.cross(fw,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,fw);tx=plan['sensor_width_mm']/(2*r['lens']);ty=tx*H/W
 def project(v):
  q=np.array(v)-loc;z=float(q@fw);x=(.5+(q@right)/z/(2*tx))*W;y=(.5-(q@up)/z/(2*ty))*H
  return {'pixel':[float(x),float(y)],'depth':z,'in_frame':bool(z>0 and 0<=x<W and 0<=y<H)}
 arch=[]
 for profile in d['profiles']:
  ps=[project(p)for p in profile['intrados_samples']];x=profile['station_x'];corners=[project(p)for p in itertools.product([x-.14,x+.14],[36.6,39.4],[32.15,32.82])];front=[p for p in corners if p['depth']>0]
  arch.append({'station':x,'intrados_points_in_frame':sum(p['in_frame']for p in ps),'intrados_points':ps,'conservative_box_corner_projection':corners,'front_box_max_y_pixel':max([p['pixel'][1]for p in front],default=None)})
 rows.append({'index':f['index'],'camera_location':r['location'],'gaze':r['target'],'arches':arch,'stations_with_any_intrados':sum(a['intrados_points_in_frame']>0 for a in arch)})
report={'source':'Exacthistorical76earlyposes, unchangedcurrentgeometry; no newview/render','frames':rows,'maximum_stations_with_any_intrados':max(r['stations_with_any_intrados']for r in rows),'frames_with_two_or_more':[r['index']for r in rows if r['stations_with_any_intrados']>=2],'per_station_peak_sample_counts':{str(x):max(a['intrados_points_in_frame']for r in rows for a in r['arches']if a['station']==x)for x in[-1.8,.4,2.6]},'limits':'Pointprojection surrogateplusboundingcorners, not renderedocclusion. Forearlyall-frontboxes entirelyaboveframe, projectionmaximum atvertices bounds any withinprofile, independentofsurrogatecurvature.'};(P/'early_walk_projection.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items()if k!='frames'})
