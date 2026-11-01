"""Actual exported evaluated geometry mutations; no Blender/model writes."""
import json,traceback,copy,sys,hashlib,argparse
from pathlib import Path
from overlay_math import *
P=Path(__file__).resolve().parent
if sys.flags.optimize:raise RuntimeError('Assertions required')
ap=argparse.ArgumentParser();ap.add_argument('--geometry',required=True);ap.add_argument('--report',required=True);a=ap.parse_args();geometry_path=Path(a.geometry).resolve();report_path=Path(a.report).resolve()
if geometry_path==report_path or report_path.exists()or not report_path.parent.is_dir():raise RuntimeError('New distinct report required')
original=json.loads(geometry_path.read_text());checker=(P/'check_actual_overlay.py').read_text();rows=[]
for case in ['burial','floating','xy_escape','material','seam','hole','duplicate']:
 x=copy.deepcopy(original);v=x['patch']['vertices'];faces=x['patch']['faces'];maxface=max(faces,key=lambda f:area([v[i][:2]for i in f['vertices']]));idx=maxface['vertices'][0]
 if case=='burial':v[idx][2]-=.2
 elif case=='floating':v[idx][2]+=.2
 elif case=='material':maxface['material_index']=(maxface['material_index']+1)%3
 elif case=='seam':
  old=x['source_path']['vertices'][665];idx=next(i for i,p in enumerate(v)if p==old);v[idx][2]+=.002
 elif case=='hole':faces.remove(maxface)
 elif case=='duplicate':faces.append(dict(maxface,id=len(faces)))
 elif case=='xy_escape':
  idx=max(range(len(v)),key=lambda i:v[i][0]);v[idx][0]+=.001;p=v[idx][:2];found=False
  for tr in x['terrain']:
   t=tr['coords'];xy=[q[:2]for q in t]
   if signed(xy)<=0:continue
   if all(cross(sub(b,a),sub(p,a))>=-1e-10 for a,b in zip(xy,xy[1:]+xy[:1])):v[idx][2]=plane(t)(p)+.021;found=True;break
  assert found,'Fixture terrain unavailable'
 s=checker.replace("x=json.loads(geometry_path.read_text())","x=FIXTURE").replace("report_path.write_text", "report_path.with_name(report_path.stem+'_unexpected_pass.json').write_text")
 try:exec(compile(s,str(P/'check_actual_overlay.py')+'[geometry-negative]','exec'),{'__file__':str(P/'check_actual_overlay.py'),'FIXTURE':x})
 except AssertionError as e:
  tb=e.__traceback__
  while tb.tb_next:tb=tb.tb_next
  rows.append({'case':case,'rejected':True,'error':str(e),'actual_assertion':s.splitlines()[tb.tb_lineno-1],'traceback':traceback.format_exc()})
 else:raise RuntimeError('Negative accepted '+case)
report_path.write_text(json.dumps({'pass':True,'actual_export_sha256':hashlib.sha256(geometry_path.read_bytes()).hexdigest(),'input_sha256':original['input_sha256'],'scope':'Mutated actual evaluated mesh export only; identical independent full-face/domain/seam checker executed without model writes.','cases':rows},indent=2));print([(r['case'],r['error'])for r in rows])
