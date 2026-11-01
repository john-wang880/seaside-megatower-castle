import argparse,json,hashlib,math
from pathlib import Path
p=argparse.ArgumentParser()
for k in ['geometry','envelopes','report']:p.add_argument('--'+k,required=True)
a=p.parse_args();assert not Path(a.report).exists();g=json.loads(Path(a.geometry).read_text());e=json.loads(Path(a.envelopes).read_text());b=g['candidate_bounds']
def gap(c):return math.sqrt(sum(max(b[0][k]-c[1][k],c[0][k]-b[1][k],0)**2 for k in range(3)))
body=[{'zone':x['zone'],'distance_lower_bound':gap(x['bounds'])}for x in e['body_prisms']];camera=[{'s_interval':x['s_interval'],'distance_lower_bound':gap(x['box'])}for x in e['camera_continuous_interval_boxes']];r={'pass':all(x['distance_lower_bound']>0 for x in body+camera),'input_sha256':g['input_sha256'],'geometry_sha256':hashlib.sha256(Path(a.geometry).read_bytes()).hexdigest(),'envelopes_sha256':hashlib.sha256(Path(a.envelopes).read_bytes()).hexdigest(),'body_prisms':body,'minimum_body_gap':min(x['distance_lower_bound']for x in body),'camera_interval_count':len(camera),'minimum_camera_envelope_gap':min(x['distance_lower_bound']for x in camera),'scope':e['scope']};Path(a.report).write_text(json.dumps(r,indent=2));print(r['pass'],r['minimum_body_gap'],r['minimum_camera_envelope_gap']);assert r['pass']
