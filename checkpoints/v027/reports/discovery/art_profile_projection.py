from pathlib import Path
import json,math,hashlib
import numpy as np
P=Path('work/interior_ceiling_v026');d=json.loads((P/'current_survey.json').read_text());v=json.loads((P/'views.json').read_text());W,H=v['resolution'];stations=[-1.8,.4,2.6];spring=32.15;crown=32.5
# Deliberately only a monotone shallow twin-curve projection surrogate, NOT authorized/final circular-arc geometry.
profiles=[]
for x in stations:
 points=[]
 for i in range(25):
  y=36.6+2.8*i/24;t=1-abs(y-38)/1.4;z=spring+.35*(1.5*t-.5*t*t);points.append([x,y,z])
 extr=[[x,y,min(z+.30,32.82)]for x,y,z in points];profiles.append({'station_x':x,'intrados_samples':points,'extrados_vertical_surrogate':extr,'landmarks':{'south_spring':[x,36.6,32.15],'crown_intrados':[x,38,32.5],'crown_outer_target':[x,38,32.82],'north_spring':[x,39.4,32.15]}})
envelopes=[{'name':'rib'+str(i),'bounds':[[x-.14,36.3,32.15],[x+.14,39.7,32.82]],'note':'Conservative full .30radial lateral extent, not a designed boundary'}for i,x in enumerate(stations)]+[{'name':'south band','bounds':[[-2.5,36.56,31.98],[3.2,36.72,32.22]]},{'name':'north band','bounds':[[-2.5,39.28,31.98],[3.2,39.44,32.22]]}]
def gap(a,b):return math.sqrt(sum(max(a[0][k]-b[1][k],b[0][k]-a[1][k],0)**2 for k in range(3)))
clear=[]
for e in envelopes:
 for o in d['objects']:
  if o['type']=='MESH'and(o['name'].startswith(('V013 |','V014 |','V015 |'))or'timber leaf'in o['name']or'open-leaf'in o['name']):clear.append({'envelope':e['name'],'object':o['name'],'separation_lower_bound':gap(e['bounds'],o['bounds'])})
projection=[]
for name,cv in v['views'].items():
 inv=np.linalg.inv(np.array(cv['reference_matrix']));cd=cv['camera_data'];tx=cd['sensor_width']/(2*cd['lens']);ty=tx*H/W
 def pr(p):
  q=inv@np.append(p,1);xy=[(.5+q[0]/-q[2]/(2*tx))*W,(.5-q[1]/-q[2]/(2*ty))*H];return {'pixel':xy,'depth':float(-q[2]),'in_frame':bool(q[2]<0 and 0<=xy[0]<W and 0<=xy[1]<H)}
 for p in profiles:
  a=[pr(x)for x in p['intrados_samples']];b=[pr(x)for x in p['extrados_vertical_surrogate']];projection.append({'view':name,'station_x':p['station_x'],'intrados':a,'extrados_surrogate':b,'intrados_in_frame':sum(x['in_frame']for x in a),'landmarks':{k:pr(x)for k,x in p['landmarks'].items()},'note':'Point projection only, no depthbuffer/occlusion; curvature surrogate not finalgeometry.'})
 bands=[]
 for e in envelopes[-2:]:
  lo,hi=e['bounds'];pts=[pr([x,y,z])for x in[lo[0],hi[0]]for y in[lo[1],hi[1]]for z in[lo[2],hi[2]]];bands.append({'name':e['name'],'corners':pts})
 projection.append({'view':name,'bands':bands})
r={'source_sha256':d['source_sha256'],'scope':'ART target renewed bounds/projection only; no geometry/no Blender/no render. Curve surrogate deliberately not a final pointedarch recipe.','intrados_min_body_top_margin':32.15-31.1,'band_min_body_top_margin':31.98-31.1,'profiles':profiles,'review_envelopes':envelopes,'fixture_clearance':clear,'projection':projection,'host_note':'Actual sidewalls .1thick andceiling32.799999..32.900002 unchanged. Crown32.82 can seat .020001; fullradial feet mayextend beyondthinlinings, requiring actuallegacyhost checks or bounded heel profile before geometryapproval. Bandtop32.22 overlaps springheight32.15 by.07 nominal.'};(P/'art_profile_review.json').write_text(json.dumps(r,indent=2));print('MIN',min(clear,key=lambda x:x['separation_lower_bound']))
for p in projection:
 if 'station_x'in p:print(p['view'],p['station_x'],p['intrados_in_frame'],p['landmarks'])
