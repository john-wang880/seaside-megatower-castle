import os
import json,sys,hashlib
from pathlib import Path
P=Path(os.environ['V028_QA_OUTPUT']);DATA=Path(os.environ['V028_QA_DATA']);sys.path.insert(0,str(Path(__file__).resolve().parent));from continuous_box_cover import box_inside
n=json.loads((P/'native_geometry.json').read_text());m=n['meshes'][-1];c={'object':m['name'],'seed':0,'vertices':m['vertices'],'local_triangles':m['triangles'],'local_faces':m['faces']};proof=json.loads((DATA/'guard_partition_proof.json').read_text());rows={}
for name,r in proof['source_seat_positive_box_witnesses'].items():
 q=box_inside(c,*r['bounds']);assert q['pass'],name;rows[name]=q
# Strict interior witness through each retained pier into the retained roof band.
for name,y in [('south',35.),('north',38.6)]:
 q=box_inside(c,[10.7,y-.1,31.7],[11.3,y+.1,31.9]);assert q['pass'];rows[name+'_pier_band_continuity']=q
out={'pass':True,'candidate_sha256':n['candidate_sha256'],'eleven_original_positive_seats_retained':len(proof['source_seat_positive_box_witnesses'])==11,'witnesses':rows,'limits':'Finite positive-volume geometric seating/continuity witnesses, not structural capacity. Distances are scene coordinate units.'};assert out['eleven_original_positive_seats_retained'];(P/'saved_seats.json').write_text(json.dumps(out,indent=2));print('SAVED SEATS PASS',len(rows))
