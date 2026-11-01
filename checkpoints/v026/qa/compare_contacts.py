import sys
if sys.flags.optimize:raise RuntimeError('Optimized Python unsupported')
import json,argparse,collections,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--before',required=True);p.add_argument('--after',required=True);p.add_argument('--report',required=True);a=p.parse_args();before=json.loads(Path(a.before).read_text());after=json.loads(Path(a.after).read_text());assert not Path(a.report).exists();target='V005 | main tower calibrated stone surface';removed=set(range(6))|set(range(14,20));mapping=[i for i in range(413)if i not in removed]
def summarize(rows,post):
 out=collections.defaultdict(float)
 for r in rows:
  index=r['neighbor_polygon']if post else r['source_polygon']
  if post and r['object']==target:index=mapping[index]
  key=(r['object'],index,tuple(round(x,9)for x in r['normal']),round(r['plane_offset'],7),r['same_facing'])
  out[key]+=r['area']
 return out
b=summarize(before['contacts'],False);c=summarize(after['results'][0]['contacts'],True);assert set(b)==set(c),(set(b)-set(c),set(c)-set(b));delta={str(k):c[k]-b[k]for k in b};assert max(map(abs,delta.values()),default=0)<1e-7,delta
Path(a.report).write_text(json.dumps({'pass':True,'before_model_sha256':before['source_sha256'],'after_model_sha256':after['model_sha256'],'before_sha256':hashlib.sha256(Path(a.before).read_bytes()).hexdigest(),'after_sha256':hashlib.sha256(Path(a.after).read_bytes()).hexdigest(),'contact_area_deltas':delta,'same_logical_source_polygon_plane_and_orientation':True,'source_face_remapping_explicit':{'7':13,'16':28},'scope':'Preserves two known source top coplanar contacts. No global disjointness/exposure claim; pairwise areas may double-count multiway contact.'},indent=2));print('CONTACT SET PRESERVED')
